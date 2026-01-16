import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Database, FileSpreadsheet, FileText, Link2, Key, Shield, Upload } from "lucide-react";
import { cn } from "@/lib/utils";

type SourceType = "supabase" | "excel" | "csv" | "googlesheets";

interface LinkDataSourceDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSync: (data: any) => void;
}

export const LinkDataSourceDialog = ({
  open,
  onOpenChange,
  onSync,
}: LinkDataSourceDialogProps) => {
  const [selectedType, setSelectedType] = useState<SourceType>("supabase");
  const [datasetName, setDatasetName] = useState("");
  const [readAccess, setReadAccess] = useState(true);
  const [writeAccess, setWriteAccess] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  // Supabase fields
  const [supabaseData, setSupabaseData] = useState({
    accessToken: "",
    host: "",
    database: "postgres",
    user: "postgres",
    password: "",
    port: "5432",
    targetTable: "",
  });

  // Google Sheets fields
  const [sheetsUrl, setSheetsUrl] = useState("");

  const sourceTypes = [
    {
      id: "supabase" as SourceType,
      label: "SUPABASE",
      icon: Database,
      description: "Connect to Supabase database",
    },
    {
      id: "excel" as SourceType,
      label: "EXCEL",
      icon: FileSpreadsheet,
      description: "Upload Excel file (.xlsx, .xls)",
    },
    {
      id: "csv" as SourceType,
      label: "CSV",
      icon: FileText,
      description: "Upload CSV file",
    },
    {
      id: "googlesheets" as SourceType,
      label: "GOOGLE SHEETS",
      icon: Link2,
      description: "Connect Google Spreadsheet",
    },
  ];

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
    }
  };

  const handleSync = () => {
    const data = {
      type: selectedType,
      datasetName,
      readAccess,
      writeAccess,
      ...(selectedType === "supabase" && supabaseData),
      ...(selectedType === "googlesheets" && { sheetsUrl }),
      ...(selectedType === "excel" || selectedType === "csv" ? { file: uploadedFile } : {}),
    };
    onSync(data);
    handleDiscard();
  };

  const handleDiscard = () => {
    setDatasetName("");
    setReadAccess(true);
    setWriteAccess(false);
    setUploadedFile(null);
    setSupabaseData({
      accessToken: "",
      host: "",
      database: "postgres",
      user: "postgres",
      password: "",
      port: "5432",
      targetTable: "",
    });
    setSheetsUrl("");
    onOpenChange(false);
  };

  const isFormValid = () => {
    if (!datasetName) return false;
    if (selectedType === "supabase") {
      return (
        supabaseData.accessToken &&
        supabaseData.host &&
        supabaseData.database &&
        supabaseData.user &&
        supabaseData.password &&
        supabaseData.targetTable
      );
    }
    if (selectedType === "googlesheets") {
      return sheetsUrl;
    }
    if (selectedType === "excel" || selectedType === "csv") {
      return uploadedFile !== null;
    }
    return false;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Database className="w-6 h-6 text-primary" />
            </div>
            <div>
              <DialogTitle className="text-2xl">Link Data Source</DialogTitle>
              <DialogDescription className="text-base">
                Empower Vani AI with live external data
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Source Type Selection */}
          <div className="space-y-3">
            <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              SELECT ENVIRONMENT
            </Label>
            <div className="grid grid-cols-4 gap-3">
              {sourceTypes.map((type) => {
                const Icon = type.icon;
                const isSelected = selectedType === type.id;
                return (
                  <button
                    key={type.id}
                    onClick={() => setSelectedType(type.id)}
                    className={cn(
                      "p-4 rounded-xl border-2 transition-all flex flex-col items-center justify-center gap-2 hover:border-primary/50",
                      isSelected
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-card border-border"
                    )}
                  >
                    <Icon className="w-6 h-6" />
                    <span className="text-xs font-semibold">{type.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Dataset Display Name */}
          <div className="space-y-2">
            <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              DATASET DISPLAY NAME
            </Label>
            <Input
              placeholder="e.g. MCD_Garbage_Schedule"
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              className="bg-muted/30"
            />
          </div>

          {/* Conditional Forms Based on Source Type */}
          {selectedType === "supabase" && (
            <div className="space-y-4">
              {/* Management Access Token */}
              <div className="space-y-2 p-4 bg-primary/5 border border-primary/20 rounded-lg">
                <div className="flex items-center gap-2 text-primary">
                  <Key className="w-4 h-4" />
                  <Label className="text-xs font-semibold uppercase tracking-wider">
                    MANAGEMENT ACCESS TOKEN
                  </Label>
                </div>
                <Input
                  placeholder="sbp_xxxxxxxxxxxxxxxxxxxx"
                  value={supabaseData.accessToken}
                  onChange={(e) =>
                    setSupabaseData({ ...supabaseData, accessToken: e.target.value })
                  }
                  className="bg-background font-mono text-sm"
                />
                <p className="text-xs text-primary">
                  USED TO DEPLOY EDGE FUNCTIONS TO YOUR PROJECT.
                </p>
              </div>

              {/* Connection Details Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-sm text-muted-foreground">Host (db.xxx.supabase.co)</Label>
                  <Input
                    placeholder="db.xxx.supabase.co"
                    value={supabaseData.host}
                    onChange={(e) => setSupabaseData({ ...supabaseData, host: e.target.value })}
                    className="bg-muted/30"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-sm text-muted-foreground">Database</Label>
                  <Input
                    value={supabaseData.database}
                    onChange={(e) =>
                      setSupabaseData({ ...supabaseData, database: e.target.value })
                    }
                    className="bg-muted/30"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-sm text-muted-foreground">User</Label>
                  <Input
                    value={supabaseData.user}
                    onChange={(e) => setSupabaseData({ ...supabaseData, user: e.target.value })}
                    className="bg-muted/30"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-sm text-muted-foreground">DB Password</Label>
                  <Input
                    type="password"
                    placeholder="••••••••••••••••••"
                    value={supabaseData.password}
                    onChange={(e) =>
                      setSupabaseData({ ...supabaseData, password: e.target.value })
                    }
                    className="bg-muted/30"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-sm text-muted-foreground">Port</Label>
                  <Input
                    value={supabaseData.port}
                    onChange={(e) => setSupabaseData({ ...supabaseData, port: e.target.value })}
                    className="bg-muted/30"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-sm text-muted-foreground">Target Table (public.schemes)</Label>
                  <Input
                    placeholder="public.schemes"
                    value={supabaseData.targetTable}
                    onChange={(e) =>
                      setSupabaseData({ ...supabaseData, targetTable: e.target.value })
                    }
                    className="bg-muted/30"
                  />
                </div>
              </div>
            </div>
          )}

          {(selectedType === "excel" || selectedType === "csv") && (
            <div className="space-y-2">
              <Label className="text-sm font-medium">Upload File</Label>
              <div className="relative">
                <input
                  type="file"
                  accept={selectedType === "excel" ? ".xlsx,.xls" : ".csv"}
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  id="file-upload"
                />
                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors cursor-pointer bg-muted/20">
                  <Upload className="w-8 h-8 mx-auto mb-3 text-muted-foreground" />
                  {uploadedFile ? (
                    <p className="text-sm text-foreground font-medium">{uploadedFile.name}</p>
                  ) : (
                    <>
                      <p className="text-sm text-foreground font-medium mb-1">
                        Click to upload or drag and drop
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {selectedType === "excel" ? "Excel files (.xlsx, .xls)" : "CSV files (.csv)"}
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {selectedType === "googlesheets" && (
            <div className="space-y-3">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Link2 className="w-4 h-4 text-primary" />
                  <Label className="text-sm font-medium">Google Spreadsheet URL</Label>
                </div>
                <Input
                  placeholder="https://docs.google.com/spreadsheets/d/..."
                  value={sheetsUrl}
                  onChange={(e) => setSheetsUrl(e.target.value)}
                  className="bg-muted/30"
                />
              </div>
              <div className="p-3 bg-warning/10 border border-warning/30 rounded-lg">
                <p className="text-xs text-warning-foreground">
                  ⚠️ Ensure the sheet is shared with 'Anyone with the link can view'
                </p>
              </div>
            </div>
          )}

          {/* Intelligence Permissions */}
          <div className="space-y-4 p-4 bg-muted/30 border border-border rounded-lg">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-muted-foreground" />
              <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                INTELLIGENCE PERMISSIONS
              </Label>
            </div>

            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <Checkbox
                  id="read-access"
                  checked={readAccess}
                  onCheckedChange={(checked) => setReadAccess(checked as boolean)}
                />
                <div className="space-y-1">
                  <Label htmlFor="read-access" className="font-semibold cursor-pointer">
                    Read Access
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    Allow Vani AI to query this for knowledge.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Checkbox
                  id="write-access"
                  checked={writeAccess}
                  onCheckedChange={(checked) => setWriteAccess(checked as boolean)}
                  disabled={selectedType === "excel" || selectedType === "csv"}
                />
                <div className="space-y-1">
                  <Label
                    htmlFor="write-access"
                    className={cn(
                      "font-semibold cursor-pointer",
                      (selectedType === "excel" || selectedType === "csv") &&
                      "text-muted-foreground"
                    )}
                  >
                    Write Access (Append)
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    Vapi native tool for ticketing/logs.
                    {(selectedType === "excel" || selectedType === "csv") && (
                      <span className="block text-warning mt-1">Not available for files</span>
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t">
          <Button variant="ghost" onClick={handleDiscard} className="uppercase text-muted-foreground">
            Discard
          </Button>
          <Button
            onClick={handleSync}
            disabled={!isFormValid()}
            className="uppercase px-8"
          >
            Sync with Vani AI
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
