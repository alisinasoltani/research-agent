// src/app/context/chat-context.tsx
"use client";

import React, { createContext, useContext, useState, useMemo } from "react";

interface ChatContextType {
  currentThreadId: string | null;
  setCurrentThreadId: (id: string | null) => void;
  isSidebarOpen: boolean;
  setIsSidebarOpen: (isOpen: boolean) => void;
  isDevPanelOpen: boolean;
  setIsDevPanelOpen: (isOpen: boolean) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isDevPanelOpen, setIsDevPanelOpen] = useState(false);

  // Use useMemo to prevent unnecessary re-renders of the context value
  const value = useMemo(
    () => ({
      currentThreadId,
      setCurrentThreadId,
      isSidebarOpen,
      setIsSidebarOpen,
      isDevPanelOpen,
      setIsDevPanelOpen,
    }),
    [currentThreadId, isSidebarOpen, isDevPanelOpen]
  );

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
}
