import { Phone, Clock, TrendingUp, DollarSign, ArrowRight } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { AnalyticsCard } from "@/components/dashboard/AnalyticsCard";
import { ActiveCallsMonitor } from "@/components/dashboard/ActiveCallsMonitor";
import { CallLogsTable } from "@/components/dashboard/CallLogsTable";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { generateMockAnalytics } from "@/lib/api";

const analytics = generateMockAnalytics();

const Index = () => {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Analytics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <AnalyticsCard
            title="Total Calls"
            value={analytics.totalCalls.toLocaleString()}
            subtitle={`${analytics.callsToday} today`}
            icon={Phone}
            trend={{ value: 12.5, isPositive: true }}
            variant="primary"
            delay={0}
          />
          <AnalyticsCard
            title="Avg. Resolution Time"
            value={`${Math.floor(analytics.avgResolutionTime / 60)}:${(analytics.avgResolutionTime % 60).toString().padStart(2, "0")}`}
            subtitle="minutes"
            icon={Clock}
            trend={{ value: 8.2, isPositive: true }}
            variant="default"
            delay={0.1}
          />
          <AnalyticsCard
            title="Success Rate"
            value={`${analytics.successRate}%`}
            subtitle="calls resolved"
            icon={TrendingUp}
            trend={{ value: 3.1, isPositive: true }}
            variant="success"
            delay={0.2}
          />
          <AnalyticsCard
            title="Cost Saved"
            value={`$${(analytics.costSaved / 1000).toFixed(0)}K`}
            subtitle="this month"
            icon={DollarSign}
            trend={{ value: 24.3, isPositive: true }}
            variant="warning"
            delay={0.3}
          />
        </div>

        {/* Live Call Monitor */}
        <ActiveCallsMonitor />

        {/* Recent Calls */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-foreground">Recent Calls</h3>
              <p className="text-sm text-muted-foreground">
                Overview of the latest call activity
              </p>
            </div>
            <Link to="/call-logs">
              <Button variant="ghost" className="gap-2 text-primary hover:text-primary">
                View All
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
          <CallLogsTable limit={5} showHeader={false} />
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Index;
