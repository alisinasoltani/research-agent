// src/components/composer.tsx
"use client";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";
import { useDraft } from "@/hooks/useDraft";
import { useChat } from "@/app/context/chat-context";

interface ComposerProps {
  onSendMessage: (message: string) => void;
}

export function Composer({ onSendMessage }: ComposerProps) {
  const { currentThreadId } = useChat();
  const { draft, setDraft } = useDraft(currentThreadId);

  const handleSendMessage = () => {
    if (draft.trim()) {
      onSendMessage(draft);
      setDraft("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex w-full items-center space-x-2">
      <Textarea
        placeholder="Type your message..."
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={handleKeyPress}
        className="flex-1 resize-none"
      />
      <Button onClick={handleSendMessage} disabled={!draft.trim()}>
        <Send className="h-4 w-4" />
      </Button>
    </div>
  );
}
