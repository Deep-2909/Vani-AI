import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Users,
  CheckCircle,
  AlertTriangle,
  Clock,
  TrendingUp,
  FileText,
  MapPin,
  Phone,
} from "lucide-react";
import { getManagerStats, type ManagerStats } from "@/lib/api";

const ManagerDashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<ManagerStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      setIsLoading(true);
      const response = await getManagerStats();
      if (response.data) {
        setStats(response.data);
      }
      setIsLoading(false);
    };
    fetchStats();
  }, []);

  const statCards = stats
    ? [
      {
        label: "Open Complaints",
        value: stats.total_open_complaints,
        icon: AlertTriangle,
        color: "text-warning",
        bgColor: "bg-warning/10",
      },
      {
        label: "Resolved",
        value: stats.total_resolved_complaints,
        icon: CheckCircle,
        color: "text-success",
        bgColor: "bg-success/10",
      },
      {
        label: "Active Hotspots",
        value: stats.active_hotspots,
        icon: MapPin,
        color: "text-destructive",
        bgColor: "bg-destructive/10",
      },
      {
        label: "Avg Resolution Time",
        value: `${Math.round(stats.avg_resolution_hours)}h`,
        icon: Clock,
        color: "text-primary",
        bgColor: "bg-primary/10",
      },
    ]
    : [];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-3xl font-bold text-foreground">Manager Dashboard</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Government officials complaint management system
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button onClick={() => navigate("/complaints")} className="gap-2">
              <FileText className="w-4 h-4" />
              View Complaints
            </Button>
          </div>
        </motion.div>

        {/* Stats Cards */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="glass-card p-6 animate-pulse">
                <div className="h-20 bg-muted/20 rounded"></div>
              </Card>
            ))}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {statCards.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + index * 0.05 }}
              >
                <Card className="glass-card p-6 hover:border-primary/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground uppercase tracking-wider mb-2">
                        {stat.label}
                      </p>
                      <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                    </div>
                    <div className={`w-12 h-12 rounded-xl ${stat.bgColor} flex items-center justify-center`}>
                      <stat.icon className={`w-6 h-6 ${stat.color}`} />
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Priority Breakdown */}
        {stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6"
          >
            {/* By Priority */}
            <Card className="glass-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-5 h-5 text-primary" />
                <h3 className="text-lg font-semibold text-foreground">Priority Breakdown</h3>
              </div>
              <div className="space-y-4">
                {Object.entries(stats.by_priority).map(([priority, count]) => (
                  <div key={priority} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-3 h-3 rounded-full ${priority === "CRITICAL"
                            ? "bg-destructive"
                            : priority === "HIGH"
                              ? "bg-warning"
                              : "bg-success"
                          }`}
                      />
                      <span className="text-sm text-foreground capitalize">{priority.toLowerCase()}</span>
                    </div>
                    <span className="text-sm font-semibold text-foreground">{count}</span>
                  </div>
                ))}
              </div>
            </Card>

            {/* By Department */}
            <Card className="glass-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <Users className="w-5 h-5 text-primary" />
                <h3 className="text-lg font-semibold text-foreground">Top Departments</h3>
              </div>
              <div className="space-y-4">
                {Object.entries(stats.top_departments).map(([dept, count]) => (
                  <div key={dept} className="flex items-center justify-between">
                    <span className="text-sm text-foreground">{dept}</span>
                    <span className="text-sm font-semibold text-foreground">{count}</span>
                  </div>
                ))}
              </div>
            </Card>
          </motion.div>
        )}

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="glass-card p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">


              <Button
                onClick={() => navigate("/area-hotspots")}
                variant="outline"
                className="h-auto py-4 flex flex-col items-center gap-2"
              >
                <MapPin className="w-6 h-6" />
                <div className="text-center">
                  <p className="font-semibold">Monitor Hotspots</p>
                  <p className="text-xs text-muted-foreground">Track problem areas</p>
                </div>
              </Button>

              <Button
                onClick={() => navigate("/outbound-campaigns")}
                variant="outline"
                className="h-auto py-4 flex flex-col items-center gap-2"
              >
                <Phone className="w-6 h-6" />
                <div className="text-center">
                  <p className="font-semibold">Create Campaign</p>
                  <p className="text-xs text-muted-foreground">Initiate outbound calls</p>
                </div>
              </Button>
            </div>
          </Card>
        </motion.div>
      </div>
    </DashboardLayout>
  );
};

export default ManagerDashboard;
