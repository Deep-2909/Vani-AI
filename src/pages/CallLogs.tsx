import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Filter, Download, Calendar } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { CallLogsTable } from "@/components/dashboard/CallLogsTable";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function CallLogs() {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row md:items-center md:justify-between gap-4"
        >
          <div>
            <h1 className="text-2xl font-bold text-foreground">Call Logs</h1>
            <p className="text-muted-foreground">
              View and manage all call recordings and transcripts
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button variant="outline" className="gap-2">
              <Calendar className="w-4 h-4" />
              Date Range
            </Button>
            <Button variant="outline" className="gap-2">
              <Download className="w-4 h-4" />
              Export
            </Button>
          </div>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-col md:flex-row gap-4"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search by caller ID, transcript..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-muted/30 border-border"
            />
          </div>

          <div className="flex gap-2">
            <Button variant="outline" className="gap-2">
              <Filter className="w-4 h-4" />
              Filters
            </Button>
          </div>
        </motion.div>

        {/* Stats Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          {[
            { label: "Total", value: "2,847", color: "text-foreground" },
            { label: "Inbound", value: "1,923", color: "text-success" },
            { label: "Outbound", value: "924", color: "text-primary" },
            { label: "Avg Duration", value: "4:32", color: "text-warning" },
          ].map((stat, index) => (
            <div
              key={stat.label}
              className="glass-card p-4 text-center"
            >
              <p className="text-xs text-muted-foreground uppercase tracking-wider">
                {stat.label}
              </p>
              <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
            </div>
          ))}
        </motion.div>

        {/* Table */}
        <CallLogsTable limit={20} />
      </div>
    </DashboardLayout>
  );
}
