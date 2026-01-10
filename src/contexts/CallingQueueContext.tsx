import React, { createContext, useContext, useState, useEffect } from "react";

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
}

const CallingQueueContext = createContext<CallingQueueContextType | undefined>(undefined);

const STORAGE_KEY = "calling_queue_entries";

export const CallingQueueProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [entries, setEntries] = useState<CallingQueueEntry[]>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        return parsed.map((entry: any) => ({
          ...entry,
          addedAt: new Date(entry.addedAt),
        }));
      } catch {
        return [];
      }
    }
    return [];
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
  }, [entries]);

  const addEntry = (entry: Omit<CallingQueueEntry, "id" | "addedAt">) => {
    const newEntry: CallingQueueEntry = {
      ...entry,
      id: crypto.randomUUID(),
      addedAt: new Date(),
    };
    setEntries((prev) => [...prev, newEntry]);
  };

  const removeEntry = (id: string) => {
    setEntries((prev) => prev.filter((entry) => entry.id !== id));
  };

  const updateEntry = (id: string, updates: Partial<CallingQueueEntry>) => {
    setEntries((prev) =>
      prev.map((entry) => (entry.id === id ? { ...entry, ...updates } : entry))
    );
  };

  const reorderEntries = (newOrder: CallingQueueEntry[]) => {
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
