/**
 * API Client for FastAPI Backend
 * Base URL should be configured via environment variable
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data: T | null;
  error: string | null;
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    return { 
      data: null, 
      error: error instanceof Error ? error.message : 'Unknown error occurred' 
    };
  }
}

// Types
export interface Call {
  id: string;
  callerId: string;
  type: 'inbound' | 'outbound';
  duration: number; // in seconds
  outcome: 'resolved' | 'escalated' | 'dropped' | 'voicemail';
  timestamp: string;
  transcript?: string;
  summary?: string;
  sentiment?: number; // 0-100
  recordingUrl?: string;
}

export interface Analytics {
  totalCalls: number;
  avgResolutionTime: number; // in seconds
  successRate: number; // percentage
  costSaved: number; // in dollars
  callsToday: number;
  activeNow: number;
}

export interface UploadResponse {
  success: boolean;
  fileId: string;
  fileName: string;
  vectorCount: number;
}

export interface SyncStatus {
  status: 'syncing' | 'synced' | 'error' | 'idle';
  lastSync: string;
  documentsCount: number;
  vectorsCount: number;
}

// API Endpoints

/**
 * GET /calls - Fetch all call logs
 */
export async function getCalls(params?: {
  limit?: number;
  offset?: number;
  type?: 'inbound' | 'outbound';
  outcome?: string;
}): Promise<ApiResponse<Call[]>> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
  if (params?.type) searchParams.set('type', params.type);
  if (params?.outcome) searchParams.set('outcome', params.outcome);

  const query = searchParams.toString();
  return apiRequest<Call[]>(`/calls${query ? `?${query}` : ''}`);
}

/**
 * GET /calls/:id - Fetch single call details
 */
export async function getCall(id: string): Promise<ApiResponse<Call>> {
  return apiRequest<Call>(`/calls/${id}`);
}

/**
 * GET /analytics - Fetch dashboard analytics
 */
export async function getAnalytics(): Promise<ApiResponse<Analytics>> {
  return apiRequest<Analytics>('/analytics');
}

/**
 * POST /upload-docs - Upload documents to knowledge base
 */
export async function uploadDocuments(files: File[]): Promise<ApiResponse<UploadResponse[]>> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  try {
    const response = await fetch(`${API_BASE_URL}/upload-docs`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    return { 
      data: null, 
      error: error instanceof Error ? error.message : 'Unknown error occurred' 
    };
  }
}

/**
 * GET /knowledge-base/sync-status - Get Pinecone sync status
 */
export async function getSyncStatus(): Promise<ApiResponse<SyncStatus>> {
  return apiRequest<SyncStatus>('/knowledge-base/sync-status');
}

/**
 * POST /knowledge-base/sync - Trigger sync to Pinecone
 */
export async function triggerSync(): Promise<ApiResponse<{ success: boolean }>> {
  return apiRequest<{ success: boolean }>('/knowledge-base/sync', {
    method: 'POST',
  });
}

// Mock data generators for development
export function generateMockCalls(count: number): Call[] {
  const outcomes: Call['outcome'][] = ['resolved', 'escalated', 'dropped', 'voicemail'];
  const types: Call['type'][] = ['inbound', 'outbound'];
  const summaries = [
    'Customer inquired about water supply issues in their area. Provided information about scheduled maintenance and expected restoration time. Issue marked as resolved.',
    'Complaint about road maintenance and potholes. Customer expressed concerns about safety. Escalated to relevant department for immediate action.',
    'Query regarding government schemes eligibility. Explained application process and required documents. Customer satisfied with the information provided.',
    'Report of streetlight malfunction in residential area. Logged complaint and provided ticket number. Expected resolution within 48 hours.',
    'Request for property tax payment details. Guided customer through online payment portal and answered questions about payment methods.',
    'Feedback about recent civic improvements. Customer appreciated the work done. Forwarded positive feedback to concerned department.',
    'Emergency report of water pipeline burst. Immediately dispatched repair team. Kept customer informed about repair progress.',
    'Inquiry about building permit application status. Checked system and provided current status. Explained next steps in the approval process.',
  ];

  return Array.from({ length: count }, (_, i) => ({
    id: `call-${i + 1}`,
    callerId: `+1${Math.floor(Math.random() * 9000000000 + 1000000000)}`,
    type: types[Math.floor(Math.random() * types.length)],
    duration: Math.floor(Math.random() * 600) + 30,
    outcome: outcomes[Math.floor(Math.random() * outcomes.length)],
    timestamp: new Date(Date.now() - Math.random() * 86400000 * 7).toISOString(),
    summary: summaries[Math.floor(Math.random() * summaries.length)],
    sentiment: Math.floor(Math.random() * 100),
    recordingUrl: `https://storage.example.com/recordings/call-${i + 1}.mp3`,
  }));
}

export function generateMockAnalytics(): Analytics {
  return {
    totalCalls: Math.floor(Math.random() * 5000) + 10000,
    avgResolutionTime: Math.floor(Math.random() * 120) + 60,
    successRate: Math.floor(Math.random() * 15) + 85,
    costSaved: Math.floor(Math.random() * 50000) + 100000,
    callsToday: Math.floor(Math.random() * 200) + 50,
    activeNow: Math.floor(Math.random() * 10) + 1,
  };
}
