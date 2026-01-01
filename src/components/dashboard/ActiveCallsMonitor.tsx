import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Phone, PhoneIncoming, PhoneOutgoing, Clock, Radio } from "lucide-react";
import { SentimentGauge } from "./SentimentGauge";
import { LiveTranscript } from "./LiveTranscript";
import { cn } from "@/lib/utils";

interface ActiveCall {
  id: string;
  callerId: string;
  type: "inbound" | "outbound";
  duration: number;
  sentiment: number;
  status: "active" | "on-hold" | "transferring";
}

const mockActiveCalls: ActiveCall[] = [
  { id: "1", callerId: "+1 (555) 123-4567", type: "inbound", duration: 245, sentiment: 72, status: "active" },
  { id: "2", callerId: "+1 (555) 987-6543", type: "outbound", duration: 128, sentiment: 45, status: "active" },
  { id: "3", callerId: "+1 (555) 456-7890", type: "inbound", duration: 67, sentiment: 88, status: "on-hold" },
];

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export function ActiveCallsMonitor() {
  const [selectedCall, setSelectedCall] = useState<ActiveCall>(mockActiveCalls[0]);
  const [sentiment, setSentiment] = useState(selectedCall.sentiment);

  // Simulate real-time sentiment updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSentiment((prev) => {
        const change = Math.random() * 10 - 5;
        return Math.min(100, Math.max(0, prev + change));
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="glass-card-elevated p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
            <Radio className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground">Live Call Monitor</h3>
            <p className="text-sm text-muted-foreground">
              {mockActiveCalls.length} active calls
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="status-dot status-dot-live" />
          <span className="text-sm text-success font-medium">Live</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Calls List */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">
            Active Calls
          </p>
          {mockActiveCalls.map((call) => (
            <motion.button
              key={call.id}
              onClick={() => setSelectedCall(call)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                "w-full p-4 rounded-xl border transition-all duration-200 text-left",
                selectedCall.id === call.id
                  ? "bg-primary/10 border-primary/30"
                  : "bg-muted/30 border-border hover:border-primary/20"
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {call.type === "inbound" ? (
                    <PhoneIncoming className="w-4 h-4 text-success" />
                  ) : (
                    <PhoneOutgoing className="w-4 h-4 text-primary" />
                  )}
                  <span className="font-mono text-sm text-foreground">
                    {call.callerId}
                  </span>
                </div>
                <span
                  className={cn(
                    "text-xs px-2 py-0.5 rounded-full",
                    call.status === "active"
                      ? "bg-success/20 text-success"
                      : call.status === "on-hold"
                      ? "bg-warning/20 text-warning"
                      : "bg-accent/20 text-accent"
                  )}
                >
                  {call.status}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="w-3 h-3" />
                <span>{formatDuration(call.duration)}</span>
              </div>
            </motion.button>
          ))}
        </div>

        {/* Transcript */}
        <div className="lg:col-span-1 bg-muted/20 rounded-xl border border-border">
          <div className="p-4 border-b border-border">
            <p className="text-sm font-medium text-foreground">Live Transcript</p>
            <p className="text-xs text-muted-foreground">{selectedCall.callerId}</p>
          </div>
          <LiveTranscript />
        </div>

        {/* Sentiment & Stats */}
        <div className="space-y-6">
          <div className="text-center">
            <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
              Sentiment Analysis
            </p>
            <div className="flex justify-center">
              <SentimentGauge value={Math.round(sentiment)} size="lg" />
            </div>
          </div>

          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-muted/30 border border-border">
              <p className="text-xs text-muted-foreground uppercase mb-1">
                Call Duration
              </p>
              <p className="text-xl font-bold font-mono text-foreground">
                {formatDuration(selectedCall.duration)}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-muted/30 border border-border">
              <p className="text-xs text-muted-foreground uppercase mb-1">
                Call Type
              </p>
              <p className="text-xl font-bold text-foreground capitalize">
                {selectedCall.type}
              </p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
