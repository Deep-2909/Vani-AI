import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { MapPin, AlertTriangle, TrendingUp, Droplet, Construction, Zap } from "lucide-react";
import { getAreaHotspots, getAreaDetails, type AreaHotspot } from "@/lib/api";
import { cn } from "@/lib/utils";

const AreaHotspots = () => {
  const [hotspots, setHotspots] = useState<AreaHotspot[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [flaggedOnly, setFlaggedOnly] = useState(false);
  const [selectedArea, setSelectedArea] = useState<string | null>(null);
  const [areaDetails, setAreaDetails] = useState<any>(null);
  const [isDetailsDialogOpen, setIsDetailsDialogOpen] = useState(false);

  useEffect(() => {
    fetchHotspots();
  }, [flaggedOnly]);

  const fetchHotspots = async () => {
    setIsLoading(true);
    const response = await getAreaHotspots(flaggedOnly, 5);
    if (response.data) {
      setHotspots(response.data.hotspots);
    }
    setIsLoading(false);
  };

  const handleViewDetails = async (areaName: string) => {
    setSelectedArea(areaName);
    const response = await getAreaDetails(areaName);
    if (response.data) {
      setAreaDetails(response.data);
      setIsDetailsDialogOpen(true);
    }
  };

  const getHotspotLevelBadge = (level: string) => {
    const variants = {
      CRITICAL: "bg-destructive text-destructive-foreground",
      HIGH: "bg-warning text-warning-foreground",
      MEDIUM: "bg-blue-500/10 text-blue-600 border-blue-500/30",
      LOW: "bg-success/10 text-success border-success/30",
    };
    return variants[level as keyof typeof variants] || variants.MEDIUM;
  };

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
            <h1 className="text-3xl font-bold text-foreground">Area Hotspots</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Monitor areas with high complaint density
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Switch checked={flaggedOnly} onCheckedChange={setFlaggedOnly} />
              <span className="text-sm text-muted-foreground">Flagged Only</span>
            </div>
          </div>
        </motion.div>

        {/* Stats Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <Card className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground uppercase tracking-wider mb-2">
                  Total Hotspots
                </p>
                <p className="text-3xl font-bold text-foreground">{hotspots.length}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-destructive/10 flex items-center justify-center">
                <MapPin className="w-6 h-6 text-destructive" />
              </div>
            </div>
          </Card>

          <Card className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground uppercase tracking-wider mb-2">
                  Flagged Areas
                </p>
                <p className="text-3xl font-bold text-warning">
                  {hotspots.filter((h) => h.is_hotspot).length}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-warning/10 flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-warning" />
              </div>
            </div>
          </Card>

          <Card className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground uppercase tracking-wider mb-2">
                  Open Complaints
                </p>
                <p className="text-3xl font-bold text-primary">
                  {hotspots.reduce((sum, h) => sum + h.open_complaints, 0)}
                </p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-primary" />
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Hotspots Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i} className="glass-card p-6 animate-pulse">
                <div className="h-40 bg-muted/20 rounded"></div>
              </Card>
            ))}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {hotspots.map((hotspot, index) => (
              <motion.div
                key={hotspot.area_name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.05 }}
              >
                <Card className="glass-card p-6 hover:border-primary/50 transition-colors cursor-pointer">
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <MapPin className="w-5 h-5 text-primary" />
                        <h3 className="font-semibold text-foreground">{hotspot.area_name}</h3>
                      </div>
                      {hotspot.is_hotspot && (
                        <Badge className={cn("text-xs", getHotspotLevelBadge(hotspot.hotspot_level))}>
                          {hotspot.hotspot_level}
                        </Badge>
                      )}
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <p className="text-2xl font-bold text-foreground">{hotspot.total_complaints}</p>
                        <p className="text-xs text-muted-foreground">Total</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-warning">{hotspot.open_complaints}</p>
                        <p className="text-xs text-muted-foreground">Open</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-success">{hotspot.resolved_complaints}</p>
                        <p className="text-xs text-muted-foreground">Resolved</p>
                      </div>
                    </div>

                    {/* Category Breakdown */}
                    <div className="space-y-2">
                      <p className="text-xs text-muted-foreground uppercase tracking-wider">Breakdown</p>
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <Droplet className="w-4 h-4 text-blue-500" />
                          <span className="text-muted-foreground">Water</span>
                        </div>
                        <span className="font-semibold text-foreground">{hotspot.breakdown.water}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <Construction className="w-4 h-4 text-orange-500" />
                          <span className="text-muted-foreground">Roads</span>
                        </div>
                        <span className="font-semibold text-foreground">{hotspot.breakdown.road}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <Zap className="w-4 h-4 text-yellow-500" />
                          <span className="text-muted-foreground">Electricity</span>
                        </div>
                        <span className="font-semibold text-foreground">{hotspot.breakdown.electricity}</span>
                      </div>
                    </div>

                    {/* Priority Stats */}
                    <div className="flex items-center justify-between pt-4 border-t border-border">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="w-2 h-2 rounded-full bg-destructive"></span>
                        <span className="text-muted-foreground">Critical:</span>
                        <span className="font-semibold text-foreground">
                          {hotspot.priority_breakdown.critical}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="w-2 h-2 rounded-full bg-warning"></span>
                        <span className="text-muted-foreground">High:</span>
                        <span className="font-semibold text-foreground">
                          {hotspot.priority_breakdown.high}
                        </span>
                      </div>
                    </div>

                    {/* View Details Button */}
                    <Button
                      onClick={() => handleViewDetails(hotspot.area_name)}
                      variant="outline"
                      className="w-full"
                      size="sm"
                    >
                      View Details
                    </Button>
                  </div>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}

        {!isLoading && hotspots.length === 0 && (
          <Card className="glass-card p-12 text-center">
            <MapPin className="w-16 h-16 mx-auto mb-4 text-muted-foreground/30" />
            <h3 className="text-lg font-semibold text-foreground mb-2">No hotspots found</h3>
            <p className="text-sm text-muted-foreground">
              {flaggedOnly
                ? "No flagged areas. Try disabling the filter."
                : "All areas are under control."}
            </p>
          </Card>
        )}
      </div>

      {/* Area Details Dialog */}
      <Dialog open={isDetailsDialogOpen} onOpenChange={setIsDetailsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              {selectedArea}
            </DialogTitle>
            <DialogDescription>Detailed complaint breakdown for this area</DialogDescription>
          </DialogHeader>

          {areaDetails && (
            <div className="space-y-6">
              {/* Stats */}
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-muted/30 rounded-lg">
                  <p className="text-2xl font-bold text-foreground">{areaDetails.stats.total_complaints}</p>
                  <p className="text-sm text-muted-foreground">Total</p>
                </div>
                <div className="text-center p-4 bg-muted/30 rounded-lg">
                  <p className="text-2xl font-bold text-warning">{areaDetails.stats.open}</p>
                  <p className="text-sm text-muted-foreground">Open</p>
                </div>
                <div className="text-center p-4 bg-muted/30 rounded-lg">
                  <p className="text-2xl font-bold text-success">{areaDetails.stats.resolved}</p>
                  <p className="text-sm text-muted-foreground">Resolved</p>
                </div>
              </div>

              {/* Recent Complaints */}
              <div>
                <h4 className="font-semibold text-foreground mb-3">Recent Complaints</h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {areaDetails.recent_complaints.map((complaint: any) => (
                    <div
                      key={complaint.ticket_id}
                      className="p-3 bg-muted/20 rounded-lg border border-border"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-mono text-sm text-foreground">{complaint.ticket_id}</span>
                        <Badge variant="secondary" className="text-xs">
                          {complaint.priority}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{complaint.category}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
};

export default AreaHotspots;
