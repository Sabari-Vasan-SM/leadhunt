import React from 'react';
import { Compass, Database, Phone, Mail, Sparkles } from 'lucide-react';
import type { DashboardStats } from '../types';

interface NavbarProps {
  stats: DashboardStats | null;
  onOpenHistory: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ stats, onOpenHistory }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Compass className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-white font-sans">
                Lead<span className="text-indigo-400">Hunt</span>
              </span>
              <span className="px-2 py-0.5 text-xs font-semibold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full">
                Scraper Engine
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Public Business Intelligence & Contact Extraction
            </p>
          </div>
        </div>

        {/* Live Counters */}
        <div className="hidden md:flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300">
            <Database className="w-3.5 h-3.5 text-indigo-400" />
            <span className="font-semibold text-white">{stats?.total_leads || 0}</span>
            <span className="text-slate-400">Leads</span>
          </div>
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300">
            <Phone className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-semibold text-white">{stats?.leads_with_phone || 0}</span>
            <span className="text-slate-400">Phones</span>
          </div>
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300">
            <Mail className="w-3.5 h-3.5 text-sky-400" />
            <span className="font-semibold text-white">{stats?.leads_with_email || 0}</span>
            <span className="text-slate-400">Emails</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenHistory}
            className="flex items-center space-x-2 px-3.5 py-1.5 text-sm font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700/80 border border-slate-700 rounded-lg transition-all duration-150 shadow-sm"
          >
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span>Search History</span>
          </button>
        </div>
      </div>
    </header>
  );
};
