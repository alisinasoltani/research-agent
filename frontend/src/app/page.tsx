// src/app/page.tsx
"use client";

import { useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { signIn } from "next-auth/react";
import { ChatLayout } from "@/components/chat-layout";
import { ChatProvider } from "./context/chat-context";

export default function HomePage() {
  const { data: session, status } = useSession();

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        Loading...
      </div>
    );
  }

  if (!session) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-4 text-center">
        <h1 className="text-3xl font-bold">Agentic Chat Client</h1>
        <p className="mt-2 text-lg text-gray-600">
          Please sign in to continue.
        </p>
        <div className="mt-6 flex flex-col space-y-4">
          <Button onClick={() => signIn("google")} className="w-full">
            Sign In with Google
          </Button>
          <Button onClick={() => signIn("github")} className="w-full">
            Sign In with GitHub
          </Button>
        </div>
      </div>
    );
  }

  // Wrap the ChatLayout with the ChatProvider
  return (
    <ChatProvider>
      <ChatLayout />
    </ChatProvider>
  );
}
