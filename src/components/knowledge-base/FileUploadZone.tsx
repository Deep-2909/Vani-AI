import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, X, Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status: "uploading" | "processing" | "complete" | "error";
  progress: number;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileUploadZone() {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const processFile = useCallback((file: File) => {
    const uploadedFile: UploadedFile = {
      id: `file-${Date.now()}-${Math.random()}`,
      name: file.name,
      size: file.size,
      status: "uploading",
      progress: 0,
    };

    setFiles((prev) => [...prev, uploadedFile]);

    // Simulate upload progress
    let progress = 0;
    const uploadInterval = setInterval(() => {
      progress += Math.random() * 20;
      if (progress >= 100) {
        progress = 100;
        clearInterval(uploadInterval);

        setFiles((prev) =>
          prev.map((f) =>
            f.id === uploadedFile.id
              ? { ...f, status: "processing", progress: 100 }
              : f
          )
        );

        // Simulate processing
        setTimeout(() => {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === uploadedFile.id ? { ...f, status: "complete" } : f
            )
          );
        }, 1500);
      } else {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === uploadedFile.id ? { ...f, progress: Math.min(progress, 99) } : f
          )
        );
      }
    }, 200);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const droppedFiles = Array.from(e.dataTransfer.files);
      droppedFiles.forEach(processFile);
    },
    [processFile]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFiles = Array.from(e.target.files || []);
      selectedFiles.forEach(processFile);
    },
    [processFile]
  );

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <motion.div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        animate={{
          borderColor: isDragging ? "hsl(var(--primary))" : "hsl(var(--border))",
          backgroundColor: isDragging
            ? "hsl(var(--primary) / 0.05)"
            : "transparent",
        }}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-8 text-center transition-colors",
          isDragging && "ring-2 ring-primary/20"
        )}
      >
        <input
          type="file"
          accept=".pdf,.doc,.docx,.txt,.md"
          multiple
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        <div className="space-y-4">
          <motion.div
            animate={{ scale: isDragging ? 1.1 : 1 }}
            className="w-16 h-16 mx-auto rounded-2xl bg-primary/10 flex items-center justify-center"
          >
            <Upload
              className={cn(
                "w-8 h-8 transition-colors",
                isDragging ? "text-primary" : "text-muted-foreground"
              )}
            />
          </motion.div>

          <div>
            <p className="text-foreground font-medium">
              {isDragging ? "Drop files here" : "Drag and drop files here"}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              or click to browse • PDF, DOC, DOCX, TXT, MD
            </p>
          </div>

          <Button
            variant="outline"
            className="pointer-events-none"
          >
            Select Files
          </Button>
        </div>
      </motion.div>

      {/* File List */}
      <AnimatePresence mode="popLayout">
        {files.map((file) => (
          <motion.div
            key={file.id}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="flex items-center gap-4 p-4 rounded-xl bg-muted/30 border border-border"
          >
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <FileText className="w-5 h-5 text-primary" />
            </div>

            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">
                {file.name}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-muted-foreground">
                  {formatFileSize(file.size)}
                </span>
                {file.status === "uploading" && (
                  <span className="text-xs text-primary">
                    Uploading... {Math.round(file.progress)}%
                  </span>
                )}
                {file.status === "processing" && (
                  <span className="text-xs text-warning">Processing...</span>
                )}
                {file.status === "complete" && (
                  <span className="text-xs text-success">Complete</span>
                )}
              </div>

              {file.status === "uploading" && (
                <div className="mt-2 h-1 rounded-full bg-muted overflow-hidden">
                  <motion.div
                    className="h-full bg-primary"
                    initial={{ width: 0 }}
                    animate={{ width: `${file.progress}%` }}
                    transition={{ duration: 0.2 }}
                  />
                </div>
              )}
            </div>

            <div className="flex items-center gap-2">
              {file.status === "uploading" && (
                <Loader2 className="w-4 h-4 text-primary animate-spin" />
              )}
              {file.status === "processing" && (
                <Loader2 className="w-4 h-4 text-warning animate-spin" />
              )}
              {file.status === "complete" && (
                <Check className="w-4 h-4 text-success" />
              )}

              <Button
                size="icon"
                variant="ghost"
                onClick={() => removeFile(file.id)}
                className="h-8 w-8 text-muted-foreground hover:text-destructive"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
