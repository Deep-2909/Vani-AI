import React, { createContext, useContext, useState, useEffect } from "react";
import { getCallingQueue, addToCallingQueue, removeFromCallingQueue } from "@/lib/api";

export interface CallingQueueEntry {
  id: string;
  name: string;
  phone: string;
  description: string;
  addedAt: Date;
}

interface CallingQueueContextType {
  entries: CallingQueueEntry[];
  addEntry: (entry: Omit<CallingQueueEntry, "id" | "addedAt">) => void;
  removeEntry: (id: string) => void;
  updateEntry: (id: string, entry: Partial<CallingQueueEntry>) => void;
  reorderEntries: (newOrder: CallingQueueEntry[]) => void;
  clearCompleted: () => void;
  isLoading: boolean;
  refreshEntries: () => void;
}

const CallingQueueContext = createContext<CallingQueueContextType | undefined>(undefined);

export const CallingQueueProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [entries, setEntries] = useState<CallingQueueEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchEntries = async () => {
    setIsLoading(true);
    const response = await getCallingQueue();
    if (response.data) {
      const mapped = response.data.map((entry: any) => ({
        ...entry,
        addedAt: new Date(entry.addedAt),
      }));
      setEntries(mapped);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    fetchEntries();
  }, []);

  const addEntry = async (entry: Omit<CallingQueueEntry, "id" | "addedAt">) => {
    const response = await addToCallingQueue(entry);
    if (response.data) {
      await fetchEntries(); // Refresh from backend
    }
  };

  const removeEntry = async (id: string) => {
    const response = await removeFromCallingQueue(id);
    if (response.data?.success) {
      setEntries((prev) => prev.filter((entry) => entry.id !== id));
    }
  };

  const updateEntry = (id: string, updates: Partial<CallingQueueEntry>) => {
    // TODO: Implement backend update endpoint if needed
    setEntries((prev) =>
      prev.map((entry) => (entry.id === id ? { ...entry, ...updates } : entry))
    );
  };

  const reorderEntries = (newOrder: CallingQueueEntry[]) => {
    // Local reorder for UI - could sync to backend later
    setEntries(newOrder);
  };

  const clearCompleted = () => {
    setEntries([]);
  };

  return (
    <CallingQueueContext.Provider
      value={{
        entries,
        addEntry,
        removeEntry,
        updateEntry,
        reorderEntries,
        clearCompleted,
        isLoading,
        refreshEntries: fetchEntries,
      }}
    >
      {children}
    </CallingQueueContext.Provider>
  );
};

export const useCallingQueue = () => {
  const context = useContext(CallingQueueContext);
  if (!context) {
    throw new Error("useCallingQueue must be used within CallingQueueProvider");
  }
  return context;
};
