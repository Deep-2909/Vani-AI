import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Search, Filter, Download, Calendar } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { CallLogsTable } from "@/components/dashboard/CallLogsTable";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getCalls } from "@/lib/api";

export default function CallLogs() {
  const [searchQuery, setSearchQuery] = useState("");
  const [stats, setStats] = useState({
    total: 0,
    inbound: 0,
    outbound: 0,
    avgDuration: "0:00"
  });

  useEffect(() => {
    const fetchStats = async () => {
      const response = await getCalls({ limit: 1000 });
      if (response.data) {
        const calls = response.data;
        const inbound = calls.filter(c => c.type === 'inbound').length;
        const outbound = calls.filter(c => c.type === 'outbound').length;
        const totalDuration = calls.reduce((sum, c) => sum + c.duration, 0);
        const avgSeconds = calls.length > 0 ? Math.floor(totalDuration / calls.length) : 0;
        const avgMins = Math.floor(avgSeconds / 60);
        const avgSecs = avgSeconds % 60;

        setStats({
          total: calls.length,
          inbound,
          outbound,
          avgDuration: `${avgMins}:${avgSecs.toString().padStart(2, '0')}`
        });
      }
    };
    fetchStats();
  }, []);

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
            { label: "Total", value: stats.total.toString(), color: "text-foreground" },
            { label: "Inbound", value: stats.inbound.toString(), color: "text-success" },
            { label: "Outbound", value: stats.outbound.toString(), color: "text-primary" },
            { label: "Avg Duration", value: stats.avgDuration, color: "text-warning" },
          ].map((stat) => (
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
