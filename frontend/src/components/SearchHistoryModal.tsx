import React from 'react';
import type { SearchJob } from '../types';
import { X, Clock, FileSpreadsheet, Trash2, ArrowRight, CheckCircle2, AlertCircle, Layers } from 'lucide-react';
import { api } from '../services/api';

interface SearchHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  jobs: SearchJob[];
  onSelectJob: (job: SearchJob) => void;
  onDeleteJob: (jobId: string) => void;
}

export const SearchHistoryModal: React.FC<SearchHistoryModalProps> = ({
  isOpen,
  onClose,
  jobs,
  onSelectJob,
  onDeleteJob,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <Clock className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-semibold text-white">Search & Scraping History</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Job List */}
        <div className="p-4 overflow-y-auto divide-y divide-slate-800/80 space-y-2">
          {jobs.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-sm">
              No previous searches found. Run your first lead search above!
            </div>
          ) : (
            jobs.map((job) => (
              <div
                key={job.id}
                className="pt-3 pb-3 first:pt-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-800/30 p-2 rounded-xl transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-white text-sm">{job.query}</span>
                    {job.status === 'completed' ? (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>Completed</span>
                      </span>
                    ) : job.status === 'failed' ? (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        <AlertCircle className="w-3 h-3" />
                        <span>Failed</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        <Layers className="w-3 h-3 animate-pulse" />
                        <span>Active</span>
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-400 flex items-center space-x-3">
                    <span>{new Date(job.created_at).toLocaleString()}</span>
                    <span>•</span>
                    <span className="text-indigo-300 font-medium">{job.total_processed} leads saved</span>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      onSelectJob(job);
                      onClose();
                    }}
                    className="flex items-center space-x-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 transition-all"
                  >
                    <span>View Leads</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>

                  <a
                    href={api.getExportUrl(job.id, 'xlsx')}
                    download
                    title="Export as Excel"
                    className="p-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 transition-all"
                  >
                    <FileSpreadsheet className="w-4 h-4" />
                  </a>

                  <button
                    onClick={() => onDeleteJob(job.id)}
                    title="Delete record"
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 border border-slate-700 transition-all"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
