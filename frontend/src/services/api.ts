import type { SearchJob, PaginatedLeads, DashboardStats } from '../types';

const API_BASE = '/api/v1';

export const api = {
  async startSearch(params: {
    query: string;
    category?: string;
    location?: string;
    max_results?: number;
    enable_website_crawl?: boolean;
  }): Promise<SearchJob> {
    const res = await fetch(`${API_BASE}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to start search');
    }
    return res.json();
  },

  async getJobs(): Promise<SearchJob[]> {
    const res = await fetch(`${API_BASE}/jobs`);
    if (!res.ok) throw new Error('Failed to fetch jobs');
    return res.json();
  },

  async getJob(id: string): Promise<SearchJob> {
    const res = await fetch(`${API_BASE}/jobs/${id}`);
    if (!res.ok) throw new Error('Failed to fetch job details');
    return res.json();
  },

  async deleteJob(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/jobs/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete job');
  },

  async getJobLeads(
    jobId: string,
    params: {
      search?: string;
      city?: string;
      has_phone?: boolean;
      has_email?: boolean;
      has_website?: boolean;
      sort_by?: string;
      sort_order?: string;
      page?: number;
      page_size?: number;
    } = {}
  ): Promise<PaginatedLeads> {
    const searchParams = new URLSearchParams();
    if (params.search) searchParams.set('search', params.search);
    if (params.city) searchParams.set('city', params.city);
    if (params.has_phone !== undefined) searchParams.set('has_phone', String(params.has_phone));
    if (params.has_email !== undefined) searchParams.set('has_email', String(params.has_email));
    if (params.has_website !== undefined) searchParams.set('has_website', String(params.has_website));
    if (params.sort_by) searchParams.set('sort_by', params.sort_by);
    if (params.sort_order) searchParams.set('sort_order', params.sort_order);
    if (params.page) searchParams.set('page', String(params.page));
    if (params.page_size) searchParams.set('page_size', String(params.page_size));

    const res = await fetch(`${API_BASE}/jobs/${jobId}/leads?${searchParams.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch job leads');
    return res.json();
  },

  async getStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  },

  getExportUrl(jobId: string, format: 'xlsx' | 'csv'): string {
    return `${API_BASE}/export/jobs/${jobId}?format=${format}`;
  }
};
