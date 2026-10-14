import React, { useState } from 'react';
import type { SearchJob } from '../types';
import { CheckCircle2, Clock, AlertCircle, ChevronDown, ChevronUp, Terminal, Activity, Layers } from 'lucide-react';

interface ProgressCardProps {
  job: SearchJob | null;
}

export const ProgressCard: React.FC<ProgressCardProps> = ({ job }) => {
  const [showLogs, setShowLogs] = useState(false);

  if (!job) return null;

  const isCompleted = job.status === 'completed';
  const isFailed = job.status === 'failed';

  // Compute progress percentage
  let progressPercent = 0;
  if (isCompleted) {
    progressPercent = 100;
  } else if (job.status === 'pending') {
    progressPercent = 10;
  } else if (job.status === 'discovering') {
    progressPercent = Math.min(30 + (job.total_discovered > 0 ? 20 : 0), 45);
  } else if (job.status === 'crawling') {
    if (job.total_discovered > 0) {
      const crawlRatio = (job.total_processed / job.total_discovered);
      progressPercent = Math.round(50 + crawlRatio * 45);
    } else {
      progressPercent = 60;
    }
  }

  const getStatusBadge = () => {
    switch (job.status) {
      case 'completed':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Completed</span>
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Failed</span>
          </span>
        );
      case 'discovering':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Layers className="w-3.5 h-3.5 animate-pulse" />
            <span>Discovering Businesses</span>
          </span>
        );
      case 'crawling':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Activity className="w-3.5 h-3.5 animate-pulse" />
            <span>Crawling Websites</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20">
            <Clock className="w-3.5 h-3.5" />
            <span>Queued</span>
          </span>
        );
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg backdrop-blur-xl space-y-4">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <h3 className="text-base font-semibold text-white tracking-tight">
              {job.query}
            </h3>
            {getStatusBadge()}
          </div>
          <p className="text-xs text-slate-400 flex items-center space-x-2">
            <span>Stage:</span>
            <span className="text-indigo-300 font-medium">{job.current_stage || 'Processing'}</span>
          </p>
        </div>

        {/* Live Counters */}
        <div className="flex items-center space-x-4 text-xs">
          <div className="bg-slate-950/70 border border-slate-800 px-3 py-1.5 rounded-lg">
            <span className="text-slate-400">Discovered: </span>
            <span className="font-bold text-white ml-1">{job.total_discovered}</span>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 px-3 py-1.5 rounded-lg">
            <span className="text-slate-400">Processed: </span>
            <span className="font-bold text-emerald-400 ml-1">{job.total_processed}</span>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-slate-400">
          <span>Pipeline Progress</span>
          <span className="font-mono">{progressPercent}%</span>
        </div>
        <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              isFailed
                ? 'bg-rose-500'
                : isCompleted
                ? 'bg-emerald-500'
                : 'bg-gradient-to-r from-indigo-500 to-emerald-400 animate-pulse'
            }`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Error Banner */}
      {isFailed && job.error_message && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-xs text-rose-300 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0 text-rose-400" />
          <span>{job.error_message}</span>
        </div>
      )}

      {/* Scraping Log Toggle */}
      {job.logs && job.logs.length > 0 && (
        <div className="pt-2 border-t border-slate-800/80">
          <button
            onClick={() => setShowLogs(!showLogs)}
            className="flex items-center justify-between w-full text-xs text-slate-400 hover:text-slate-200 transition-colors"
          >
            <span className="flex items-center space-x-1.5 font-mono">
              <Terminal className="w-3.5 h-3.5 text-indigo-400" />
              <span>Scraper Execution Log ({job.logs.length} entries)</span>
            </span>
            {showLogs ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showLogs && (
            <div className="mt-3 p-3 bg-slate-950 rounded-xl border border-slate-800 font-mono text-xs max-h-48 overflow-y-auto space-y-1">
              {job.logs.map((l, idx) => (
                <div key={idx} className="flex items-start space-x-2 text-slate-300 leading-relaxed">
                  <span className="text-slate-500 select-none">[{l.time.split(' ')[1]}]</span>
                  <span
                    className={
                      l.level === 'error'
                        ? 'text-rose-400'
                        : l.level === 'warning'
                        ? 'text-amber-400'
                        : 'text-indigo-300'
                    }
                  >
                    {l.message}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
