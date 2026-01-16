import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
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
  Upload,
  Database,
} from "lucide-react";
import { toast } from "sonner";
import { getAgentConfig, updateAgentConfig, startInboundAgent, startOutboundCalling } from "@/lib/api";

const Index = () => {
  const navigate = useNavigate();
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
