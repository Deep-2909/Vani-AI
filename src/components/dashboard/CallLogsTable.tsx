import { useState, useMemo, useEffect } from "react";
import { motion } from "framer-motion";
import {
  PhoneIncoming,
  PhoneOutgoing,
  FileText,
  ArrowUpDown,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Voicemail,
  MessageSquare,
  Loader2,
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { getCalls, fetchTranscript, Call } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

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
  const [selectedCall, setSelectedCall] = useState<Call | null>(null);
  const [isSummaryDialogOpen, setIsSummaryDialogOpen] = useState(false);
  const [calls, setCalls] = useState<Call[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [transcript, setTranscript] = useState<string | null>(null);
  const [isLoadingTranscript, setIsLoadingTranscript] = useState(false);

  useEffect(() => {
    const fetchCalls = async () => {
      setIsLoading(true);
      const response = await getCalls({ limit: limit || 20 });
      if (response.data) {
        setCalls(response.data);
      }
      setIsLoading(false);
    };
    fetchCalls();
  }, [limit]);

  const handleViewSummary = async (call: Call) => {
    setSelectedCall(call);
    setIsSummaryDialogOpen(true);
    setTranscript(call.transcript || null);
  };

  const handleFetchTranscript = async (callId: string) => {
    setIsLoadingTranscript(true);
    console.log('Fetching transcript for call:', callId);

    const response = await fetchTranscript(callId);
    console.log('Transcript response:', response);

    if (response.data) {
      setTranscript(response.data.transcript);
      console.log('Transcript loaded successfully');
    } else if (response.error) {
      console.error('Failed to fetch transcript:', response.error);
      setTranscript(`Error: ${response.error}`);
    }
    setIsLoadingTranscript(false);
  };

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
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center py-8">
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  <span className="text-muted-foreground">Loading calls...</span>
                </div>
              </TableCell>
            </TableRow>
          ) : calls.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                No calls found
              </TableCell>
            </TableRow>
          ) : (
            sortedCalls.map((call, index) => {
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
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewSummary(call);
                    }}
                  >
                    <FileText className="w-3 h-3" />
                    Summary
                  </Button>
                </TableCell>
              </motion.tr>
            );
          })
          )}
        </TableBody>
      </Table>

      <Dialog open={isSummaryDialogOpen} onOpenChange={setIsSummaryDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Call Summary</DialogTitle>
            <DialogDescription>
              Detailed summary of the conversation
            </DialogDescription>
          </DialogHeader>
          {selectedCall && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 p-4 rounded-lg bg-muted/30">
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
                    Caller ID
                  </p>
                  <p className="font-mono text-sm text-foreground">{selectedCall.callerId}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
                    Call Type
                  </p>
                  <div className="flex items-center gap-2">
                    {selectedCall.type === "inbound" ? (
                      <PhoneIncoming className="w-4 h-4 text-success" />
                    ) : (
                      <PhoneOutgoing className="w-4 h-4 text-primary" />
                    )}
                    <span className="capitalize text-sm text-foreground">
                      {selectedCall.type}
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
                    Duration
                  </p>
                  <p className="text-sm text-foreground">{formatDuration(selectedCall.duration)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
                    Outcome
                  </p>
                  <div className="flex items-center gap-2">
                    {(() => {
                      const OutcomeIcon = outcomeIcons[selectedCall.outcome].icon;
                      return (
                        <>
                          <OutcomeIcon
                            className={cn("w-4 h-4", outcomeIcons[selectedCall.outcome].className)}
                          />
                          <span className="capitalize text-sm text-foreground">
                            {selectedCall.outcome}
                          </span>
                        </>
                      );
                    })()}
                  </div>
                </div>
                <div className="col-span-2">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
                    Time
                  </p>
                  <p className="text-sm text-foreground">{formatDate(selectedCall.timestamp)}</p>
                </div>
              </div>

              <Tabs defaultValue="summary" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="summary">Summary</TabsTrigger>
                  <TabsTrigger value="transcript">Transcript</TabsTrigger>
                </TabsList>

                <TabsContent value="summary" className="mt-4">
                  <div>
                    <h4 className="font-medium text-foreground mb-2 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-primary" />
                      Summary
                    </h4>
                    <div className="p-4 rounded-lg bg-muted/30 border border-border">
                      <p className="text-sm text-foreground leading-relaxed">
                        {selectedCall.summary || "No summary available for this call."}
                      </p>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="transcript" className="mt-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-foreground flex items-center gap-2">
                        <MessageSquare className="w-4 h-4 text-primary" />
                        Transcript
                      </h4>
                      {!transcript && selectedCall.id && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleFetchTranscript(selectedCall.id)}
                          disabled={isLoadingTranscript}
                        >
                          {isLoadingTranscript ? (
                            <>
                              <Loader2 className="w-3 h-3 mr-2 animate-spin" />
                              Loading...
                            </>
                          ) : (
                            "Fetch Transcript"
                          )}
                        </Button>
                      )}
                    </div>
                    <div className="p-4 rounded-lg bg-muted/30 border border-border max-h-96 overflow-y-auto">
                      {transcript ? (
                        <div className="space-y-3 text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                          {transcript}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">
                          No transcript available. Click "Fetch Transcript" to load from Retell.
                        </p>
                      )}
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
