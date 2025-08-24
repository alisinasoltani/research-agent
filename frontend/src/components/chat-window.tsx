// src/components/chat-window.tsx
"use client";

import { useEffect, useState, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Composer } from "@/components/composer";
import { MessageBubble } from "@/components/message-bubble";
import { useScrollPosition } from "@/hooks/useScrollPosition";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/apiClient";
import { useSession } from "next-auth/react";
import { useWsStream, ChatMessage } from "@/hooks/useWsStream";
import { useChat } from "@/app/context/chat-context";
import { Card } from "@/components/ui/card";
import { TerminalSquare } from "lucide-react";
import { Button } from "./ui/button";

interface Conversation {
  thread_id: string;
  messages: ChatMessage[];
}

export function ChatWindow() {
  const { currentThreadId, isDevPanelOpen, setIsDevPanelOpen } = useChat();
  const { data: session } = useSession();
  const scrollRef = useScrollPosition(currentThreadId);
  const devPanelEventsRef = useRef<any[]>([]);

  // Use the WebSocket streaming hook, which now handles its own data fetching
  const { messages, sendMessage, isLoading } = useWsStream({
    threadId: currentThreadId,
    onEvent: (event) => {
      // Append raw events to the Dev Panel log
      devPanelEventsRef.current = [...devPanelEventsRef.current, event];
    },
  });
  
  const initialMessage = { id: "initial", content: "Hello! How can I help you?", isUser: false };
  const displayMessages = messages.length > 0 ? messages : [initialMessage];

  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1 px-4 py-8" ref={scrollRef}>
        <div className="flex flex-col space-y-4">
          {isLoading && (
            <p className="text-center text-sm text-gray-500">Loading conversation history...</p>
          )}
          {displayMessages.map((message, index) => (
            <MessageBubble key={message.id || index} message={message} />
          ))}
        </div>
      </ScrollArea>
      {/* Dev Panel */}
      <Card
        className={`fixed bottom-4 right-4 z-40 transition-transform duration-300 ease-in-out ${
          isDevPanelOpen ? "translate-x-0" : "translate-x-[calc(100%+16px)]"
        } w-80 max-h-96 flex flex-col`}
      >
        <div className="flex items-center justify-between border-b p-3">
          <h3 className="text-sm font-semibold flex items-center gap-1">
            <TerminalSquare size={16} /> Dev Panel
          </h3>
          <Button variant="ghost" size="sm" onClick={() => setIsDevPanelOpen(false)}>
            Close
          </Button>
        </div>
        <ScrollArea className="flex-1 text-sm p-3 overflow-y-scroll">
          <div className="space-y-2">
            {devPanelEventsRef.current.map((event, index) => (
              <pre key={index} className="overflow-x-auto whitespace-pre-wrap rounded-md bg-gray-100 p-2 text-xs dark:bg-gray-700">
                {JSON.stringify(event, null, 2)}
              </pre>
            ))}
          </div>
        </ScrollArea>
      </Card>
      <div className="border-t p-4">
        <Composer onSendMessage={sendMessage} />
      </div>
    </div>
  );
}