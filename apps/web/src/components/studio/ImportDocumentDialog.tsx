'use client';

import { useState, useCallback, useRef } from 'react';
import { Upload, FileText, X, Check, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { apiUpload, ApiError } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

const SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.txt', '.md', '.rtf', '.odt'];
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50 MB

interface ImportedChapter {
  id: string;
  title: string;
  sort_order: number;
  word_count: number;
}

interface ImportDocumentDialogProps {
  projectId: string;
  bookId: string;
  onImported?: (chapters: ImportedChapter[]) => void;
  trigger?: React.ReactNode;
  /** Controlled mode: external open state */
  open?: boolean;
  /** Controlled mode: external open state setter */
  onOpenChange?: (open: boolean) => void;
}

type ImportStatus = 'idle' | 'dragging' | 'uploading' | 'success' | 'error';

export function ImportDocumentDialog({
  projectId,
  bookId,
  onImported,
  trigger,
  open: controlledOpen,
  onOpenChange: controlledOnOpenChange,
}: ImportDocumentDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const isControlled = controlledOpen !== undefined;
  const open = isControlled ? controlledOpen : internalOpen;
  const setOpen = isControlled
    ? (next: boolean) => controlledOnOpenChange?.(next)
    : setInternalOpen;
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<ImportStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [importedChapters, setImportedChapters] = useState<ImportedChapter[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const reset = useCallback(() => {
    setFile(null);
    setStatus('idle');
    setError(null);
    setImportedChapters([]);
  }, []);

  const handleOpenChange = useCallback(
    (next: boolean) => {
      if (!next) reset();
      setOpen(next);
    },
    [reset]
  );

  const validateFile = useCallback((f: File): string | null => {
    const ext = '.' + f.name.split('.').pop()?.toLowerCase();
    if (!SUPPORTED_EXTENSIONS.includes(ext)) {
      return `Unsupported file type: ${ext}. Supported: PDF, DOCX, TXT, MD, RTF, ODT`;
    }
    if (f.size > MAX_FILE_SIZE) {
      return `File too large (${(f.size / 1024 / 1024).toFixed(1)} MB). Maximum: 50 MB`;
    }
    if (f.size === 0) {
      return 'File is empty';
    }
    return null;
  }, []);

  const handleFile = useCallback(
    (f: File) => {
      const err = validateFile(f);
      if (err) {
        setError(err);
        setStatus('error');
        return;
      }
      setFile(f);
      setError(null);
      setStatus('idle');
    },
    [validateFile]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setStatus('idle');
      const dropped = e.dataTransfer.files[0];
      if (dropped) handleFile(dropped);
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setStatus('dragging');
  }, []);

  const handleDragLeave = useCallback(() => {
    setStatus((s) => (s === 'dragging' ? 'idle' : s));
  }, []);

  const handleImport = useCallback(async () => {
    if (!file) return;
    setStatus('uploading');
    setError(null);

    try {
      const chapters = await apiUpload<ImportedChapter[]>(
        `/api/v1/projects/${projectId}/books/${bookId}/import`,
        file
      );
      setImportedChapters(chapters);
      setStatus('success');
      toast({
        title: 'Import complete',
        description: `${chapters.length} chapter${chapters.length !== 1 ? 's' : ''} created from "${file.name}"`,
      });
      onImported?.(chapters);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : 'Failed to import document. Please try again.';
      setError(message);
      setStatus('error');
    }
  }, [file, projectId, bookId, toast, onImported]);

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" size="sm">
            <Upload className="mr-2 h-4 w-4" />
            Import document
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Import document</DialogTitle>
          <DialogDescription>
            Upload a PDF, Word document, or text file. Authora will extract the text and create
            chapters automatically.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Drop zone */}
          {status !== 'success' && (
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                'relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors cursor-pointer',
                status === 'dragging'
                  ? 'border-primary bg-primary/5'
                  : file
                    ? 'border-green-500/50 bg-green-50 dark:bg-green-950/20'
                    : 'border-muted-foreground/25 hover:border-muted-foreground/50'
              )}
            >
              {file ? (
                <div className="flex flex-col items-center gap-2 text-center">
                  <FileText className="h-10 w-10 text-green-600 dark:text-green-400" />
                  <div>
                    <p className="font-medium text-sm">{file.name}</p>
                    <p className="text-xs text-muted-foreground">{formatSize(file.size)}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      setFile(null);
                      setStatus('idle');
                      setError(null);
                    }}
                  >
                    <X className="mr-1 h-3 w-3" />
                    Remove
                  </Button>
                </div>
              ) : (
                <>
                  <Upload className="mb-3 h-8 w-8 text-muted-foreground" />
                  <p className="text-sm font-medium">Drop your file here or click to browse</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    PDF, DOCX, TXT, MD, RTF, ODT — up to 50 MB
                  </p>
                </>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc,.txt,.md,.rtf,.odt"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) handleFile(f);
                }}
              />
            </div>
          )}

          {/* Uploading state */}
          {status === 'uploading' && (
            <div className="flex items-center gap-3 rounded-lg border bg-muted/30 p-4">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
              <div>
                <p className="text-sm font-medium">Importing &quot;{file?.name}&quot;…</p>
                <p className="text-xs text-muted-foreground">
                  Extracting text and creating chapters…
                </p>
              </div>
            </div>
          )}

          {/* Error state */}
          {status === 'error' && error && (
            <div className="flex items-start gap-3 rounded-lg border border-destructive/50 bg-destructive/10 p-4">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />
              <div>
                <p className="text-sm font-medium text-destructive">Import failed</p>
                <p className="text-xs text-destructive/80">{error}</p>
              </div>
            </div>
          )}

          {/* Success state */}
          {status === 'success' && (
            <div className="space-y-3">
              <div className="flex items-start gap-3 rounded-lg border border-green-500/50 bg-green-50 p-4 dark:bg-green-950/20">
                <Check className="mt-0.5 h-5 w-5 shrink-0 text-green-600 dark:text-green-400" />
                <div>
                  <p className="text-sm font-medium text-green-700 dark:text-green-300">
                    Import complete
                  </p>
                  <p className="text-xs text-green-600/80 dark:text-green-400/80">
                    {importedChapters.length} chapter{importedChapters.length !== 1 ? 's' : ''}{' '}
                    created from &quot;{file?.name}&quot;
                  </p>
                </div>
              </div>
              {importedChapters.length > 0 && (
                <div className="max-h-40 overflow-y-auto rounded-lg border">
                  {importedChapters.map((ch) => (
                    <div
                      key={ch.id}
                      className="flex items-center justify-between border-b px-3 py-2 last:border-b-0 text-sm"
                    >
                      <span className="font-medium">{ch.title}</span>
                      <span className="text-xs text-muted-foreground">
                        {ch.word_count.toLocaleString()} words
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <DialogFooter>
          {status === 'success' ? (
            <Button onClick={() => handleOpenChange(false)}>Done</Button>
          ) : (
            <>
              <Button variant="outline" onClick={() => handleOpenChange(false)}>
                Cancel
              </Button>
              <Button onClick={handleImport} disabled={!file || status === 'uploading'}>
                {status === 'uploading' ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Importing…
                  </>
                ) : (
                  'Import'
                )}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
