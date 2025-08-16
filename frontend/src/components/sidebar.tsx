// src/components/sidebar.tsx
"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useChat } from "@/app/context/chat-context";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/apiClient";
import { useSession } from "next-auth/react";

interface ConversationHistory {
  thread_id: string;
  initial_prompt: string;
}

export function Sidebar() {
  const { currentThreadId, setCurrentThreadId, isSidebarOpen } = useChat();
  const { data: session } = useSession();

  // Use TanStack Query to fetch conversation history
  const { data: conversations, isLoading } = useQuery<ConversationHistory[]>({
    queryKey: ["history", session?.user?.id],
    queryFn: () => {
      if (!session) {
        return Promise.resolve([]);
      }
      return apiClient<ConversationHistory[]>(`/history/${session.user.id}`, "GET", session);
    },
    enabled: !!session, // Only run the query if a session exists
  });

  return (
    <div className="flex h-full flex-col p-4">
      <h2 className="text-2xl font-bold mb-4">Conversations</h2>
      <Button onClick={() => setCurrentThreadId(null)} className="mb-4 w-full">
        <Plus className="mr-2 h-4 w-4" /> New Chat
      </Button>
      <div className="flex-1 overflow-y-auto space-y-2">
        {isLoading && (
          <p className="text-center text-sm text-gray-500">Loading history...</p>
        )}
        {conversations?.map((conv) => (
          <Card
            key={conv.thread_id}
            onClick={() => setCurrentThreadId(conv.thread_id)}
            className={`cursor-pointer transition-colors hover:bg-gray-200 dark:hover:bg-gray-700 ${
              currentThreadId === conv.thread_id ? "border-primary" : ""
            }`}
          >
            <CardContent className="p-4">
              <p className="truncate">{conv.initial_prompt}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
