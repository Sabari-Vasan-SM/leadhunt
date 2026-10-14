import asyncio
from datetime import datetime
import logging
from typing import List, Dict, Any
from sqlalchemy import select, update
from app.core.database import async_session_maker
from app.models.job import SearchJob
from app.models.lead import Lead
from app.core.config import settings
from app.services.query_parser import parse_natural_language_query
from app.services.discovery.osm import OSMDiscoveryProvider
from app.services.discovery.web_search import WebSearchDiscoveryProvider
from app.services.discovery.google_places import GooglePlacesDiscoveryProvider
from app.services.crawler.contact_extractor import ContactExtractor
from app.services.pipeline.validator import DataValidator
from app.services.pipeline.deduplicator import DataDeduplicator

logger = logging.getLogger(__name__)

class ScrapingManager:
    def __init__(self):
        self.osm_provider = OSMDiscoveryProvider()
        self.web_provider = WebSearchDiscoveryProvider()
        self.google_provider = GooglePlacesDiscoveryProvider()
        self.extractor = ContactExtractor()
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENCY)

    async def _log_job(self, job_id: str, message: str, level: str = "info"):
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {"time": timestamp, "level": level, "message": message}
        async with async_session_maker() as session:
            job = await session.get(SearchJob, job_id)
            if job:
                current_logs = list(job.logs or [])
                current_logs.append(log_entry)
                job.logs = current_logs
                await session.commit()

    async def _update_job_stage(self, job_id: str, status: str, stage: str, discovered: int = None, processed: int = None):
        async with async_session_maker() as session:
            job = await session.get(SearchJob, job_id)
            if job:
                job.status = status
                job.current_stage = stage
                if discovered is not None:
                    job.total_discovered = discovered
                if processed is not None:
                    job.total_processed = processed
                await session.commit()

    async def run_pipeline(self, job_id: str, max_results: int = 40, enable_website_crawl: bool = True):
        """
        Executes the full end-to-end async scraping pipeline.
        """
        try:
            async with async_session_maker() as session:
                job = await session.get(SearchJob, job_id)
                if not job:
                    return
                query = job.query
                category = job.category
                location = job.location

            if not category or not location:
                parsed_cat, parsed_loc = parse_natural_language_query(query)
                category = category or parsed_cat
                location = location or parsed_loc
                async with async_session_maker() as session:
                    job = await session.get(SearchJob, job_id)
                    if job:
                        job.category = category
                        job.location = location
                        await session.commit()

            await self._log_job(job_id, f"Parsed query '{query}' -> Category: '{category}', Location: '{location}'")
            await self._update_job_stage(job_id, "discovering", f"Searching public directories in {location}")

            # 1. Search Discovery Providers concurrently
            discovered_items: List[Dict[str, Any]] = []

            # Primary: OpenStreetMap Overpass (Real physical businesses)
            try:
                osm_results = await self.osm_provider.search(category, location, limit=max_results)
                await self._log_job(job_id, f"Discovered {len(osm_results)} listings from OpenStreetMap Overpass API")
                discovered_items.extend(osm_results)
            except Exception as e:
                await self._log_job(job_id, f"OSM provider error: {e}", level="warning")

            # Secondary: Web Search for business websites
            try:
                web_results = await self.web_provider.search(category, location, limit=20)
                await self._log_job(job_id, f"Discovered {len(web_results)} web search directory listings")
                discovered_items.extend(web_results)
            except Exception as e:
                await self._log_job(job_id, f"WebSearch provider error: {e}", level="warning")

            # Tertiary: Google Places API if configured
            if settings.GOOGLE_PLACES_API_KEY:
                try:
                    google_results = await self.google_provider.search(category, location, limit=20)
                    await self._log_job(job_id, f"Discovered {len(google_results)} listings from Google Places API")
                    discovered_items.extend(google_results)
                except Exception as e:
                    await self._log_job(job_id, f"Google Places provider error: {e}", level="warning")

            total_discovered = len(discovered_items)
            await self._update_job_stage(job_id, "discovering", f"Discovered {total_discovered} raw listings", discovered=total_discovered)

            # 2. Concurrently crawl websites for contact details
            enriched_items: List[Dict[str, Any]] = []
            processed_count = 0

            if enable_website_crawl and total_discovered > 0:
                await self._update_job_stage(job_id, "crawling", "Enriching contacts from business websites...")

                async def enrich_item(item: Dict[str, Any]):
                    nonlocal processed_count
                    website = item.get("website_url")
                    # If item has a website and is missing either phone or email, crawl website
                    if website and (not item.get("phone") or not item.get("email")):
                        async with self.semaphore:
                            try:
                                scraped = await self.extractor.extract_from_website(website)
                                if scraped.get("phone") and not item.get("phone"):
                                    item["phone"] = scraped["phone"]
                                if scraped.get("email") and not item.get("email"):
                                    item["email"] = scraped["email"]
                                if scraped.get("pincode") and not item.get("pincode"):
                                    item["pincode"] = scraped["pincode"]
                                if scraped.get("google_maps_url") and not item.get("google_maps_url"):
                                    item["google_maps_url"] = scraped["google_maps_url"]
                            except Exception as ex:
                                logger.debug(f"Error enriching {website}: {ex}")

                    # Validate and score
                    validated = DataValidator.validate_and_score(item)
                    processed_count += 1
                    
                    # Update progress every 5 items
                    if processed_count % 5 == 0 or processed_count == total_discovered:
                        await self._update_job_stage(
                            job_id, 
                            "crawling", 
                            f"Enriched {processed_count}/{total_discovered} leads", 
                            processed=processed_count
                        )
                    return validated

                # Run bounded concurrency enrichment
                tasks = [enrich_item(it) for it in discovered_items]
                enriched_items = await asyncio.gather(*tasks)
            else:
                for it in discovered_items:
                    enriched_items.append(DataValidator.validate_and_score(it))
                processed_count = total_discovered

            # 3. Deduplication
            await self._update_job_stage(job_id, "crawling", "Deduplicating and quality filtering...", processed=processed_count)
            deduped_items = DataDeduplicator.deduplicate(enriched_items)
            await self._log_job(job_id, f"Deduplication complete: {len(deduped_items)} unique leads remaining from {total_discovered} raw records")

            # 4. Save to Database
            async with async_session_maker() as session:
                for d in deduped_items:
                    lead = Lead(
                        job_id=job_id,
                        business_name=d.get("business_name") or "Unknown Business",
                        category=d.get("category"),
                        address=d.get("address"),
                        city=d.get("city"),
                        pincode=d.get("pincode"),
                        phone=d.get("phone"),
                        email=d.get("email"),
                        website_url=d.get("website_url"),
                        google_maps_url=d.get("google_maps_url"),
                        source_url=d.get("source_url"),
                        source_name=d.get("source_name", "OpenStreetMap"),
                        confidence_score=d.get("confidence_score", 1.0),
                        raw_metadata=d.get("raw_metadata", {})
                    )
                    session.add(lead)

                job = await session.get(SearchJob, job_id)
                if job:
                    job.status = "completed"
                    job.current_stage = "Completed"
                    job.total_discovered = total_discovered
                    job.total_processed = len(deduped_items)
                await session.commit()

            await self._log_job(job_id, f"Pipeline completed successfully. {len(deduped_items)} leads saved.")

        except Exception as e:
            logger.exception(f"Pipeline error for job {job_id}: {e}")
            await self._log_job(job_id, f"Pipeline error: {str(e)}", level="error")
            async with async_session_maker() as session:
                job = await session.get(SearchJob, job_id)
                if job:
                    job.status = "failed"
                    job.current_stage = "Failed"
                    job.error_message = str(e)
                    await session.commit()
