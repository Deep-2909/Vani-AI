import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Radio, CheckCircle, MapPin, FileText, MessageSquare } from "lucide-react";
import { SentimentGauge } from "./SentimentGauge";
import { LiveTranscript } from "./LiveTranscript";

interface ActionTaken {
  id: string;
  action: string;
  icon: React.ComponentType<{ className?: string }>;
  status: "completed" | "in-progress" | "pending";
  timestamp: string;
  details?: string;
}

const mockActionsTaken: ActionTaken[] = [
  {
    id: "1",
    action: "Caller Identity Verified",
    icon: CheckCircle,
    status: "completed",
    timestamp: "4 mins ago",
    details: "Name: Rajesh Kumar | Phone: +91-9876543210"
  },
  {
    id: "2",
    action: "Issue Classification",
    icon: FileText,
    status: "completed",
    timestamp: "3 mins ago",
    details: "Category: Water Supply | Urgency: HIGH"
  },
  {
    id: "3", 
    action: "Location Mapping",
    icon: MapPin,
    status: "completed",
    timestamp: "2 mins ago",
    details: "Sector 12, Dwarka | 15-20 houses affected"
  },
  {
    id: "4",
    action: "Complaint Registered", 
    icon: CheckCircle,
    status: "completed",
    timestamp: "1 min ago",
    details: "Ticket ID: DEL-964A76 | Status: ACTIVE"
  },
  {
    id: "5",
    action: "Emergency Response",
    icon: MessageSquare,
    status: "completed",
    timestamp: "30 secs ago",
    details: "Water tanker dispatched | SMS sent to caller"
  }
];

interface ActiveCall {
  id: string;
  callerId: string;
  type: "inbound" | "outbound";
  duration: number;
  sentiment: number;
  status: "active" | "on-hold" | "transferring";
}

const mockActiveCalls: ActiveCall[] = [
  { id: "1", callerId: "+91-9876543210", type: "inbound", duration: 285, sentiment: 78, status: "active" },
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
  const [sentiment, setSentiment] = useState(78); // Static sentiment for demo

  // Static sentiment - no random updates for demo
  useEffect(() => {
    setSentiment(78); // Final sentiment: Satisfied after complaint resolution
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
              Real-time call monitoring
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="status-dot status-dot-live" />
          <span className="text-sm text-success font-medium">Live</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Transcript */}
        <div className="bg-muted/20 rounded-xl border border-border">
          <div className="p-4 border-b border-border">
            <p className="text-sm font-medium text-foreground">Live Transcript</p>
            <p className="text-xs text-muted-foreground">{selectedCall.callerId}</p>
          </div>
          <LiveTranscript />
        </div>

        {/* Action Taken Panel */}
        <div className="bg-muted/20 rounded-xl border border-border">
          <div className="p-4 border-b border-border">
            <p className="text-sm font-medium text-foreground">Actions Taken</p>
            <p className="text-xs text-muted-foreground">AI automated responses</p>
          </div>
          <div className="p-4 space-y-3 max-h-80 overflow-y-auto">
            {mockActionsTaken.map((action, index) => (
              <motion.div
                key={action.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start gap-3 p-3 rounded-lg bg-background/50 border border-border/50"
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  action.status === "completed" 
                    ? "bg-success/20 text-success" 
                    : action.status === "in-progress"
                    ? "bg-warning/20 text-warning"
                    : "bg-muted/20 text-muted-foreground"
                }`}>
                  <action.icon className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="text-sm font-medium text-foreground">{action.action}</p>
                    {action.status === "completed" && (
                      <CheckCircle className="w-3 h-3 text-success" />
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mb-1">{action.timestamp}</p>
                  {action.details && (
                    <p className="text-xs text-muted-foreground font-mono bg-muted/30 px-2 py-1 rounded">
                      {action.details}
                    </p>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Sentiment & Stats */}
        <div className="space-y-6">
          <div className="text-center">
            <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
              Sentiment Analysis
            </p>
            <div className="flex justify-center mb-4">
              <SentimentGauge value={sentiment} size="lg" />
            </div>
            
            {/* Sentiment Progression */}
            <div className="bg-muted/30 rounded-lg p-3 text-left">
              <p className="text-xs text-muted-foreground uppercase mb-2">Initial User Sentiment</p>
              <div className="flex justify-between">
                <span className="text-sm">Call Start:</span>
                <span className="text-orange-500 font-medium">45% (Frustrated)</span>
              </div>
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
