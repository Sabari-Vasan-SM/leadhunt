export interface SearchJob {
  id: string;
  query: string;
  category?: string;
  location?: string;
  status: 'pending' | 'discovering' | 'crawling' | 'completed' | 'failed';
  current_stage?: string;
  total_discovered: number;
  total_processed: number;
  error_message?: string;
  logs?: Array<{ time: string; level: string; message: string }>;
  created_at: string;
  updated_at: string;
}

export interface Lead {
  id: string;
  job_id: string;
  business_name: string;
  category?: string;
  address?: string;
  city?: string;
  pincode?: string;
  phone?: string;
  email?: string;
  website_url?: string;
  google_maps_url?: string;
  source_url?: string;
  source_name: string;
  confidence_score: number;
  created_at: string;
}

export interface PaginatedLeads {
  items: Lead[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface DashboardStats {
  total_jobs: number;
  completed_jobs: number;
  total_leads: number;
  leads_with_phone: number;
  leads_with_email: number;
  leads_with_website: number;
}
