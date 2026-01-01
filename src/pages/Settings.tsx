import { useState } from "react";
import { motion } from "framer-motion";
import { Settings as SettingsIcon, Key, Bell, Shield, Volume2, Globe, Save } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { toast } from "@/hooks/use-toast";

const settingsSections = [
  { id: "api", label: "API Keys", icon: Key },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "voice", label: "Voice Settings", icon: Volume2 },
  { id: "security", label: "Security", icon: Shield },
  { id: "localization", label: "Localization", icon: Globe },
];

export default function Settings() {
  const [activeSection, setActiveSection] = useState("api");
  const [vapiKey, setVapiKey] = useState("");
  const [pineconeKey, setPineconeKey] = useState("");
  const [voiceSpeed, setVoiceSpeed] = useState([1.0]);
  const [notifications, setNotifications] = useState({
    callAlerts: true,
    dailyReports: true,
    errorAlerts: true,
    weeklyDigest: false,
  });

  const handleSave = () => {
    toast({
      title: "Settings saved",
      description: "Your changes have been saved successfully.",
    });
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
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <SettingsIcon className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Settings</h1>
              <p className="text-muted-foreground">
                Configure your voice agent and integrations
              </p>
            </div>
          </div>

          <Button onClick={handleSave} className="gap-2 bg-gradient-to-r from-primary to-accent">
            <Save className="w-4 h-4" />
            Save Changes
          </Button>
        </motion.div>

        {/* Settings Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Navigation */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card-elevated p-4 h-fit"
          >
            <nav className="space-y-1">
              {settingsSections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    activeSection === section.id
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                  }`}
                >
                  <section.icon className="w-5 h-5" />
                  <span className="font-medium">{section.label}</span>
                </button>
              ))}
            </nav>
          </motion.div>

          {/* Settings Content */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-3 glass-card-elevated p-6"
          >
            {activeSection === "api" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-4">API Configuration</h3>
                  <p className="text-sm text-muted-foreground mb-6">
                    Manage your API keys for external integrations
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="vapi-key">Vapi API Key</Label>
                    <Input
                      id="vapi-key"
                      type="password"
                      placeholder="vapi_..."
                      value={vapiKey}
                      onChange={(e) => setVapiKey(e.target.value)}
                      className="bg-muted/30 border-border font-mono"
                    />
                    <p className="text-xs text-muted-foreground">
                      Used for voice agent functionality
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="pinecone-key">Pinecone API Key</Label>
                    <Input
                      id="pinecone-key"
                      type="password"
                      placeholder="pc_..."
                      value={pineconeKey}
                      onChange={(e) => setPineconeKey(e.target.value)}
                      className="bg-muted/30 border-border font-mono"
                    />
                    <p className="text-xs text-muted-foreground">
                      Used for knowledge base vector storage
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeSection === "notifications" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-4">Notification Preferences</h3>
                  <p className="text-sm text-muted-foreground mb-6">
                    Configure how you want to be notified
                  </p>
                </div>

                <div className="space-y-4">
                  {Object.entries(notifications).map(([key, value]) => (
                    <div
                      key={key}
                      className="flex items-center justify-between p-4 rounded-lg bg-muted/30 border border-border"
                    >
                      <div>
                        <p className="font-medium text-foreground">
                          {key.replace(/([A-Z])/g, " $1").replace(/^./, (str) => str.toUpperCase())}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          Receive notifications for {key.toLowerCase().replace(/([A-Z])/g, " $1")}
                        </p>
                      </div>
                      <Switch
                        checked={value}
                        onCheckedChange={(checked) =>
                          setNotifications((prev) => ({ ...prev, [key]: checked }))
                        }
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeSection === "voice" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-4">Voice Settings</h3>
                  <p className="text-sm text-muted-foreground mb-6">
                    Configure voice agent behavior
                  </p>
                </div>

                <div className="space-y-6">
                  <div className="space-y-4">
                    <Label>Speech Speed</Label>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-muted-foreground">0.5x</span>
                      <Slider
                        value={voiceSpeed}
                        onValueChange={setVoiceSpeed}
                        min={0.5}
                        max={2}
                        step={0.1}
                        className="flex-1"
                      />
                      <span className="text-sm text-muted-foreground">2x</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Current: {voiceSpeed[0].toFixed(1)}x
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="voice-model">Voice Model</Label>
                    <Input
                      id="voice-model"
                      placeholder="eleven_multilingual_v2"
                      className="bg-muted/30 border-border font-mono"
                      defaultValue="eleven_multilingual_v2"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeSection === "security" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-4">Security Settings</h3>
                  <p className="text-sm text-muted-foreground mb-6">
                    Manage security and access controls
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 rounded-lg bg-muted/30 border border-border">
                    <div>
                      <p className="font-medium text-foreground">Two-Factor Authentication</p>
                      <p className="text-sm text-muted-foreground">
                        Add an extra layer of security
                      </p>
                    </div>
                    <Switch />
                  </div>

                  <div className="flex items-center justify-between p-4 rounded-lg bg-muted/30 border border-border">
                    <div>
                      <p className="font-medium text-foreground">Call Recording Encryption</p>
                      <p className="text-sm text-muted-foreground">
                        Encrypt all stored recordings
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </div>
              </div>
            )}

            {activeSection === "localization" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-4">Localization</h3>
                  <p className="text-sm text-muted-foreground mb-6">
                    Language and regional settings
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="language">Primary Language</Label>
                    <Input
                      id="language"
                      defaultValue="English (US)"
                      className="bg-muted/30 border-border"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="timezone">Timezone</Label>
                    <Input
                      id="timezone"
                      defaultValue="America/New_York (EST)"
                      className="bg-muted/30 border-border"
                    />
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </DashboardLayout>
  );
}
