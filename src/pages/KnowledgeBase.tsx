import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Search, Plus, FileText, Upload, Loader2 } from "lucide-react";
import { getDocuments, uploadDocuments, Document } from "@/lib/api";
import { toast } from "sonner";

const KnowledgeBase = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);

  useEffect(() => {
    const fetchDocs = async () => {
      setIsLoadingDocs(true);
      const response = await getDocuments(searchQuery);
      if (response.data) {
        setDocuments(response.data);
      }
      setIsLoadingDocs(false);
    };
    fetchDocs();
  }, [searchQuery]);

  const filteredDocuments = documents.filter((doc) =>
    doc.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setUploadedFiles(files);
  };

  const handleSync = async () => {
    if (uploadedFiles.length === 0) return;

    setIsUploading(true);

    try {
      const response = await uploadDocuments(uploadedFiles);

      if (response.data) {
        setDocuments([...documents, ...response.data]);
        setIsUploadDialogOpen(false);
        setUploadedFiles([]);
        toast.success(`Successfully synced ${uploadedFiles.length} document(s)`);
      } else {
        toast.error(response.error || "Failed to upload documents");
      }
    } catch (error) {
      toast.error("An error occurred during upload");
    } finally {
      setIsUploading(false);
    }
  };

  const getFileIcon = (type: string) => {
    return <FileText className="w-8 h-8 text-primary" />;
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-primary">Knowledge Base</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Manage and preview documents used by Vani AI for AI reference
            </p>
          </div>
          <Button onClick={() => setIsUploadDialogOpen(true)} className="gap-2">
            <Plus className="w-4 h-4" />
            Sync New Documents
          </Button>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            placeholder="Search documents by name or file type..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-background border-border h-12 text-base"
          />
        </div>

        {/* Documents Grid */}
        {filteredDocuments.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {filteredDocuments.map((doc) => (
              <Card
                key={doc.id}
                className="glass-card p-6 hover:border-primary/50 transition-all cursor-pointer group"
              >
                <div className="flex flex-col items-center text-center space-y-3">
                  {/* File Icon */}
                  <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                    {getFileIcon(doc.type)}
                  </div>

                  {/* File Name */}
                  <div className="w-full">
                    <h3 className="font-medium text-foreground text-sm line-clamp-2 mb-2">
                      {doc.name}
                    </h3>
                    <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
                      <span className="uppercase font-semibold">{doc.type}</span>
                      <span>•</span>
                      <span>{doc.uploadedDate}</span>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="glass-card p-12 text-center">
            <FileText className="w-16 h-16 mx-auto mb-4 text-muted-foreground/30" />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              No documents found
            </h3>
            <p className="text-sm text-muted-foreground mb-6">
              {searchQuery
                ? "Try adjusting your search query"
                : "Upload documents to get started"}
            </p>
            {!searchQuery && (
              <Button onClick={() => setIsUploadDialogOpen(true)} className="gap-2">
                <Plus className="w-4 h-4" />
                Sync New Documents
              </Button>
            )}
          </Card>
        )}
      </div>

      {/* Upload Dialog */}
      <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Sync New Documents</DialogTitle>
            <DialogDescription>
              Upload documents to enhance Vani AI's knowledge base
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="relative">
              <input
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.xlsx,.xls"
                onChange={handleFileUpload}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                id="doc-upload"
              />
              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors cursor-pointer bg-muted/20">
                <Upload className="w-10 h-10 mx-auto mb-3 text-muted-foreground" />
                {uploadedFiles.length > 0 ? (
                  <div>
                    <p className="text-sm text-foreground font-medium mb-2">
                      {uploadedFiles.length} file(s) selected
                    </p>
                    <div className="text-xs text-muted-foreground space-y-1">
                      {uploadedFiles.map((file, index) => (
                        <p key={index}>{file.name}</p>
                      ))}
                    </div>
                  </div>
                ) : (
                  <>
                    <p className="text-sm text-foreground font-medium mb-1">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-muted-foreground">
                      PDF, DOC, TXT, or XLSX files
                    </p>
                  </>
                )}
              </div>
            </div>

            {isUploading && (
              <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
                <div className="flex items-center gap-3">
                  <Loader2 className="w-5 h-5 text-primary animate-spin" />
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      Processing documents...
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Vectorizing and indexing for AI reference
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsUploadDialogOpen(false);
                setUploadedFiles([]);
              }}
              disabled={isUploading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSync}
              disabled={uploadedFiles.length === 0 || isUploading}
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Syncing...
                </>
              ) : (
                "Sync Documents"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
};

export default KnowledgeBase;
