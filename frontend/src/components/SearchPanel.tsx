import React, { useState } from 'react';
import { Search, MapPin, Tag, SlidersHorizontal, Loader2, Globe2 } from 'lucide-react';

interface SearchPanelProps {
  onStartSearch: (params: {
    query: string;
    category?: string;
    location?: string;
    max_results?: number;
    enable_website_crawl?: boolean;
  }) => void;
  isLoading: boolean;
}

const EXAMPLE_SEARCHES = [
  { label: 'Salons in Coimbatore', query: 'List salons in Coimbatore', category: 'salons', location: 'Coimbatore' },
  { label: 'Hotels in Chennai', query: 'Hotels in Chennai', category: 'Hotels', location: 'Chennai' },
  { label: 'Software in Bangalore', query: 'Software companies in Bangalore', category: 'Software companies', location: 'Bangalore' },
  { label: 'Hospitals in Erode', query: 'Hospitals in Erode', category: 'Hospitals', location: 'Erode' },
];

export const SearchPanel: React.FC<SearchPanelProps> = ({ onStartSearch, isLoading }) => {
  const [query, setQuery] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [category, setCategory] = useState('');
  const [location, setLocation] = useState('');
  const [maxResults, setMaxResults] = useState(30);
  const [enableWebsiteCrawl, setEnableWebsiteCrawl] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() && (!category.trim() || !location.trim())) return;
    onStartSearch({
      query: query.trim() || `${category.trim()} in ${location.trim()}`,
      category: category.trim() || undefined,
      location: location.trim() || undefined,
      max_results: maxResults,
      enable_website_crawl: enableWebsiteCrawl,
    });
  };

  const handleChipClick = (item: typeof EXAMPLE_SEARCHES[0]) => {
    setQuery(item.query);
    setCategory(item.category);
    setLocation(item.location);
    onStartSearch({
      query: item.query,
      category: item.category,
      location: item.location,
      max_results: maxResults,
      enable_website_crawl: enableWebsiteCrawl,
    });
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-xl">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Main Search Bar */}
        <div className="relative flex items-center">
          <div className="absolute left-4 pointer-events-none text-slate-400">
            <Search className="w-5 h-5 text-indigo-400" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search e.g. 'List salons in Coimbatore' or 'Hotels in Chennai'..."
            className="w-full pl-12 pr-36 py-3.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-white placeholder-slate-400 text-base focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all shadow-inner"
          />
          <div className="absolute right-2 flex items-center space-x-2">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className={`p-2 rounded-lg border text-xs font-medium transition-all ${
                showAdvanced
                  ? 'bg-indigo-600/20 border-indigo-500/40 text-indigo-300'
                  : 'bg-slate-800/80 border-slate-700 text-slate-400 hover:text-slate-200'
              }`}
              title="Toggle separate Category/Location inputs"
            >
              <SlidersHorizontal className="w-4 h-4" />
            </button>
            <button
              type="submit"
              disabled={isLoading || (!query.trim() && (!category.trim() || !location.trim()))}
              className="flex items-center space-x-2 px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium text-sm transition-all shadow-md shadow-indigo-600/30 hover:shadow-indigo-600/50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Scraping...</span>
                </>
              ) : (
                <span>Start Scraping</span>
              )}
            </button>
          </div>
        </div>

        {/* Advanced Filters (Optional Breakdown) */}
        {showAdvanced && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-950/50 border border-slate-800/80 text-sm">
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-400 flex items-center space-x-1.5">
                <Tag className="w-3.5 h-3.5 text-indigo-400" />
                <span>Business Category</span>
              </label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g. Salons, Hotels, IT"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-400 flex items-center space-x-1.5">
                <MapPin className="w-3.5 h-3.5 text-rose-400" />
                <span>City / Location</span>
              </label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Coimbatore, Chennai"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700/80 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-400">Max Results: {maxResults}</label>
              <input
                type="range"
                min="10"
                max="50"
                step="5"
                value={maxResults}
                onChange={(e) => setMaxResults(Number(e.target.value))}
                className="w-full accent-indigo-500 cursor-pointer h-2 bg-slate-800 rounded-lg"
              />
            </div>

            <div className="flex items-center space-x-3 pt-4 md:pt-6">
              <input
                type="checkbox"
                id="deepCrawl"
                checked={enableWebsiteCrawl}
                onChange={(e) => setEnableWebsiteCrawl(e.target.checked)}
                className="w-4 h-4 rounded text-indigo-600 bg-slate-900 border-slate-700 focus:ring-indigo-500"
              />
              <label htmlFor="deepCrawl" className="text-xs text-slate-300 flex items-center space-x-1.5 cursor-pointer">
                <Globe2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Deep Website Crawl (Emails & Phones)</span>
              </label>
            </div>
          </div>
        )}

        {/* Quick Example Chips */}
        <div className="flex items-center flex-wrap gap-2 pt-1">
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
            Quick Examples:
          </span>
          {EXAMPLE_SEARCHES.map((item) => (
            <button
              key={item.label}
              type="button"
              disabled={isLoading}
              onClick={() => handleChipClick(item)}
              className="text-xs px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700/80 transition-colors duration-150 flex items-center space-x-1 disabled:opacity-50"
            >
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </form>
    </div>
  );
};
