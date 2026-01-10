export interface ComplaintRecord {
  id: string;
  date: string;
  nameOfPerson: string;
  descriptionOfComplain: string;
  department: string;
}

export interface DatabaseSource {
  id: string;
  name: string;
  type: 'table' | 'api' | 'csv';
  status: 'active' | 'inactive' | 'syncing';
  recordCount: number;
  lastSync: string;
  columns: string[];
  data?: ComplaintRecord[];
}

// Mock data for complaint tickets
export function generateMockComplaintData(): ComplaintRecord[] {
  return [
    {
      id: '1',
      date: '12 Jan',
      nameOfPerson: 'karan sharma',
      descriptionOfComplain: 'The syllabus is too old and there is a need to update the syllabus of 12 th standard',
      department: 'Education'
    },
    {
      id: '2',
      date: '3 Aug',
      nameOfPerson: 'ishan roy',
      descriptionOfComplain: 'There is issue in the pipeline as no water supply in my home from last 4 months , i live near delhi sector 32 rohini',
      department: 'Municipal'
    },
    {
      id: '3',
      date: '2024-04-27',
      nameOfPerson: 'User',
      descriptionOfComplain: 'The pattern of the board exams of class 12 was incorrect and I recommend to change.',
      department: 'go ed'
    },
    {
      id: '4',
      date: '2023-10-05',
      nameOfPerson: 'Karan',
      descriptionOfComplain: 'Shortage of water supply in Rohini sector 32',
      department: 'Municipal'
    },
    {
      id: '5',
      date: '2024-04-27',
      nameOfPerson: 'Kartik',
      descriptionOfComplain: 'There is a lot of garbage near my society in Mumbai and no action has been taken.',
      department: 'Ministry'
    },
    {
      id: '6',
      date: '2024-04-27',
      nameOfPerson: 'Ali Yusu',
      descriptionOfComplain: 'Professor Mehra is not a good person and traps people into the wrong side of conversations.',
      department: 'IIT Ma'
    },
  ];
}

// Mock database sources
export function getMockDatabaseSources(): DatabaseSource[] {
  return [
    {
      id: 'db-1',
      name: 'COMPLAIN TICKET DATA',
      type: 'table',
      status: 'active',
      recordCount: 6,
      lastSync: new Date().toISOString(),
      columns: ['DATE', 'NAME OF PERSON', 'DESCRIPTION OF COMPLAIN', 'DEPARTMENT'],
      data: generateMockComplaintData()
    }
  ];
}
