import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
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
import { Phone, Plus, CheckCircle, Clock, XCircle, Loader2 } from "lucide-react";
import { getOutboundCallsStatus, initiateOutboundCalls, type OutboundCall } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const OutboundCampaigns = () => {
  const [campaigns, setCampaigns] = useState<OutboundCall[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [campaignData, setCampaignData] = useState({
    call_type: "",
    message_content: "",
    language: "hindi",
    phone_numbers: "",
  });

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    setIsLoading(true);
    const response = await getOutboundCallsStatus(undefined, undefined, 50);
    if (response.data) {
      setCampaigns(response.data.calls);
    }
    setIsLoading(false);
  };

  const handleCreateCampaign = async () => {
    if (!campaignData.call_type || !campaignData.message_content || !campaignData.phone_numbers) {
      toast.error("Please fill in all required fields");
      return;
    }

    // Parse phone numbers (comma or newline separated)
    const phoneNumbers = campaignData.phone_numbers
      .split(/[,\n]/)
      .map((num) => num.trim())
      .filter((num) => num.length > 0);

    if (phoneNumbers.length === 0) {
      toast.error("Please provide at least one phone number");
      return;
    }

    setIsCreating(true);
    const response = await initiateOutboundCalls({
      phone_numbers: phoneNumbers,
      call_type: campaignData.call_type,
      message_content: campaignData.message_content,
      language: campaignData.language,
    });

    if (response.data) {
      toast.success(`Campaign created! ${phoneNumbers.length} calls initiated`);
      setIsCreateDialogOpen(false);
      setCampaignData({
        call_type: "",
        message_content: "",
        language: "hindi",
        phone_numbers: "",
      });
      fetchCampaigns();
    } else {
      toast.error(response.error || "Failed to create campaign");
    }
    setIsCreating(false);
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      PENDING: "bg-blue-500/10 text-blue-600 border-blue-500/30",
      INITIATED: "bg-warning/10 text-warning border-warning/30",
      COMPLETED: "bg-success/10 text-success border-success/30",
      FAILED: "bg-destructive/10 text-destructive border-destructive/30",
    };
    return variants[status as keyof typeof variants] || variants.PENDING;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return <CheckCircle className="w-4 h-4" />;
      case "FAILED":
        return <XCircle className="w-4 h-4" />;
      case "INITIATED":
        return <Loader2 className="w-4 h-4 animate-spin" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  // Group campaigns by type
  const campaignStats = campaigns.reduce(
    (acc, call) => {
      acc.total++;
      if (call.status === "COMPLETED") acc.completed++;
      if (call.status === "PENDING") acc.pending++;
      if (call.answered) acc.answered++;
      return acc;
    },
    { total: 0, completed: 0, pending: 0, answered: 0 }
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
            <h1 className="text-3xl font-bold text-foreground">Outbound Campaigns</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Create and manage proactive calling campaigns
            </p>
          </div>
          <Button onClick={() => setIsCreateDialogOpen(true)} className="gap-2">
            <Plus className="w-4 h-4" />
            Create Campaign
          </Button>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6"
        >
          <Card className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground uppercase tracking-wider mb-2">
                  Total Calls
                </p>
                <p className="text-3xl font-bold text-foreground">{campaignStats.total}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <Phone className="w-6 h-6 text-primary" />
              </div>
            </div>
          </Card>

          <Card className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground uppercase tracking-wider mb-2">Completed</p>
                <p className="text-3xl font-bold text-success">{campaignStats.completed}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-success/10 flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-success" />
              </div>
            </div>
          </Card>

          <Card className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground uppercase tracking-wider mb-2">Pending</p>
                <p className="text-3xl font-bold text-warning">{campaignStats.pending}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-warning/10 flex items-center justify-center">
                <Clock className="w-6 h-6 text-warning" />
              </div>
            </div>
          </Card>

          <Card className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground uppercase tracking-wider mb-2">Answered</p>
                <p className="text-3xl font-bold text-foreground">{campaignStats.answered}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
                <Phone className="w-6 h-6 text-blue-500" />
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Campaigns List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="glass-card p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Recent Campaigns</h3>

            {isLoading ? (
              <div className="text-center py-8">
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  <span className="text-muted-foreground">Loading campaigns...</span>
                </div>
              </div>
            ) : campaigns.length === 0 ? (
              <div className="text-center py-12">
                <Phone className="w-16 h-16 mx-auto mb-4 text-muted-foreground/30" />
                <h3 className="text-lg font-semibold text-foreground mb-2">No campaigns yet</h3>
                <p className="text-sm text-muted-foreground mb-6">
                  Create your first outbound calling campaign
                </p>
                <Button onClick={() => setIsCreateDialogOpen(true)} className="gap-2">
                  <Plus className="w-4 h-4" />
                  Create Campaign
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {campaigns.map((call) => (
                  <div
                    key={call.call_id}
                    className="p-4 bg-muted/20 rounded-lg border border-border hover:bg-muted/30 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="font-mono text-sm text-foreground">{call.call_id}</span>
                          <Badge className={cn("text-xs", getStatusBadge(call.status))}>
                            <div className="flex items-center gap-1">
                              {getStatusIcon(call.status)}
                              {call.status}
                            </div>
                          </Badge>
                          <Badge variant="outline" className="text-xs capitalize">
                            {call.call_type.replace("_", " ")}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>To: {call.phone_number}</span>
                          <span>•</span>
                          <span className="capitalize">{call.language}</span>
                          <span>•</span>
                          <span>{new Date(call.initiated_at).toLocaleString()}</span>
                        </div>
                      </div>
                      {call.answered && (
                        <div className="flex items-center gap-2 text-success">
                          <CheckCircle className="w-4 h-4" />
                          <span className="text-sm font-medium">Answered</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </motion.div>
      </div>

      {/* Create Campaign Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Create Outbound Campaign</DialogTitle>
            <DialogDescription>
              Set up a new calling campaign to reach citizens proactively
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Campaign Type</label>
              <Select
                value={campaignData.call_type}
                onValueChange={(value) => setCampaignData({ ...campaignData, call_type: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="scheme_notification">Scheme Notification</SelectItem>
                  <SelectItem value="alert">Emergency Alert</SelectItem>
                  <SelectItem value="follow_up">Follow-up Call</SelectItem>
                  <SelectItem value="survey">Survey</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Language</label>
              <Select
                value={campaignData.language}
                onValueChange={(value) => setCampaignData({ ...campaignData, language: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hindi">Hindi</SelectItem>
                  <SelectItem value="english">English</SelectItem>
                  <SelectItem value="punjabi">Punjabi</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Message Content</label>
              <Textarea
                placeholder="Enter the message that will be conveyed to citizens..."
                value={campaignData.message_content}
                onChange={(e) =>
                  setCampaignData({ ...campaignData, message_content: e.target.value })
                }
                rows={4}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Phone Numbers</label>
              <Textarea
                placeholder="Enter phone numbers (comma or newline separated)&#10;+91-9876543210&#10;+91-9876543211"
                value={campaignData.phone_numbers}
                onChange={(e) =>
                  setCampaignData({ ...campaignData, phone_numbers: e.target.value })
                }
                rows={4}
              />
              <p className="text-xs text-muted-foreground">
                Enter multiple phone numbers separated by commas or new lines
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsCreateDialogOpen(false);
                setCampaignData({
                  call_type: "",
                  message_content: "",
                  language: "hindi",
                  phone_numbers: "",
                });
              }}
              disabled={isCreating}
            >
              Cancel
            </Button>
            <Button onClick={handleCreateCampaign} disabled={isCreating}>
              {isCreating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create Campaign"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
};

export default OutboundCampaigns;
