import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Phone,
  PhoneIncoming,
  Settings as SettingsIcon,
  Edit2,
  UserPlus,
  Upload,
  Database,
  Info,
} from "lucide-react";
import { toast } from "sonner";
import { getAgentConfig, updateAgentConfig, startInboundAgent, startOutboundCalling } from "@/lib/api";

const Index = () => {
  const navigate = useNavigate();
  const [isEditingName, setIsEditingName] = useState(false);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [agentName, setAgentName] = useState("Voice AI");
  const [agentDescription, setAgentDescription] = useState(
    "Voice AI is an AI voice agent serving jhh to help people through voice interactions and knowledge access."
  );

  // Tool toggles
  const [tools, setTools] = useState({
    knowledgeQuery: false,
    endCall: false,
    complainTicket: false,
  });

  useEffect(() => {
    const fetchConfig = async () => {
      const response = await getAgentConfig();
      if (response.data) {
        setAgentName(response.data.agentName);
        setAgentDescription(response.data.agentDescription);
        setTools({
          knowledgeQuery: response.data.tools.knowledgeQuery,
          endCall: response.data.tools.endCall,
          complainTicket: response.data.tools.complainTicket,
        });
      }
    };
    fetchConfig();
  }, []);

  const handleToggleTool = async (tool: keyof typeof tools) => {
    const newValue = !tools[tool];
    setTools({ ...tools, [tool]: newValue });

    // Save to backend
    await updateAgentConfig({
      tools: { ...tools, [tool]: newValue }
    });

    toast.success(`${tool} tool ${newValue ? "enabled" : "disabled"}`);
  };

  const handleStartOutbound = async () => {
    toast.info("Starting outbound calling...");
    const response = await startOutboundCalling();
    if (response.data) {
      toast.success(response.data.message);
    } else {
      toast.error(response.error || "Failed to start outbound calling");
    }
  };

  const handleStartInbound = async () => {
    toast.info("Starting inbound agent...");
    const response = await startInboundAgent();
    if (response.data) {
      toast.success(response.data.message);
    } else {
      toast.error(response.error || "Failed to start inbound agent");
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-primary mb-2">Voice AI</h1>
            <p className="text-base text-muted-foreground">
              AI Voice Partner for Public Outreach in Delhi
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button onClick={handleStartOutbound} className="gap-2 px-6">
              <Phone className="w-4 h-4" />
              Start Outbound Calling
            </Button>
            <Button onClick={handleStartInbound} variant="secondary" className="gap-2 px-6">
              <PhoneIncoming className="w-4 h-4" />
              Start Inbound Agent
            </Button>
          </div>
        </div>

        {/* User Details */}
        <Card className="glass-card p-6">
          <h3 className="text-xl font-semibold text-primary mb-4">User Details</h3>
          <div className="grid grid-cols-3 gap-8">
            <div>
              <p className="text-sm text-muted-foreground mb-2">Category</p>
              <p className="text-base font-medium text-foreground">Company</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-2">Department/Body</p>
              <p className="text-base font-medium text-foreground">jhh</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-2">Account Type</p>
              <p className="text-base font-medium text-foreground">Demo Account</p>
            </div>
          </div>
        </Card>

        {/* AI Customization */}
        <Card className="glass-card p-6">
          <div className="flex items-center gap-2 mb-6">
            <SettingsIcon className="w-5 h-5 text-primary" />
            <h3 className="text-xl font-semibold text-primary">AI Customization</h3>
          </div>

          {/* AI Agent Name */}
          <div className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-3">AI Agent Name</p>
              {isEditingName ? (
                <div className="flex items-center gap-2">
                  <Input
                    value={agentName}
                    onChange={(e) => setAgentName(e.target.value)}
                    className="max-w-md"
                  />
                  <Button
                    size="sm"
                    onClick={() => {
                      setIsEditingName(false);
                      toast.success("Agent name updated");
                    }}
                  >
                    Save
                  </Button>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <p className="text-lg font-medium text-foreground">{agentName}</p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsEditingName(true)}
                    className="h-8 w-8 p-0"
                  >
                    <Edit2 className="w-4 h-4" />
                  </Button>
                </div>
              )}
            </div>

            {/* Agent Description */}
            <div>
              <p className="text-sm text-muted-foreground mb-3">Agent Description</p>
              {isEditingDescription ? (
                <div className="space-y-2">
                  <Textarea
                    value={agentDescription}
                    onChange={(e) => setAgentDescription(e.target.value)}
                    rows={3}
                    className="resize-none"
                  />
                  <Button
                    size="sm"
                    onClick={() => {
                      setIsEditingDescription(false);
                      toast.success("Description updated");
                    }}
                  >
                    Save
                  </Button>
                </div>
              ) : (
                <div className="flex items-start gap-3 p-4 bg-muted/30 rounded-lg">
                  <p className="text-sm text-foreground flex-1">{agentDescription}</p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsEditingDescription(true)}
                    className="h-8 w-8 p-0"
                  >
                    <Edit2 className="w-4 h-4" />
                  </Button>
                </div>
              )}
            </div>

            {/* Human-in-the-Loop Escalation */}
            <div className="pt-4">
              <div className="flex items-center gap-2 mb-3">
                <p className="text-sm text-muted-foreground">Human-in-the-Loop Escalation</p>
                <Info className="w-4 h-4 text-muted-foreground" />
              </div>
              <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors cursor-pointer">
                <UserPlus className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Add Human Expert</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Upload Documents */}
        <Card className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold text-primary mb-2">Upload Documents</h3>
              <p className="text-sm text-muted-foreground">
                Upload PDFs, Word docs, and other files for AI knowledge base
              </p>
            </div>
            <Button
              onClick={() => navigate("/knowledge-base")}
              className="gap-2"
            >
              <Upload className="w-4 h-4" />
              Upload
            </Button>
          </div>
        </Card>

        {/* Connect Database */}
        <Card className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold text-primary mb-2">Connect Database</h3>
              <p className="text-sm text-muted-foreground">
                Connect PostgreSQL, Excel, CSV, or external data sources
              </p>
            </div>
            <Button
              onClick={() => navigate("/databases")}
              className="gap-2"
            >
              <Database className="w-4 h-4" />
              Connect
            </Button>
          </div>
        </Card>

        {/* AI Tools & Capabilities */}
        <Card className="glass-card p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-primary mb-2">AI Tools & Capabilities</h3>
            <p className="text-sm text-muted-foreground">
              Toggle tools on/off to control what the AI agent can access during calls.
            </p>
          </div>

          <div className="space-y-4">
            {/* Knowledge Query Tool */}
            <div className="flex items-center justify-between p-4 bg-muted/20 rounded-lg border border-border">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-foreground">Knowledge Query Tool</h4>
                  <Badge variant="secondary" className="text-xs">BASE</Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  Query the knowledge base for information
                </p>
              </div>
              <Switch
                checked={tools.knowledgeQuery}
                onCheckedChange={() => handleToggleTool("knowledgeQuery")}
              />
            </div>

            {/* End Call Tool */}
            <div className="flex items-center justify-between p-4 bg-muted/20 rounded-lg border border-border">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-foreground">End Call Tool</h4>
                  <Badge variant="secondary" className="text-xs">BASE</Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  End the current call gracefully
                </p>
              </div>
              <Switch
                checked={tools.endCall}
                onCheckedChange={() => handleToggleTool("endCall")}
              />
            </div>

            {/* Complain ticket data */}
            <div className="flex items-center justify-between p-4 bg-muted/20 rounded-lg border border-border">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-foreground">Complain ticket data</h4>
                  <Badge className="text-xs bg-purple-500/10 text-purple-600 border-purple-500/30">
                    DATABASE
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground line-clamp-1">
                  Read: This database contains complaint ticket information, including the "name of person" (string), ...
                </p>
              </div>
              <Switch
                checked={tools.complainTicket}
                onCheckedChange={() => handleToggleTool("complainTicket")}
              />
            </div>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Index;
