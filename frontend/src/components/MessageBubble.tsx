"use client";

import ReactMarkdown from "react-markdown";
import { User, Bot } from "lucide-react";
import SourceCard from "./SourceCard";
import type { SourceInfo } from "@/lib/api";

export interface MessageData {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceInfo[];
}

interface MessageBubbleProps {
  message: MessageData;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-200"
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      <div className={`max-w-[80%] space-y-2 ${isUser ? "text-right" : ""}`}>
        <div
          className={`inline-block rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
            isUser
              ? "bg-blue-600 text-white"
              : "bg-white text-slate-800 shadow-sm ring-1 ring-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:ring-slate-700"
          }`}
        >
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="space-y-1.5 text-left">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
              Sources:
            </p>
            {message.sources.map((src, i) => (
              <SourceCard key={`${src.document}-${src.page}-${i}`} source={src} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
