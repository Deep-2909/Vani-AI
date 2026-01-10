export interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'doc' | 'txt' | 'xlsx';
  uploadedDate: string;
  size?: number;
  url?: string;
  vectorized?: boolean;
}

// Mock documents data
export function getMockDocuments(): Document[] {
  return [
    {
      id: 'doc-1',
      name: 'pensions_rules.pdf',
      type: 'pdf',
      uploadedDate: '1/9/2026',
      size: 2048,
      vectorized: true,
    },
    {
      id: 'doc-2',
      name: 'meter_rules_doc.pdf',
      type: 'pdf',
      uploadedDate: '1/9/2026',
      size: 1536,
      vectorized: true,
    },
    {
      id: 'doc-3',
      name: 'pensions_rules.pdf',
      type: 'pdf',
      uploadedDate: '1/9/2026',
      size: 2048,
      vectorized: true,
    },
    {
      id: 'doc-4',
      name: '4d653-government-schemes-in-news.pdf',
      type: 'pdf',
      uploadedDate: '1/9/2026',
      size: 3072,
      vectorized: true,
    },
  ];
}
