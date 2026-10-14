import React, { useState } from 'react';
import type { PaginatedLeads } from '../types';
import { 
  Phone, Mail, Globe, MapPin, ExternalLink, ArrowUpDown, 
  Search, ShieldCheck, ChevronLeft, ChevronRight, FileSpreadsheet, Download
} from 'lucide-react';
import { api } from '../services/api';

interface LeadsTableProps {
  jobId: string;
  data: PaginatedLeads | null;
  isLoading: boolean;
  onPageChange: (newPage: number) => void;
  onFilterChange: (filters: {
    search?: string;
    has_phone?: boolean;
    has_email?: boolean;
    has_website?: boolean;
    sort_by?: string;
    sort_order?: string;
  }) => void;
}

export const LeadsTable: React.FC<LeadsTableProps> = ({
  jobId,
  data,
  isLoading,
  onPageChange,
  onFilterChange,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPhone, setFilterPhone] = useState<boolean | undefined>(undefined);
  const [filterEmail, setFilterEmail] = useState<boolean | undefined>(undefined);
  const [filterWebsite, setFilterWebsite] = useState<boolean | undefined>(undefined);
  const [sortBy, setSortBy] = useState('confidence_score');
  const [sortOrder, setSortOrder] = useState('desc');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFilterChange({
      search: searchTerm,
      has_phone: filterPhone,
      has_email: filterEmail,
      has_website: filterWebsite,
      sort_by: sortBy,
      sort_order: sortOrder,
    });
  };

  const handleSort = (field: string) => {
    const nextOrder = sortBy === field && sortOrder === 'desc' ? 'asc' : 'desc';
    setSortBy(field);
    setSortOrder(nextOrder);
    onFilterChange({
      search: searchTerm,
      has_phone: filterPhone,
      has_email: filterEmail,
      has_website: filterWebsite,
      sort_by: field,
      sort_order: nextOrder,
    });
  };

  const toggleFilter = (type: 'phone' | 'email' | 'website') => {
    let nextPhone = filterPhone;
    let nextEmail = filterEmail;
    let nextWebsite = filterWebsite;

    if (type === 'phone') nextPhone = filterPhone === true ? undefined : true;
    if (type === 'email') nextEmail = filterEmail === true ? undefined : true;
    if (type === 'website') nextWebsite = filterWebsite === true ? undefined : true;

    setFilterPhone(nextPhone);
    setFilterEmail(nextEmail);
    setFilterWebsite(nextWebsite);

    onFilterChange({
      search: searchTerm,
      has_phone: nextPhone,
      has_email: nextEmail,
      has_website: nextWebsite,
      sort_by: sortBy,
      sort_order: sortOrder,
    });
  };

  const getConfidenceBadge = (score: number) => {
    const percent = Math.round(score * 100);
    let colorClass = 'bg-slate-800 text-slate-400 border-slate-700';
    if (percent >= 75) colorClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    else if (percent >= 50) colorClass = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
    else if (percent >= 25) colorClass = 'bg-amber-500/10 text-amber-400 border-amber-500/20';

    return (
      <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${colorClass}`}>
        <ShieldCheck className="w-3 h-3" />
        <span>{percent}%</span>
      </span>
    );
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-xl backdrop-blur-xl overflow-hidden">
      {/* Table Toolbar */}
      <div className="p-4 sm:p-5 border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter leads by name, phone, address, email..."
            className="w-full pl-10 pr-20 py-2 bg-slate-950/80 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-all"
          />
          <button
            type="submit"
            className="absolute right-1.5 top-1.5 px-2.5 py-1 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
          >
            Filter
          </button>
        </form>

        {/* Filter Chips & Export Actions */}
        <div className="flex items-center flex-wrap gap-2">
          {/* Quick Filters */}
          <button
            onClick={() => toggleFilter('phone')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
              filterPhone
                ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                : 'bg-slate-800/80 border-slate-700/60 text-slate-400 hover:text-slate-200'
            }`}
          >
            <Phone className="w-3.5 h-3.5" />
            <span>Has Phone</span>
          </button>

          <button
            onClick={() => toggleFilter('email')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
              filterEmail
                ? 'bg-sky-500/20 border-sky-500/40 text-sky-300'
                : 'bg-slate-800/80 border-slate-700/60 text-slate-400 hover:text-slate-200'
            }`}
          >
            <Mail className="w-3.5 h-3.5" />
            <span>Has Email</span>
          </button>

          <button
            onClick={() => toggleFilter('website')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
              filterWebsite
                ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                : 'bg-slate-800/80 border-slate-700/60 text-slate-400 hover:text-slate-200'
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            <span>Has Website</span>
          </button>

          {/* Export Buttons */}
          <div className="h-4 w-[1px] bg-slate-800 mx-1 hidden sm:block" />

          <a
            href={api.getExportUrl(jobId, 'xlsx')}
            download
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 transition-all shadow-sm"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
            <span>Excel (.xlsx)</span>
          </a>

          <a
            href={api.getExportUrl(jobId, 'csv')}
            download
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all shadow-sm"
          >
            <Download className="w-3.5 h-3.5 text-slate-400" />
            <span>CSV</span>
          </a>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 uppercase tracking-wider font-semibold">
              <th className="py-3 px-4">
                <button
                  onClick={() => handleSort('business_name')}
                  className="flex items-center space-x-1 hover:text-white"
                >
                  <span>Business Name</span>
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </th>
              <th className="py-3 px-4">
                <button
                  onClick={() => handleSort('city')}
                  className="flex items-center space-x-1 hover:text-white"
                >
                  <span>Location</span>
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </th>
              <th className="py-3 px-4">Phone</th>
              <th className="py-3 px-4">Email</th>
              <th className="py-3 px-4">Website</th>
              <th className="py-3 px-4">Maps</th>
              <th className="py-3 px-4">
                <button
                  onClick={() => handleSort('confidence_score')}
                  className="flex items-center space-x-1 hover:text-white"
                >
                  <span>Quality</span>
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {isLoading ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-400">
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                    <span>Loading leads...</span>
                  </div>
                </td>
              </tr>
            ) : !data || data.items.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-400">
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <MapPin className="w-8 h-8 text-slate-600" />
                    <p className="font-medium text-slate-300">No leads found</p>
                    <p className="text-xs text-slate-500">
                      Try adjusting your search criteria or enabling deeper crawling.
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              data.items.map((lead) => (
                <tr key={lead.id} className="hover:bg-slate-800/40 transition-colors">
                  {/* Business Name */}
                  <td className="py-3 px-4">
                    <div className="space-y-0.5">
                      <div className="font-semibold text-white text-sm tracking-tight">
                        {lead.business_name}
                      </div>
                      <div className="flex items-center space-x-1.5">
                        {lead.category && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60">
                            {lead.category}
                          </span>
                        )}
                        <span className="text-[10px] text-slate-500">via {lead.source_name}</span>
                      </div>
                    </div>
                  </td>

                  {/* Location & Address */}
                  <td className="py-3 px-4 max-w-xs">
                    <div className="space-y-0.5 text-slate-300">
                      <div className="font-medium text-white flex items-center space-x-1">
                        <MapPin className="w-3 h-3 text-rose-400 flex-shrink-0" />
                        <span>{lead.city || 'N/A'}</span>
                        {lead.pincode && (
                          <span className="text-[10px] px-1 bg-slate-800 text-slate-400 rounded">
                            {lead.pincode}
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-400 truncate" title={lead.address || ''}>
                        {lead.address || 'Address not listed'}
                      </p>
                    </div>
                  </td>

                  {/* Phone */}
                  <td className="py-3 px-4">
                    {lead.phone ? (
                      <a
                        href={`tel:${lead.phone}`}
                        className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 font-mono text-[11px] transition-colors"
                      >
                        <Phone className="w-3 h-3" />
                        <span>{lead.phone}</span>
                      </a>
                    ) : (
                      <span className="text-slate-500 select-none">N/A</span>
                    )}
                  </td>

                  {/* Email */}
                  <td className="py-3 px-4">
                    {lead.email ? (
                      <a
                        href={`mailto:${lead.email}`}
                        className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/20 text-[11px] transition-colors"
                        title={lead.email}
                      >
                        <Mail className="w-3 h-3 flex-shrink-0" />
                        <span className="truncate max-w-[130px]">{lead.email}</span>
                      </a>
                    ) : (
                      <span className="text-slate-500 select-none">N/A</span>
                    )}
                  </td>

                  {/* Website */}
                  <td className="py-3 px-4">
                    {lead.website_url ? (
                      <a
                        href={lead.website_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center space-x-1 text-indigo-400 hover:text-indigo-300 transition-colors"
                        title={lead.website_url}
                      >
                        <Globe className="w-3.5 h-3.5" />
                        <span className="truncate max-w-[100px]">Visit</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <span className="text-slate-500 select-none">N/A</span>
                    )}
                  </td>

                  {/* Google Maps URL */}
                  <td className="py-3 px-4">
                    {lead.google_maps_url ? (
                      <a
                        href={lead.google_maps_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center space-x-1 px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-colors text-[11px]"
                      >
                        <MapPin className="w-3 h-3 text-rose-400" />
                        <span>Map</span>
                      </a>
                    ) : (
                      <span className="text-slate-500 select-none">N/A</span>
                    )}
                  </td>

                  {/* Quality / Confidence */}
                  <td className="py-3 px-4">
                    {getConfidenceBadge(lead.confidence_score)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {data && data.total > 0 && (
        <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing <span className="font-semibold text-white">{(data.page - 1) * data.page_size + 1}</span> to{' '}
            <span className="font-semibold text-white">
              {Math.min(data.page * data.page_size, data.total)}
            </span>{' '}
            of <span className="font-semibold text-white">{data.total}</span> leads
          </div>

          <div className="flex items-center space-x-2">
            <button
              disabled={data.page <= 1}
              onClick={() => onPageChange(data.page - 1)}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed border border-slate-700 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-2 font-medium text-slate-300">
              Page {data.page} of {data.pages}
            </span>
            <button
              disabled={data.page >= data.pages}
              onClick={() => onPageChange(data.page + 1)}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed border border-slate-700 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
