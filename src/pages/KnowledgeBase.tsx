import { motion } from "framer-motion";
import { BookOpen, FileText, Search, Trash2 } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { FileUploadZone } from "@/components/knowledge-base/FileUploadZone";
import { SyncStatusIndicator } from "@/components/knowledge-base/SyncStatusIndicator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const mockDocuments = [
  { id: "1", name: "Product Manual v2.1.pdf", size: "2.4 MB", vectors: 1247, uploadedAt: "2 days ago" },
  { id: "2", name: "FAQ Database.docx", size: "856 KB", vectors: 523, uploadedAt: "1 week ago" },
  { id: "3", name: "Troubleshooting Guide.pdf", size: "5.1 MB", vectors: 2891, uploadedAt: "2 weeks ago" },
  { id: "4", name: "Customer Scripts.txt", size: "124 KB", vectors: 89, uploadedAt: "3 weeks ago" },
  { id: "5", name: "Return Policy 2024.pdf", size: "312 KB", vectors: 156, uploadedAt: "1 month ago" },
];

export default function KnowledgeBase() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row md:items-center md:justify-between gap-4"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Knowledge Base</h1>
              <p className="text-muted-foreground">
                Manage documents for RAG-powered responses
              </p>
            </div>
          </div>
        </motion.div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-2 glass-card-elevated p-6"
          >
            <h3 className="font-semibold text-foreground mb-4">Upload Documents</h3>
            <FileUploadZone />
          </motion.div>

          {/* Sync Status */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <SyncStatusIndicator />
          </motion.div>
        </div>

        {/* Documents List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card-elevated"
        >
          <div className="p-6 border-b border-border flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h3 className="font-semibold text-foreground">Indexed Documents</h3>
              <p className="text-sm text-muted-foreground">
                {mockDocuments.length} documents in knowledge base
              </p>
            </div>

            <div className="relative w-full md:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search documents..."
                className="pl-10 bg-muted/30 border-border"
              />
            </div>
          </div>

          <div className="divide-y divide-border">
            {mockDocuments.map((doc, index) => (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.05 }}
                className="p-4 flex items-center justify-between hover:bg-muted/20 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">{doc.name}</p>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <span>{doc.size}</span>
                      <span>•</span>
                      <span>{doc.vectors.toLocaleString()} vectors</span>
                      <span>•</span>
                      <span>{doc.uploadedAt}</span>
                    </div>
                  </div>
                </div>

                <Button
                  variant="ghost"
                  size="icon"
                  className="text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
}
