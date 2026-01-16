import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Search, Filter, CheckCircle, AlertCircle, Clock, MapPin } from "lucide-react";
import { getComplaints, resolveComplaint, getResolvedComplaints, type Complaint } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const Complaints = () => {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [resolvedComplaints, setResolvedComplaints] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedComplaint, setSelectedComplaint] = useState<Complaint | null>(null);
  const [isResolveDialogOpen, setIsResolveDialogOpen] = useState(false);
  const [resolveData, setResolveData] = useState({
    resolved_by: "",
    resolution_notes: "",
    citizen_rating: 0,
  });
  const [isResolving, setIsResolving] = useState(false);
  const [activeTab, setActiveTab] = useState<"open" | "resolved">("open");
  const [filters, setFilters] = useState({
    department: "",
    priority: "",
    status: "",
  });

  useEffect(() => {
    if (activeTab === "open") {
      fetchComplaints();
    } else {
      fetchResolvedComplaints();
    }
  }, [activeTab, filters]);

  const fetchComplaints = async () => {
    setIsLoading(true);
    const response = await getComplaints({
      limit: 50,
      ...filters,
    });
    if (response.data) {
      setComplaints(response.data.complaints);
    }
    setIsLoading(false);
  };

  const fetchResolvedComplaints = async () => {
    setIsLoading(true);
    const response = await getResolvedComplaints(50, 0);
    if (response.data) {
      setResolvedComplaints(response.data.complaints);
    }
    setIsLoading(false);
  };

  const handleResolve = (complaint: Complaint) => {
    setSelectedComplaint(complaint);
    setIsResolveDialogOpen(true);
  };

  const submitResolve = async () => {
    if (!selectedComplaint) return;
    if (!resolveData.resolved_by || !resolveData.resolution_notes) {
      toast.error("Please fill in all required fields");
      return;
    }

    setIsResolving(true);
    const response = await resolveComplaint({
      ticket_id: selectedComplaint.ticket_id,
      ...resolveData,
    });

    if (response.data) {
      toast.success(`Complaint resolved! Resolution time: ${response.data.resolution_time_hours}h`);
      setIsResolveDialogOpen(false);
      setSelectedComplaint(null);
      setResolveData({ resolved_by: "", resolution_notes: "", citizen_rating: 0 });
      fetchComplaints();
    } else {
      toast.error(response.error || "Failed to resolve complaint");
    }
    setIsResolving(false);
  };

  const getPriorityBadge = (priority: string) => {
    const variants = {
      CRITICAL: "bg-destructive text-destructive-foreground",
      HIGH: "bg-warning text-warning-foreground",
      MEDIUM: "bg-blue-500/10 text-blue-600 border-blue-500/30",
      LOW: "bg-success/10 text-success border-success/30",
    };
    return variants[priority as keyof typeof variants] || variants.MEDIUM;
  };

  const filteredComplaints = complaints.filter((c) =>
    (c.citizen_name || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
    (c.ticket_id || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
    (c.description || "").toLowerCase().includes(searchQuery.toLowerCase())
  );

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
            <h1 className="text-3xl font-bold text-foreground">Complaints Management</h1>
            <p className="text-sm text-muted-foreground mt-1">
              View, filter, and resolve citizen complaints
            </p>
          </div>
        </motion.div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-border">
          <button
            onClick={() => setActiveTab("open")}
            className={cn(
              "px-4 py-2 font-medium transition-colors relative",
              activeTab === "open"
                ? "text-primary"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            Open Complaints
            {activeTab === "open" && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("resolved")}
            className={cn(
              "px-4 py-2 font-medium transition-colors relative",
              activeTab === "resolved"
                ? "text-primary"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            Resolved
            {activeTab === "resolved" && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
            )}
          </button>
        </div>

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
              placeholder="Search by name, ticket ID, or description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-muted/30 border-border"
            />
          </div>

          {activeTab === "open" && (
            <>
              <Select
                value={filters.department}
                onValueChange={(value) => setFilters({ ...filters, department: value })}
              >
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Department" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Departments</SelectItem>
                  <SelectItem value="Water">Water</SelectItem>
                  <SelectItem value="Roads">Roads</SelectItem>
                  <SelectItem value="Electricity">Electricity</SelectItem>
                  <SelectItem value="Health">Health</SelectItem>
                </SelectContent>
              </Select>

              <Select
                value={filters.priority}
                onValueChange={(value) => setFilters({ ...filters, priority: value })}
              >
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Priorities</SelectItem>
                  <SelectItem value="CRITICAL">Critical</SelectItem>
                  <SelectItem value="HIGH">High</SelectItem>
                  <SelectItem value="MEDIUM">Medium</SelectItem>
                  <SelectItem value="LOW">Low</SelectItem>
                </SelectContent>
              </Select>
            </>
          )}
        </motion.div>

        {/* Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="glass-card">
            <Table>
              <TableHeader>
                <TableRow className="border-border hover:bg-transparent">
                  <TableHead>Ticket ID</TableHead>
                  <TableHead>Citizen</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Area</TableHead>
                  <TableHead>Created</TableHead>
                  {activeTab === "open" && <TableHead className="text-right">Action</TableHead>}
                  {activeTab === "resolved" && <TableHead>Resolution Time</TableHead>}
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={activeTab === "open" ? 7 : 7} className="text-center py-8">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                        <span className="text-muted-foreground">Loading complaints...</span>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : activeTab === "open" && filteredComplaints.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                      No complaints found
                    </TableCell>
                  </TableRow>
                ) : activeTab === "resolved" && resolvedComplaints.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                      No resolved complaints yet
                    </TableCell>
                  </TableRow>
                ) : activeTab === "open" ? (
                  filteredComplaints.map((complaint) => (
                    <TableRow key={complaint.ticket_id} className="border-border hover:bg-muted/30">
                      <TableCell className="font-mono text-sm">{complaint.ticket_id}</TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium text-foreground">{complaint.citizen_name}</p>
                          <p className="text-xs text-muted-foreground line-clamp-1">
                            {complaint.description}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>{complaint.department}</TableCell>
                      <TableCell>
                        <Badge className={cn("text-xs", getPriorityBadge(complaint.priority))}>
                          {complaint.priority}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <MapPin className="w-3 h-3" />
                          {complaint.area || "N/A"}
                        </div>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(complaint.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          size="sm"
                          onClick={() => handleResolve(complaint)}
                          className="gap-2"
                        >
                          <CheckCircle className="w-3 h-3" />
                          Resolve
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  resolvedComplaints.map((complaint) => (
                    <TableRow key={complaint.ticket_id} className="border-border hover:bg-muted/30">
                      <TableCell className="font-mono text-sm">{complaint.ticket_id}</TableCell>
                      <TableCell className="font-medium">{complaint.citizen_name}</TableCell>
                      <TableCell>{complaint.department}</TableCell>
                      <TableCell>
                        <Badge className={cn("text-xs", getPriorityBadge(complaint.priority))}>
                          {complaint.priority}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {complaint.resolved_by}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {complaint.resolved_at
                          ? new Date(complaint.resolved_at).toLocaleDateString()
                          : "N/A"}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-sm text-success">
                          <Clock className="w-3 h-3" />
                          {complaint.resolution_hours}h
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </motion.div>
      </div>

      {/* Resolve Dialog */}
      <Dialog open={isResolveDialogOpen} onOpenChange={setIsResolveDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Resolve Complaint</DialogTitle>
            <DialogDescription>
              Mark this complaint as resolved and provide resolution details
            </DialogDescription>
          </DialogHeader>

          {selectedComplaint && (
            <div className="space-y-4">
              <div className="p-4 bg-muted/30 rounded-lg space-y-2">
                <p className="text-sm">
                  <span className="font-semibold">Ticket ID:</span> {selectedComplaint.ticket_id}
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Citizen:</span> {selectedComplaint.citizen_name}
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Issue:</span> {selectedComplaint.description}
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Your Name (Manager)</label>
                <Input
                  placeholder="Enter your name"
                  value={resolveData.resolved_by}
                  onChange={(e) =>
                    setResolveData({ ...resolveData, resolved_by: e.target.value })
                  }
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Resolution Notes</label>
                <Textarea
                  placeholder="Describe how the complaint was resolved..."
                  value={resolveData.resolution_notes}
                  onChange={(e) =>
                    setResolveData({ ...resolveData, resolution_notes: e.target.value })
                  }
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Citizen Rating (Optional)</label>
                <Select
                  value={resolveData.citizen_rating.toString()}
                  onValueChange={(value) =>
                    setResolveData({ ...resolveData, citizen_rating: parseInt(value) })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select rating" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">Not rated</SelectItem>
                    <SelectItem value="5">⭐⭐⭐⭐⭐ Excellent</SelectItem>
                    <SelectItem value="4">⭐⭐⭐⭐ Good</SelectItem>
                    <SelectItem value="3">⭐⭐⭐ Average</SelectItem>
                    <SelectItem value="2">⭐⭐ Poor</SelectItem>
                    <SelectItem value="1">⭐ Very Poor</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsResolveDialogOpen(false);
                setSelectedComplaint(null);
                setResolveData({ resolved_by: "", resolution_notes: "", citizen_rating: 0 });
              }}
              disabled={isResolving}
            >
              Cancel
            </Button>
            <Button onClick={submitResolve} disabled={isResolving}>
              {isResolving ? "Resolving..." : "Resolve Complaint"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
};

export default Complaints;
