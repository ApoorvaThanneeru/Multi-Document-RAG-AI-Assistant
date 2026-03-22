"use client";

import { useState, useEffect, useCallback } from "react";
import { MessageSquarePlus, PanelLeftClose, PanelLeft } from "lucide-react";
import toast from "react-hot-toast";
import ChatWindow from "@/components/ChatWindow";
import FileUpload from "@/components/FileUpload";
import DocumentList from "@/components/DocumentList";
import type { MessageData } from "@/components/MessageBubble";
import {
  sendMessage,
  getDocuments,
  deleteDocument,
  summarizeDocument,
} from "@/lib/api";
import type { DocumentInfo, ChatMessage, UploadResponse } from "@/lib/api";

export default function Home() {
  const [messages, setMessages] = useState<MessageData[]>([]);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [summarizingId, setSummarizingId] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch {
      // Silently fail on initial load if backend isn't up yet
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleSendMessage = async (question: string) => {
    const userMsg: MessageData = {
      id: `user-${Date.now()}`,
      role: "user",
      content: question,
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const chatHistory: ChatMessage[] = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await sendMessage(question, chatHistory);

      const botMsg: MessageData = {
        id: `bot-${Date.now()}`,
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorMsg: MessageData = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content:
          err instanceof Error
            ? `Sorry, an error occurred: ${err.message}`
            : "Sorry, something went wrong. Please try again.",
      };
      setMessages((prev) => [...prev, errorMsg]);
      toast.error("Failed to get response");
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadComplete = (result: UploadResponse) => {
    toast.success(result.message);
    fetchDocuments();
  };

  const handleDeleteDocument = async (docId: string) => {
    try {
      await deleteDocument(docId);
      toast.success(`Deleted "${docId}"`);
      fetchDocuments();
    } catch {
      toast.error("Failed to delete document");
    }
  };

  const handleSummarize = async (docId: string) => {
    setSummarizingId(docId);
    try {
      const result = await summarizeDocument(docId);
      const summaryMsg: MessageData = {
        id: `summary-${Date.now()}`,
        role: "assistant",
        content: `**Summary of ${result.document}:**\n\n${result.summary}`,
      };
      setMessages((prev) => [...prev, summaryMsg]);
      toast.success("Summary generated");
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to summarize document"
      );
    } finally {
      setSummarizingId(null);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside
        className={`flex flex-col border-r border-slate-200 bg-white transition-all duration-300 dark:border-slate-700 dark:bg-slate-900 ${
          sidebarOpen ? "w-80" : "w-0 overflow-hidden"
        }`}
      >
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-700">
          <h1 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
            Documents
          </h1>
          <button
            onClick={() => setSidebarOpen(false)}
            className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300"
          >
            <PanelLeftClose className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <FileUpload onUploadComplete={handleUploadComplete} />
          <div className="mt-6">
            <DocumentList
              documents={documents}
              onDelete={handleDeleteDocument}
              onSummarize={handleSummarize}
              summarizingId={summarizingId}
            />
          </div>
        </div>
      </aside>

      {/* Main chat area */}
      <main className="flex flex-1 flex-col bg-slate-50 dark:bg-slate-950">
        {/* Top bar */}
        <header className="flex items-center gap-2 border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-700 dark:bg-slate-900">
          {!sidebarOpen && (
            <button
              onClick={() => setSidebarOpen(true)}
              className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300"
            >
              <PanelLeft className="h-4 w-4" />
            </button>
          )}
          <h2 className="flex-1 text-sm font-semibold text-slate-800 dark:text-slate-200">
            RAG Document Chatbot
          </h2>
          <button
            onClick={handleNewChat}
            className="flex items-center gap-1.5 rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700 transition-colors hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            <MessageSquarePlus className="h-3.5 w-3.5" />
            New Chat
          </button>
        </header>

        <div className="flex-1 overflow-hidden">
          <ChatWindow
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>
      </main>
    </div>
  );
}
