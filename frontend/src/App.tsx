import { useState, useEffect, useRef } from 'react';
import { Navbar } from './components/Navbar';
import { SearchPanel } from './components/SearchPanel';
import { ProgressCard } from './components/ProgressCard';
import { LeadsTable } from './components/LeadsTable';
import { SearchHistoryModal } from './components/SearchHistoryModal';
import type { SearchJob, PaginatedLeads, DashboardStats } from './types';
import { api } from './services/api';
import { Sparkles, Database, ShieldAlert } from 'lucide-react';

export default function App() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [jobs, setJobs] = useState<SearchJob[]>([]);
  const [activeJob, setActiveJob] = useState<SearchJob | null>(null);
  const [leadsData, setLeadsData] = useState<PaginatedLeads | null>(null);
  const [isLoadingLeads, setIsLoadingLeads] = useState<boolean>(false);
  const [isStartingSearch, setIsStartingSearch] = useState<boolean>(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState<boolean>(false);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  // Filter & pagination state
  const [tableFilters, setTableFilters] = useState<{
    search?: string;
    city?: string;
    has_phone?: boolean;
    has_email?: boolean;
    has_website?: boolean;
    sort_by?: string;
    sort_order?: string;
    page: number;
    page_size: number;
  }>({
    page: 1,
    page_size: 25,
    sort_by: 'confidence_score',
    sort_order: 'desc',
  });

  const pollIntervalRef = useRef<number | null>(null);

  // Initial load
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [statsData, jobsList] = await Promise.all([
        api.getStats().catch(() => null),
        api.getJobs().catch(() => []),
      ]);
      if (statsData) setStats(statsData);
      setJobs(jobsList);

      if (jobsList.length > 0 && !activeJob) {
        setActiveJob(jobsList[0]);
      }
    } catch (err) {
      console.error('Error loading initial data:', err);
    }
  };

  // Poll active job if in progress
  useEffect(() => {
    if (pollIntervalRef.current) {
      window.clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }

    if (!activeJob) return;

    const isRunning =
      activeJob.status === 'pending' ||
      activeJob.status === 'discovering' ||
      activeJob.status === 'crawling';

    if (isRunning) {
      pollIntervalRef.current = window.setInterval(async () => {
        try {
          const updated = await api.getJob(activeJob.id);
          setActiveJob(updated);

          // If job finished, refresh stats, jobs list, and load leads
          if (updated.status === 'completed' || updated.status === 'failed') {
            window.clearInterval(pollIntervalRef.current!);
            pollIntervalRef.current = null;
            setIsStartingSearch(false);
            api.getStats().then(setStats).catch(() => {});
            api.getJobs().then(setJobs).catch(() => {});
            loadLeadsForJob(updated.id, tableFilters);
          }
        } catch (e) {
          console.error('Polling error:', e);
        }
      }, 2000);
    } else {
      // Job is completed/failed; load its leads
      loadLeadsForJob(activeJob.id, tableFilters);
    }

    return () => {
      if (pollIntervalRef.current) {
        window.clearInterval(pollIntervalRef.current);
      }
    };
  }, [activeJob?.id, activeJob?.status]);

  const loadLeadsForJob = async (jobId: string, filters = tableFilters) => {
    setIsLoadingLeads(true);
    try {
      const data = await api.getJobLeads(jobId, filters);
      setLeadsData(data);
    } catch (err: any) {
      console.error('Failed to load leads:', err);
    } finally {
      setIsLoadingLeads(false);
    }
  };

  const handleStartSearch = async (params: {
    query: string;
    category?: string;
    location?: string;
    max_results?: number;
    enable_website_crawl?: boolean;
  }) => {
    setErrorBanner(null);
    setIsStartingSearch(true);
    try {
      const job = await api.startSearch(params);
      setActiveJob(job);
      setJobs((prev) => [job, ...prev]);
      setLeadsData(null); // Clear previous table leads
      setTableFilters((prev) => ({ ...prev, page: 1, search: undefined }));
    } catch (err: any) {
      setErrorBanner(err.message || 'Failed to trigger search job');
      setIsStartingSearch(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    const updated = { ...tableFilters, page: newPage };
    setTableFilters(updated);
    if (activeJob) {
      loadLeadsForJob(activeJob.id, updated);
    }
  };

  const handleFilterChange = (filters: any) => {
    const updated = { ...tableFilters, ...filters, page: 1 };
    setTableFilters(updated);
    if (activeJob) {
      loadLeadsForJob(activeJob.id, updated);
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    try {
      await api.deleteJob(jobId);
      setJobs((prev) => prev.filter((j) => j.id !== jobId));
      if (activeJob?.id === jobId) {
        const remaining = jobs.filter((j) => j.id !== jobId);
        setActiveJob(remaining[0] || null);
        setLeadsData(null);
      }
      api.getStats().then(setStats).catch(() => {});
    } catch (err: any) {
      alert(`Could not delete search: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans">
      {/* Navigation */}
      <Navbar stats={stats} onOpenHistory={() => setIsHistoryOpen(true)} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Error notification banner if any */}
        {errorBanner && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-5 h-5 text-rose-400" />
              <span>{errorBanner}</span>
            </div>
            <button
              onClick={() => setErrorBanner(null)}
              className="text-xs font-semibold text-rose-400 hover:text-white"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Hero & Search Panel */}
        <section className="space-y-4">
          <div className="space-y-1">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
              <span>Find & Extract Verified Business Leads</span>
              <Sparkles className="w-6 h-6 text-indigo-400" />
            </h1>
            <p className="text-slate-400 text-sm max-w-2xl">
              Type any query like <span className="text-indigo-300">"List salons in Coimbatore"</span> or{' '}
              <span className="text-indigo-300">"Hotels in Chennai"</span>. We discover real public listings,
              crawl websites for direct emails & phones, and generate ready-to-use Excel sheets.
            </p>
          </div>

          <SearchPanel onStartSearch={handleStartSearch} isLoading={isStartingSearch} />
        </section>

        {/* Live Progress Card */}
        {activeJob && (
          <section>
            <ProgressCard job={activeJob} />
          </section>
        )}

        {/* Results Leads Table */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Database className="w-4 h-4 text-indigo-400" />
              <h2 className="text-lg font-bold text-white tracking-tight">Extracted Business Leads</h2>
              {leadsData && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {leadsData.total} total
                </span>
              )}
            </div>
          </div>

          {activeJob ? (
            <LeadsTable
              jobId={activeJob.id}
              data={leadsData}
              isLoading={isLoadingLeads}
              onPageChange={handlePageChange}
              onFilterChange={handleFilterChange}
            />
          ) : (
            <div className="p-12 text-center rounded-2xl bg-slate-900/60 border border-slate-800/80 text-slate-400 space-y-3">
              <Database className="w-10 h-10 text-slate-600 mx-auto" />
              <h3 className="text-base font-semibold text-slate-300">No Active Search Selected</h3>
              <p className="text-xs text-slate-500 max-w-md mx-auto">
                Use the search bar above or click one of the quick examples to start scraping real business leads.
              </p>
            </div>
          )}
        </section>
      </main>

      {/* Search History Modal */}
      <SearchHistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        jobs={jobs}
        onSelectJob={(job) => {
          setActiveJob(job);
          setTableFilters((prev) => ({ ...prev, page: 1 }));
        }}
        onDeleteJob={handleDeleteJob}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        <p>LeadHunt • Built with Python FastAPI, Playwright, BeautifulSoup, React & PostgreSQL.</p>
      </footer>
    </div>
  );
}
