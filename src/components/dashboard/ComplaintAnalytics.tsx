import { motion } from "framer-motion";
import { MapPin, AlertTriangle, TrendingUp, Users } from "lucide-react";

interface LocationData {
  location: string;
  complaints: number;
  trend: "up" | "down" | "stable";
  percentage: number;
}

interface IssueData {
  issue: string;
  complaints: number;
  trend: "up" | "down" | "stable";
  percentage: number;
  severity: "high" | "medium" | "low";
}

const topLocations: LocationData[] = [
  { location: "Dwarka Sector 12", complaints: 47, trend: "up", percentage: 18.2 },
  { location: "Rohini Sector 8", complaints: 34, trend: "down", percentage: 13.1 },
  { location: "Lajpat Nagar", complaints: 29, trend: "up", percentage: 11.2 },
  { location: "Karol Bagh", complaints: 25, trend: "stable", percentage: 9.7 },
  { location: "Janakpuri West", complaints: 22, trend: "down", percentage: 8.5 },
];

const topIssues: IssueData[] = [
  { issue: "Water Supply", complaints: 89, trend: "up", percentage: 34.5, severity: "high" },
  { issue: "Electricity", complaints: 56, trend: "stable", percentage: 21.7, severity: "high" },
  { issue: "Road Maintenance", complaints: 43, trend: "down", percentage: 16.7, severity: "medium" },
  { issue: "Garbage Collection", complaints: 31, trend: "up", percentage: 12.0, severity: "medium" },
  { issue: "Street Lighting", complaints: 23, trend: "stable", percentage: 8.9, severity: "low" },
];

export function ComplaintAnalytics() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="glass-card-elevated p-6"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-accent/20 flex items-center justify-center">
          <TrendingUp className="w-5 h-5 text-accent" />
        </div>
        <div>
          <h3 className="font-semibold text-foreground">Complaint Analytics</h3>
          <p className="text-sm text-muted-foreground">
            Top locations and issues (Last 7 days)
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Locations */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <MapPin className="w-4 h-4 text-primary" />
            <h4 className="font-medium text-foreground">Top 5 Locations</h4>
          </div>
          
          <div className="space-y-3">
            {topLocations.map((location, index) => (
              <motion.div
                key={location.location}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 rounded-lg bg-muted/30 border border-border/50"
              >
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">{location.location}</p>
                    <p className="text-xs text-muted-foreground">{location.percentage}% of total</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-foreground">{location.complaints}</span>
                  <div className={`w-2 h-2 rounded-full ${
                    location.trend === "up" ? "bg-red-500" : 
                    location.trend === "down" ? "bg-green-500" : "bg-yellow-500"
                  }`} />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Top Issues */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-4 h-4 text-warning" />
            <h4 className="font-medium text-foreground">Top 5 Issues</h4>
          </div>
          
          <div className="space-y-3">
            {topIssues.map((issue, index) => (
              <motion.div
                key={issue.issue}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 rounded-lg bg-muted/30 border border-border/50"
              >
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-warning/20 flex items-center justify-center text-xs font-bold text-warning">
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">{issue.issue}</p>
                    <div className="flex items-center gap-2">
                      <p className="text-xs text-muted-foreground">{issue.percentage}% of total</p>
                      <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                        issue.severity === "high" ? "bg-red-500/20 text-red-500" :
                        issue.severity === "medium" ? "bg-yellow-500/20 text-yellow-500" :
                        "bg-green-500/20 text-green-500"
                      }`}>
                        {issue.severity}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-foreground">{issue.complaints}</span>
                  <div className={`w-2 h-2 rounded-full ${
                    issue.trend === "up" ? "bg-red-500" : 
                    issue.trend === "down" ? "bg-green-500" : "bg-yellow-500"
                  }`} />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 pt-4 border-t border-border">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Users className="w-4 h-4 text-muted-foreground" />
              <p className="text-xs text-muted-foreground uppercase">Total Complaints</p>
            </div>
            <p className="text-lg font-bold text-foreground">258</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <TrendingUp className="w-4 h-4 text-success" />
              <p className="text-xs text-muted-foreground uppercase">Resolved</p>
            </div>
            <p className="text-lg font-bold text-success">234</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <AlertTriangle className="w-4 h-4 text-warning" />
              <p className="text-xs text-muted-foreground uppercase">Pending</p>
            </div>
            <p className="text-lg font-bold text-warning">24</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}