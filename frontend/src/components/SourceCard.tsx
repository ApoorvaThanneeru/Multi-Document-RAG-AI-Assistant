"use client";

import { FileText } from "lucide-react";
import type { SourceInfo } from "@/lib/api";

interface SourceCardProps {
  source: SourceInfo;
}

export default function SourceCard({ source }: SourceCardProps) {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm dark:border-slate-700 dark:bg-slate-800/50">
      <FileText className="mt-0.5 h-4 w-4 shrink-0 text-blue-500" />
      <div className="min-w-0">
        <p className="font-medium text-slate-900 dark:text-slate-100">
          {source.document}
          <span className="ml-2 text-xs font-normal text-slate-500">
            Page {source.page}
          </span>
        </p>
        <p className="mt-1 line-clamp-2 text-slate-600 dark:text-slate-400">
          {source.snippet}
        </p>
      </div>
    </div>
  );
}
