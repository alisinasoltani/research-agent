// src/components/chat-layout.tsx
"use client";

import { useState } from "react";
import { Sidebar } from "@/components/sidebar";
import { ChatWindow } from "@/components/chat-window";
import { AuthButton } from "@/components/auth-button";
import { Button } from "@/components/ui/button";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { useChat } from "@/app/context/chat-context";

export function ChatLayout() {
  const { isSidebarOpen, setIsSidebarOpen, isDevPanelOpen, setIsDevPanelOpen } = useChat();

  return (
    <div className="flex min-h-screen">
      {/* Sidebar Section */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex-shrink-0 transform transition-transform duration-300 ease-in-out lg:static ${
          isSidebarOpen ? "translate-x-0 w-64 border-r" : "-translate-x-full w-0"
        } bg-gray-100 dark:bg-gray-800`}
      >
        <Sidebar />
        {/* Sidebar Toggle Button */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-full rounded-l-none border-l-0 lg:hidden"
        >
          {isSidebarOpen ? <PanelLeftClose /> : <PanelLeftOpen />}
        </Button>
      </aside>

      {/* Main Content Area */}
      <main className={`flex-1 flex flex-col transition-all duration-300 ease-in-out ${isSidebarOpen ? "lg:ml-64" : "lg:ml-0"}`}>
        {/* Main Header */}
        <header className="flex h-16 items-center justify-between border-b bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
          <div className="flex items-center">
            {!isSidebarOpen && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="mr-2"
              >
                <PanelLeftOpen />
              </Button>
            )}
            <h1 className="text-xl font-bold">
              {"New Chat"}
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              onClick={() => setIsDevPanelOpen(!isDevPanelOpen)}
            >
              Dev Panel
            </Button>
            <AuthButton />
          </div>
        </header>

        {/* Chat Window and Composer */}
        <div className="flex-1 overflow-auto p-4">
          <ChatWindow />
        </div>

      </main>

    </div>
  );
}
