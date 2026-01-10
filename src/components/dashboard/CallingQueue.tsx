import { useState } from "react";
import { Phone, Plus, X } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useCallingQueue } from "@/contexts/CallingQueueContext";
import { cn } from "@/lib/utils";

export const CallingQueue = () => {
  const { entries, addEntry, removeEntry } = useCallingQueue();
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newEntry, setNewEntry] = useState({ name: "", phone: "", description: "" });

  const handleAddEntry = () => {
    if (newEntry.name && newEntry.phone) {
      addEntry(newEntry);
      setNewEntry({ name: "", phone: "", description: "" });
      setIsAddDialogOpen(false);
    }
  };

  return (
    <>
      <Card className="glass-card border-accent/20">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <Phone className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Calling Queue</h3>
                <p className="text-sm text-muted-foreground">
                  {entries.length} {entries.length === 1 ? "entry" : "entries"} in queue
                </p>
              </div>
            </div>
            <Button onClick={() => setIsAddDialogOpen(true)} size="sm" className="gap-2">
              <Plus className="w-4 h-4" />
              Add Number
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {entries.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Phone className="w-12 h-12 mx-auto mb-3 opacity-20" />
              <p className="text-sm">No entries in queue</p>
              <p className="text-xs mt-1">Add numbers to start calling</p>
            </div>
          ) : (
            entries.slice(0, 3).map((entry, index) => (
              <div
                key={entry.id}
                className={cn(
                  "p-4 rounded-lg border transition-all",
                  index === 0
                    ? "bg-primary/5 border-primary/30"
                    : "bg-card/50 border-border/50"
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-foreground truncate">{entry.name}</h4>
                      {index === 0 && (
                        <Badge className="bg-primary text-primary-foreground text-xs px-2">
                          NEXT CALL
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-1">{entry.phone}</p>
                    {entry.description && (
                      <p className="text-xs text-muted-foreground/80 italic line-clamp-1">
                        {entry.description}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">#{index + 1}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 text-muted-foreground hover:text-destructive"
                      onClick={() => removeEntry(entry.id)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))
          )}
          {entries.length > 3 && (
            <div className="text-center pt-2">
              <p className="text-xs text-muted-foreground">
                +{entries.length - 3} more in queue
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add to Calling Queue</DialogTitle>
            <DialogDescription>
              Add a new entry to the calling queue. This will be added to the end of the queue.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">
                Name
              </label>
              <Input
                placeholder="Enter name"
                value={newEntry.name}
                onChange={(e) => setNewEntry({ ...newEntry, name: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">
                Phone Number
              </label>
              <Input
                placeholder="+91 98765 43210"
                value={newEntry.phone}
                onChange={(e) => setNewEntry({ ...newEntry, phone: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">
                Description (optional)
              </label>
              <Textarea
                placeholder="Reason for call or notes..."
                value={newEntry.description}
                onChange={(e) => setNewEntry({ ...newEntry, description: e.target.value })}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddEntry} disabled={!newEntry.name || !newEntry.phone}>
              Add to Queue
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};
