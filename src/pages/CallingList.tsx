import { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Plus, Trash2, Edit2, GripVertical, Upload, Info } from "lucide-react";
import { useCallingQueue } from "@/contexts/CallingQueueContext";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { CallingQueueEntry } from "@/contexts/CallingQueueContext";

interface SortableItemProps {
  entry: CallingQueueEntry;
  index: number;
  onEdit: (entry: CallingQueueEntry) => void;
  onDelete: (id: string) => void;
}

const SortableItem = ({ entry, index, onEdit, onDelete }: SortableItemProps) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: entry.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="bg-card rounded-lg border border-border/50 p-4 hover:border-accent/50 transition-colors"
    >
      <div className="flex items-start gap-3">
        <button
          className="mt-1 cursor-grab active:cursor-grabbing text-muted-foreground hover:text-foreground transition-colors"
          {...attributes}
          {...listeners}
        >
          <GripVertical className="w-5 h-5" />
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs text-muted-foreground">#{index + 1}</span>
                <h4 className="font-medium text-foreground">{entry.name}</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-1">{entry.phone}</p>
              {entry.description && (
                <p className="text-xs text-muted-foreground/80 italic">{entry.description}</p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground"
                onClick={() => onEdit(entry)}
              >
                <Edit2 className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0 text-muted-foreground hover:text-destructive"
                onClick={() => onDelete(entry.id)}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const CallingList = () => {
  const { entries, addEntry, updateEntry, removeEntry, reorderEntries } = useCallingQueue();
  const [newEntry, setNewEntry] = useState({ name: "", phone: "", description: "" });
  const [editingEntry, setEditingEntry] = useState<CallingQueueEntry | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = entries.findIndex((entry) => entry.id === active.id);
      const newIndex = entries.findIndex((entry) => entry.id === over.id);
      const newOrder = arrayMove(entries, oldIndex, newIndex);
      reorderEntries(newOrder);
    }
  };

  const handleAddEntry = () => {
    if (newEntry.name && newEntry.phone) {
      addEntry(newEntry);
      setNewEntry({ name: "", phone: "", description: "" });
    }
  };

  const handleEdit = (entry: CallingQueueEntry) => {
    setEditingEntry(entry);
    setIsEditDialogOpen(true);
  };

  const handleUpdateEntry = () => {
    if (editingEntry) {
      updateEntry(editingEntry.id, {
        name: editingEntry.name,
        phone: editingEntry.phone,
        description: editingEntry.description,
      });
      setIsEditDialogOpen(false);
      setEditingEntry(null);
    }
  };

  const handleCSVUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      const lines = text.split("\n").filter((line) => line.trim());

      // Skip header row if present
      const startIndex = lines[0].toLowerCase().includes("name") ? 1 : 0;

      for (let i = startIndex; i < lines.length; i++) {
        const [name, phone, description = ""] = lines[i].split(",").map((s) => s.trim());
        if (name && phone) {
          addEntry({ name, phone, description });
        }
      }
    };
    reader.readAsText(file);
    e.target.value = ""; // Reset input
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-foreground">Calling List</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Manage and prioritize phone numbers for AI calling
            </p>
          </div>
          <div className="relative">
            <input
              type="file"
              accept=".csv"
              onChange={handleCSVUpload}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              id="csv-upload"
            />
            <Button variant="outline" className="gap-2" asChild>
              <label htmlFor="csv-upload" className="cursor-pointer">
                <Upload className="w-4 h-4" />
                Add CSV
              </label>
            </Button>
          </div>
        </div>

        {/* Add New Entry Form */}
        <Card className="p-6 glass-card border-accent/20">
          <div className="flex items-center gap-2 mb-4">
            <Plus className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-foreground">Add New Entry</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              placeholder="Name"
              value={newEntry.name}
              onChange={(e) => setNewEntry({ ...newEntry, name: e.target.value })}
            />
            <Input
              placeholder="+91 98765 43210"
              value={newEntry.phone}
              onChange={(e) => setNewEntry({ ...newEntry, phone: e.target.value })}
            />
            <Input
              placeholder="Description (optional)"
              value={newEntry.description}
              onChange={(e) => setNewEntry({ ...newEntry, description: e.target.value })}
            />
          </div>
          <Button
            onClick={handleAddEntry}
            disabled={!newEntry.name || !newEntry.phone}
            className="mt-4 w-full md:w-auto"
          >
            Add to List
          </Button>
        </Card>

        {/* Info Tip */}
        <div className="bg-primary/5 border border-primary/20 rounded-lg p-4 flex items-start gap-3">
          <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-foreground">
              <span className="font-medium">Tip:</span> Drag and drop entries to change call
              priority. The top entry will be called first.
            </p>
          </div>
        </div>

        {/* Calling List */}
        <div className="space-y-3">
          {entries.length === 0 ? (
            <Card className="p-12 text-center glass-card">
              <div className="text-muted-foreground">
                <Plus className="w-12 h-12 mx-auto mb-3 opacity-20" />
                <p className="text-sm">No entries in calling list</p>
                <p className="text-xs mt-1">Add entries above to get started</p>
              </div>
            </Card>
          ) : (
            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
              <SortableContext items={entries.map((e) => e.id)} strategy={verticalListSortingStrategy}>
                {entries.map((entry, index) => (
                  <SortableItem
                    key={entry.id}
                    entry={entry}
                    index={index}
                    onEdit={handleEdit}
                    onDelete={removeEntry}
                  />
                ))}
              </SortableContext>
            </DndContext>
          )}
        </div>
      </div>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Entry</DialogTitle>
            <DialogDescription>Update the details for this calling list entry.</DialogDescription>
          </DialogHeader>
          {editingEntry && (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">Name</label>
                <Input
                  value={editingEntry.name}
                  onChange={(e) =>
                    setEditingEntry({ ...editingEntry, name: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  Phone Number
                </label>
                <Input
                  value={editingEntry.phone}
                  onChange={(e) =>
                    setEditingEntry({ ...editingEntry, phone: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  Description
                </label>
                <Textarea
                  value={editingEntry.description}
                  onChange={(e) =>
                    setEditingEntry({ ...editingEntry, description: e.target.value })
                  }
                  rows={3}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsEditDialogOpen(false);
                setEditingEntry(null);
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleUpdateEntry}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
};

export default CallingList;
