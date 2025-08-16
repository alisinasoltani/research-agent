// src/components/message-bubble.tsx
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  isStreaming?: boolean;
  isError?: boolean;
  originalPrompt?: string; // Add this to store the original prompt for retries
}

interface MessageBubbleProps {
  message: Message;
  onRetry?: (messageId: string, originalPrompt: string) => void;
}

// Simple loading component to indicate streaming
function MessageBubbleLoading() {
  return (
    <div className="flex space-x-1">
      <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400"></div>
      <div
        className="h-2 w-2 animate-bounce rounded-full bg-gray-400"
        style={{ animationDelay: "0.15s" }}
      ></div>
      <div
        className="h-2 w-2 animate-bounce rounded-full bg-gray-400"
        style={{ animationDelay: "0.3s" }}
      ></div>
    </div>
  );
}


export function MessageBubble({ message, onRetry }: MessageBubbleProps) {
  return (
    <div
      className={cn(
        "flex",
        message.isUser ? "justify-end" : "justify-start"
      )}
    >
      <Card
        className={cn(
          "max-w-md w-fit rounded-lg",
          message.isUser
            ? "bg-primary text-primary-foreground"
            : "bg-secondary text-secondary-foreground",
          message.isError ? "bg-red-500 text-white" : ""
        )}
      >
        <CardContent className="p-4">
          {message.isError ? (
            <div className="flex flex-col items-start space-y-2">
              <p>{message.content}</p>
              {onRetry && message.originalPrompt && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onRetry(message.id, message.originalPrompt!)}
                >
                  Retry
                </Button>
              )}
            </div>
          ) : message.isStreaming ? (
            <MessageBubbleLoading />
          ) : (
            <p>{message.content}</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}