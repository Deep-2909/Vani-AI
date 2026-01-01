import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Database, RefreshCw, Check, AlertCircle, Cloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type SyncStatus = "synced" | "syncing" | "error" | "idle";

interface SyncInfo {
  status: SyncStatus;
  lastSync: Date | null;
  documentsCount: number;
  vectorsCount: number;
}

export function SyncStatusIndicator() {
  const [syncInfo, setSyncInfo] = useState<SyncInfo>({
    status: "synced",
    lastSync: new Date(Date.now() - 1000 * 60 * 15), // 15 mins ago
    documentsCount: 24,
    vectorsCount: 15847,
  });

  const handleSync = () => {
    setSyncInfo((prev) => ({ ...prev, status: "syncing" }));

    // Simulate sync
    setTimeout(() => {
      setSyncInfo((prev) => ({
        ...prev,
        status: "synced",
        lastSync: new Date(),
        vectorsCount: prev.vectorsCount + Math.floor(Math.random() * 500),
      }));
    }, 3000);
  };

  const getStatusConfig = (status: SyncStatus) => {
    switch (status) {
      case "synced":
        return {
          icon: Check,
          label: "Synced",
          className: "text-success bg-success/10",
          dotClassName: "bg-success",
        };
      case "syncing":
        return {
          icon: RefreshCw,
          label: "Syncing...",
          className: "text-primary bg-primary/10",
          dotClassName: "bg-primary animate-pulse",
        };
      case "error":
        return {
          icon: AlertCircle,
          label: "Sync Error",
          className: "text-destructive bg-destructive/10",
          dotClassName: "bg-destructive",
        };
      default:
        return {
          icon: Cloud,
          label: "Idle",
          className: "text-muted-foreground bg-muted",
          dotClassName: "bg-muted-foreground",
        };
    }
  };

  const config = getStatusConfig(syncInfo.status);
  const StatusIcon = config.icon;

  const formatLastSync = (date: Date | null) => {
    if (!date) return "Never";
    const diff = Date.now() - date.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card-elevated p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-accent/20 flex items-center justify-center">
            <Database className="w-5 h-5 text-accent" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground">Pinecone Sync</h3>
            <p className="text-sm text-muted-foreground">Vector database status</p>
          </div>
        </div>

        <Button
          onClick={handleSync}
          disabled={syncInfo.status === "syncing"}
          className="gap-2"
          variant="outline"
        >
          <RefreshCw
            className={cn("w-4 h-4", syncInfo.status === "syncing" && "animate-spin")}
          />
          {syncInfo.status === "syncing" ? "Syncing..." : "Sync Now"}
        </Button>
      </div>

      {/* Status Badge */}
      <div
        className={cn(
          "inline-flex items-center gap-2 px-3 py-1.5 rounded-full mb-6",
          config.className
        )}
      >
        <span className={cn("w-2 h-2 rounded-full", config.dotClassName)} />
        <StatusIcon
          className={cn("w-4 h-4", syncInfo.status === "syncing" && "animate-spin")}
        />
        <span className="text-sm font-medium">{config.label}</span>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-muted/30 border border-border">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
            Last Sync
          </p>
          <p className="text-lg font-semibold text-foreground">
            {formatLastSync(syncInfo.lastSync)}
          </p>
        </div>

        <div className="p-4 rounded-xl bg-muted/30 border border-border">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
            Documents
          </p>
          <p className="text-lg font-semibold text-foreground">
            {syncInfo.documentsCount}
          </p>
        </div>

        <div className="p-4 rounded-xl bg-muted/30 border border-border">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
            Vectors
          </p>
          <p className="text-lg font-semibold text-foreground">
            {syncInfo.vectorsCount.toLocaleString()}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
