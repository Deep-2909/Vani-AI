import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
  PhoneIncoming,
  PhoneOutgoing,
  Play,
  ArrowUpDown,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Voicemail,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { generateMockCalls, Call } from "@/lib/api";
import { cn } from "@/lib/utils";

type SortField = "timestamp" | "duration" | "outcome";
type SortDirection = "asc" | "desc";

const outcomeIcons = {
  resolved: { icon: CheckCircle, className: "text-success" },
  escalated: { icon: AlertTriangle, className: "text-warning" },
  dropped: { icon: XCircle, className: "text-destructive" },
  voicemail: { icon: Voicemail, className: "text-muted-foreground" },
};

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

interface CallLogsTableProps {
  limit?: number;
  showHeader?: boolean;
}

export function CallLogsTable({ limit, showHeader = true }: CallLogsTableProps) {
  const [sortField, setSortField] = useState<SortField>("timestamp");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const calls = useMemo(() => generateMockCalls(limit || 10), [limit]);

  const sortedCalls = useMemo(() => {
    return [...calls].sort((a, b) => {
      let comparison = 0;
      switch (sortField) {
        case "timestamp":
          comparison = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
          break;
        case "duration":
          comparison = a.duration - b.duration;
          break;
        case "outcome":
          comparison = a.outcome.localeCompare(b.outcome);
          break;
      }
      return sortDirection === "asc" ? comparison : -comparison;
    });
  }, [calls, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="glass-card-elevated overflow-hidden"
    >
      {showHeader && (
        <div className="p-6 border-b border-border">
          <h3 className="font-semibold text-foreground">Recent Calls</h3>
          <p className="text-sm text-muted-foreground">
            Click on any call to view details and recording
          </p>
        </div>
      )}

      <Table>
        <TableHeader>
          <TableRow className="border-border hover:bg-transparent">
            <TableHead className="text-muted-foreground">Caller ID</TableHead>
            <TableHead className="text-muted-foreground">Type</TableHead>
            <TableHead className="text-muted-foreground">
              <Button
                variant="ghost"
                size="sm"
                className="gap-1 -ml-3 text-muted-foreground hover:text-foreground"
                onClick={() => handleSort("duration")}
              >
                Duration
                <ArrowUpDown className="w-3 h-3" />
              </Button>
            </TableHead>
            <TableHead className="text-muted-foreground">
              <Button
                variant="ghost"
                size="sm"
                className="gap-1 -ml-3 text-muted-foreground hover:text-foreground"
                onClick={() => handleSort("outcome")}
              >
                Outcome
                <ArrowUpDown className="w-3 h-3" />
              </Button>
            </TableHead>
            <TableHead className="text-muted-foreground">
              <Button
                variant="ghost"
                size="sm"
                className="gap-1 -ml-3 text-muted-foreground hover:text-foreground"
                onClick={() => handleSort("timestamp")}
              >
                Time
                <ArrowUpDown className="w-3 h-3" />
              </Button>
            </TableHead>
            <TableHead className="text-right text-muted-foreground">Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedCalls.map((call, index) => {
            const OutcomeIcon = outcomeIcons[call.outcome].icon;
            return (
              <motion.tr
                key={call.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="border-border hover:bg-muted/30 cursor-pointer transition-colors"
              >
                <TableCell className="font-mono text-sm text-foreground">
                  {call.callerId}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    {call.type === "inbound" ? (
                      <PhoneIncoming className="w-4 h-4 text-success" />
                    ) : (
                      <PhoneOutgoing className="w-4 h-4 text-primary" />
                    )}
                    <span className="capitalize text-sm text-foreground">
                      {call.type}
                    </span>
                  </div>
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {formatDuration(call.duration)}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <OutcomeIcon
                      className={cn("w-4 h-4", outcomeIcons[call.outcome].className)}
                    />
                    <span className="capitalize text-sm text-foreground">
                      {call.outcome}
                    </span>
                  </div>
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {formatDate(call.timestamp)}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    size="sm"
                    variant="ghost"
                    className="gap-1 text-primary hover:text-primary hover:bg-primary/10"
                  >
                    <Play className="w-3 h-3" />
                    Play
                  </Button>
                </TableCell>
              </motion.tr>
            );
          })}
        </TableBody>
      </Table>
    </motion.div>
  );
}
