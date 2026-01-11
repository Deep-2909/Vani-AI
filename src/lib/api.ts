/**
 * UPDATED API Client - Now connects to REAL backend endpoints
 * Replaces all mock data with actual API calls
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

    const result = await response.json();
    return { data: result.data || result, error: null };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}

// ===================================================================
// TYPES
// ===================================================================

export interface Call {
  id: string;
  callerId: string;
  type: 'inbound' | 'outbound';
  duration: number;
  outcome: 'resolved' | 'escalated' | 'dropped' | 'voicemail';
  timestamp: string;
  transcript?: string;
  summary?: string;
  sentiment?: number;
  recordingUrl?: string;
  ticketId?: string;
}

export interface Analytics {
  totalCalls: number;
  avgResolutionTime: number;
  successRate: number;
  costSaved: number;
  callsToday: number;
  activeNow: number;
}

export interface ComplaintAnalytics {
  topLocations: Array<{
    location: string;
    complaints: number;
    trend: 'up' | 'down' | 'stable';
    percentage: number;
  }>;
  topIssues: Array<{
    issue: string;
    complaints: number;
    trend: 'up' | 'down' | 'stable';
    percentage: number;
    severity: 'high' | 'medium' | 'low';
  }>;
  summary: {
    total: number;
    resolved: number;
    pending: number;
  };
}

export interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'doc' | 'txt' | 'xlsx';
  uploadedDate: string;
  size?: number;
  url?: string;
  vectorized?: boolean;
}

export interface DatabaseSource {
  id: string;
  name: string;
  type: 'table' | 'api' | 'csv';
  status: 'active' | 'inactive' | 'syncing';
  recordCount: number;
  lastSync: string;
  columns: string[];
  data?: any[];
}

export interface CallingQueueEntry {
  id: string;
  name: string;
  phone: string;
  description: string;
  addedAt: string;
}

export interface AgentConfiguration {
  agentName: string;
  agentDescription: string;
  category: string;
  department: string;
  accountType: string;
  tools: {
    knowledgeQuery: boolean;
    endCall: boolean;
    complainTicket: boolean;
  };
}

// ===================================================================
// CALL LOGS API
// ===================================================================

export async function getCalls(params?: {
  limit?: number;
  offset?: number;
  type?: 'inbound' | 'outbound';
  outcome?: string;
  search?: string;
}): Promise<ApiResponse<Call[]>> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
  if (params?.type) searchParams.set('call_type', params.type);
  if (params?.outcome) searchParams.set('outcome', params.outcome);
  if (params?.search) searchParams.set('search', params.search);

  const query = searchParams.toString();
  return apiRequest<Call[]>(`/api/calls${query ? `?${query}` : ''}`);
}

export async function getCall(id: string): Promise<ApiResponse<Call>> {
  return apiRequest<Call>(`/api/calls/${id}`);
}

export async function exportCallLogs(): Promise<ApiResponse<{ data: string; filename: string }>> {
  return apiRequest<{ data: string; filename: string }>('/api/calls/export');
}

export async function fetchTranscript(callId: string): Promise<ApiResponse<{ transcript: string; cached: boolean }>> {
  return apiRequest<{ transcript: string; cached: boolean }>(`/api/calls/${callId}/fetch-transcript`, {
    method: 'POST'
  });
}

// ===================================================================
// ANALYTICS API
// ===================================================================

export async function getAnalytics(): Promise<ApiResponse<Analytics>> {
  return apiRequest<Analytics>('/api/analytics');
}

export async function getComplaintAnalytics(): Promise<ApiResponse<ComplaintAnalytics>> {
  return apiRequest<ComplaintAnalytics>('/api/analytics/complaints');
}

// ===================================================================
// KNOWLEDGE BASE API
// ===================================================================

export async function uploadDocuments(files: File[]): Promise<ApiResponse<Document[]>> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  try {
    const response = await fetch(`${API_BASE_URL}/api/knowledge-base/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return { data: result.data, error: null };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}

export async function getDocuments(search?: string): Promise<ApiResponse<Document[]>> {
  const query = search ? `?search=${encodeURIComponent(search)}` : '';
  return apiRequest<Document[]>(`/api/knowledge-base/documents${query}`);
}

// ===================================================================
// DATABASE API
// ===================================================================

export async function getDatabaseSources(): Promise<ApiResponse<DatabaseSource[]>> {
  return apiRequest<DatabaseSource[]>('/api/databases/sources');
}

export async function syncDatabaseSource(
  datasetName: string,
  sourceType: string,
  connectionString?: string
): Promise<ApiResponse<{ sourceId: string; message: string }>> {
  return apiRequest<{ sourceId: string; message: string }>('/api/databases/sync', {
    method: 'POST',
    body: JSON.stringify({ dataset_name: datasetName, source_type: sourceType, connection_string: connectionString }),
  });
}

// ===================================================================
// CALLING QUEUE API
// ===================================================================

export async function getCallingQueue(): Promise<ApiResponse<CallingQueueEntry[]>> {
  return apiRequest<CallingQueueEntry[]>('/api/calling-queue');
}

export async function addToCallingQueue(entry: {
  name: string;
  phone: string;
  description?: string;
}): Promise<ApiResponse<CallingQueueEntry>> {
  return apiRequest<CallingQueueEntry>('/api/calling-queue', {
    method: 'POST',
    body: JSON.stringify(entry),
  });
}

export async function removeFromCallingQueue(entryId: string): Promise<ApiResponse<{ success: boolean }>> {
  return apiRequest<{ success: boolean }>(`/api/calling-queue/${entryId}`, {
    method: 'DELETE',
  });
}

// ===================================================================
// AGENT CONFIGURATION API
// ===================================================================

export async function getAgentConfig(): Promise<ApiResponse<AgentConfiguration>> {
  return apiRequest<AgentConfiguration>('/api/agent/config');
}

export async function updateAgentConfig(config: Partial<AgentConfiguration>): Promise<ApiResponse<AgentConfiguration>> {
  return apiRequest<AgentConfiguration>('/api/agent/config', {
    method: 'POST',
    body: JSON.stringify(config),
  });
}

// ===================================================================
// CALLING CONTROL API
// ===================================================================

export async function startInboundAgent(): Promise<ApiResponse<{ status: string; message: string }>> {
  return apiRequest<{ status: string; message: string }>('/api/calls/start-inbound', {
    method: 'POST',
  });
}

export async function startOutboundCalling(): Promise<ApiResponse<{ callId: string; phoneNumber: string; message: string }>> {
  return apiRequest<{ callId: string; phoneNumber: string; message: string }>('/api/calls/start-outbound', {
    method: 'POST',
  });
}

// ===================================================================
// MANAGER API (Government Officials Dashboard)
// ===================================================================

export interface ManagerStats {
  total_open_complaints: number;
  total_resolved_complaints: number;
  by_priority: Record<string, number>;
  top_departments: Record<string, number>;
  active_hotspots: number;
  avg_resolution_hours: number;
}

export interface Complaint {
  ticket_id: string;
  citizen_name: string;
  contact?: string;
  description: string;
  location?: string;
  area?: string;
  department: string;
  category: string;
  priority: string;
  status: string;
  created_at: string;
}

export interface AreaHotspot {
  area_name: string;
  total_complaints: number;
  open_complaints: number;
  resolved_complaints: number;
  is_hotspot: boolean;
  hotspot_level: string;
  last_complaint_at?: string;
  breakdown: {
    water: number;
    road: number;
    electricity: number;
  };
  priority_breakdown: {
    critical: number;
    high: number;
  };
}

export interface OutboundCall {
  call_id: string;
  phone_number: string;
  call_type: string;
  status: string;
  initiated_at: string;
  completed_at?: string;
  answered: boolean;
  language: string;
}

export async function getManagerStats(): Promise<ApiResponse<ManagerStats>> {
  return apiRequest<ManagerStats>('/manager/dashboard-stats');
}

export async function getComplaints(params?: {
  limit?: number;
  offset?: number;
  department?: string;
  priority?: string;
  status?: string;
}): Promise<ApiResponse<{ complaints: Complaint[]; count: number; total: number }>> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.append('limit', params.limit.toString());
  if (params?.offset) searchParams.append('offset', params.offset.toString());
  if (params?.department) searchParams.append('department', params.department);
  if (params?.priority) searchParams.append('priority', params.priority);
  if (params?.status) searchParams.append('status', params.status);

  return apiRequest<{ complaints: Complaint[]; count: number; total: number }>(
    `/api/complaints?${searchParams.toString()}`
  );
}

export async function resolveComplaint(data: {
  ticket_id: string;
  resolved_by: string;
  resolution_notes: string;
  citizen_rating?: number;
}): Promise<ApiResponse<{ success: boolean; message: string; resolution_time_hours: number }>> {
  return apiRequest<{ success: boolean; message: string; resolution_time_hours: number }>(
    '/manager/resolve-complaint',
    {
      method: 'POST',
      body: JSON.stringify(data),
    }
  );
}

export async function getResolvedComplaints(
  limit: number = 50,
  offset: number = 0
): Promise<ApiResponse<{ complaints: any[]; count: number }>> {
  return apiRequest<{ complaints: any[]; count: number }>(
    `/manager/resolved-complaints?limit=${limit}&offset=${offset}`
  );
}

export async function getAreaHotspots(
  flaggedOnly: boolean = false,
  minComplaints: number = 5
): Promise<ApiResponse<{ hotspots: AreaHotspot[]; count: number }>> {
  return apiRequest<{ hotspots: AreaHotspot[]; count: number }>(
    `/manager/area-hotspots?flagged_only=${flaggedOnly}&min_complaints=${minComplaints}`
  );
}

export async function getAreaDetails(areaName: string): Promise<ApiResponse<any>> {
  return apiRequest<any>(`/manager/area-details/${encodeURIComponent(areaName)}`);
}

export async function initiateOutboundCalls(data: {
  phone_numbers: string[];
  call_type: string;
  message_content: string;
  language?: string;
  scheme_name?: string;
  alert_type?: string;
}): Promise<ApiResponse<{ success: boolean; message: string; call_ids: string[] }>> {
  return apiRequest<{ success: boolean; message: string; call_ids: string[] }>(
    '/manager/initiate-outbound-calls',
    {
      method: 'POST',
      body: JSON.stringify(data),
    }
  );
}

export async function getOutboundCallsStatus(
  callType?: string,
  status?: string,
  limit: number = 50
): Promise<ApiResponse<{ calls: OutboundCall[]; count: number }>> {
  const params = new URLSearchParams();
  if (callType) params.append('call_type', callType);
  if (status) params.append('status', status);
  params.append('limit', limit.toString());

  return apiRequest<{ calls: OutboundCall[]; count: number }>(
    `/manager/outbound-calls/status?${params.toString()}`
  );
}

export async function notifyScheme(data: {
  scheme_code: string;
  target_areas?: string[];
  language?: string;
}): Promise<ApiResponse<{ success: boolean; scheme_name: string; notifications_sent: number; call_ids: string[] }>> {
  return apiRequest<{ success: boolean; scheme_name: string; notifications_sent: number; call_ids: string[] }>(
    '/manager/notify-scheme',
    {
      method: 'POST',
      body: JSON.stringify(data),
    }
  );
}

// ===================================================================
// WEBSOCKET CONNECTION
// ===================================================================

export function connectToActiveCalls(onUpdate: (calls: any[]) => void): WebSocket {
  const ws = new WebSocket(`ws://localhost:8000/ws/active-calls`);

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.event === 'ACTIVE_CALLS_UPDATE') {
      onUpdate(message.data);
    }
  };

  return ws;
}

// ===================================================================
// BACKWARD COMPATIBILITY - Keep mock generators for development
// ===================================================================

export function generateMockCalls(count: number): Call[] {
  // Kept for offline development - won't be used when API is available
  const outcomes: Call['outcome'][] = ['resolved', 'escalated', 'dropped', 'voicemail'];
  const types: Call['type'][] = ['inbound', 'outbound'];
  const summaries = [
    'Customer inquired about water supply issues in their area.',
    'Complaint about road maintenance and potholes.',
    'Query regarding government schemes eligibility.',
  ];

  return Array.from({ length: count }, (_, i) => ({
    id: `call-${i + 1}`,
    callerId: `+91${Math.floor(Math.random() * 9000000000 + 1000000000)}`,
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
