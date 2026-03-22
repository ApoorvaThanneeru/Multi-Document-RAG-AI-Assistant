"use client";

import { FileText, Trash2, BookOpen, Loader2 } from "lucide-react";
import type { DocumentInfo } from "@/lib/api";

interface DocumentListProps {
  documents: DocumentInfo[];
  onDelete: (docId: string) => void;
  onSummarize: (docId: string) => void;
  summarizingId: string | null;
}

export default function DocumentList({
  documents,
  onDelete,
  onSummarize,
  summarizingId,
}: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="py-8 text-center text-sm text-slate-500 dark:text-slate-400">
        No documents uploaded yet.
        <br />
        Upload a PDF to get started.
      </div>
    );
  }

  return (
    <ul className="space-y-1.5">
      {documents.map((doc) => (
        <li
          key={doc.id}
          className="group flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-slate-100 dark:hover:bg-slate-800"
        >
          <FileText className="h-4 w-4 shrink-0 text-blue-500" />
          <div className="min-w-0 flex-1">
            <p className="truncate font-medium text-slate-800 dark:text-slate-200">
              {doc.name}
            </p>
            <p className="text-xs text-slate-500">{doc.num_chunks} chunks</p>
          </div>
          <div className="flex shrink-0 gap-1 opacity-0 transition-opacity group-hover:opacity-100">
            <button
              onClick={() => onSummarize(doc.id)}
              disabled={summarizingId === doc.id}
              className="rounded p-1 text-slate-400 hover:bg-blue-100 hover:text-blue-600 dark:hover:bg-blue-900/40 dark:hover:text-blue-400"
              title="Summarize"
            >
              {summarizingId === doc.id ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <BookOpen className="h-3.5 w-3.5" />
              )}
            </button>
            <button
              onClick={() => onDelete(doc.id)}
              className="rounded p-1 text-slate-400 hover:bg-red-100 hover:text-red-600 dark:hover:bg-red-900/40 dark:hover:text-red-400"
              title="Delete"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
