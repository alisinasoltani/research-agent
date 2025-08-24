// src/components/message-bubble.tsx
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import { useState, useEffect } from "react";

// Template import statements for agent profile pictures (replace paths with actual asset locations)
import EleanorPic from "@/../public/images/agents/Eleanor.jpeg";
import IsaacPic from "@/../public/images/agents/Isaac.png";
import LaylaPic from "@/../public/images/agents/Layla.png";
import NovaPic from "@/../public/images/agents/Nova.png";
import FinalSynthesizerPic from "@/../public/images/agents/FinalSynthesizer.png";
import DefaultPic from "@/../public/images/agents/FinalSynthesizer.png";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  isStreaming?: boolean;
  isWaiting?: boolean;
  startTime?: number;
  endTime?: number;
  isError?: boolean;
  originalPrompt?: string;
  agent?: string;
}

interface MessageBubbleProps {
  message: Message;
  onRetry?: (messageId: string, originalPrompt: string) => void;
}

// Map agent names to profile pictures (assuming server sends names like "Eleanor")
// const agentImages: Record<string, string> = {
//   Eleanor: EleanorPic,
//   Isaac: IsaacPic,
//   Layla: LaylaPic,
//   Nova: NovaPic,
//   "Final Synthesizer": FinalSynthesizerPic,
// };
const agentImages: Record<string, string> = {
  Eleanor: "./images/agents/Eleanor.jpeg",
  Isaac: "./images/agents/Isaac.jpeg",
  Layla: "./images/agents/Layla.jpeg",
  Nova: "./images/agents/Nova.jpeg",
  "Final Synthesizer": "./images/agents/FinalSynthesizer.jpeg",
};

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

function Timer({ startTime, endTime }: { startTime: number; endTime?: number }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (endTime) {
      setElapsed(endTime - startTime);
      return;
    }
    const interval = setInterval(() => {
      setElapsed(Date.now() - startTime);
    }, 1000);
    return () => clearInterval(interval);
  }, [startTime, endTime]);

  return <span className="text-sm text-gray-500">({Math.floor(elapsed / 1000)}s)</span>;
}

export function MessageBubble({ message, onRetry }: MessageBubbleProps) {
  const agentImage = message.agent ? agentImages[message.agent] || "./images/agents/FinalSynthesizer.jpeg" : undefined;

  const renderContent = () => {
    if (message.isError) {
      return (
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
      );
    }

    if (message.isWaiting) {
      return <MessageBubbleLoading />;
    }

    let renderedContent;
    try {
      const jsonContent = JSON.parse(message.content);
      if (typeof jsonContent === "object" && jsonContent !== null) {
        if (jsonContent.summary && Array.isArray(jsonContent.ideas)) {
          renderedContent = (
            <>
              <ReactMarkdown>{jsonContent.summary}</ReactMarkdown>
              <ul className="list-disc pl-5 space-y-4">
                {jsonContent.ideas.map((item: { idea: string; description: string }, index: number) => (
                  <li key={index}>
                    <strong className="block mb-1">{item.idea}</strong>
                    <ReactMarkdown>{item.description}</ReactMarkdown>
                  </li>
                ))}
              </ul>
            </>
          );
        } else {
          renderedContent = Object.entries(jsonContent).map(([key, value]) => (
            <div key={key} className="mb-2">
              <h4 className="font-bold">{key}</h4>
              <ReactMarkdown>{String(value)}</ReactMarkdown>
            </div>
          ));
        }
      } else {
        renderedContent = <div className="prose prose-invert max-w-none break-words">
  <ReactMarkdown>{message.content}</ReactMarkdown>
</div>;
      }
    } catch (e) {
      renderedContent = <div className="prose prose-invert max-w-none break-words">
  <ReactMarkdown>{message.content}</ReactMarkdown>
</div>;
    }

    return (
      <div className="flex items-center gap-2">
        {renderedContent}
        {message.isStreaming && <MessageBubbleLoading />}
      </div>
    );
  };

  return (
    <div className={cn("flex", message.isUser ? "justify-end" : "justify-start")}>
      <Card
        className={cn(
          "max-w-md w-fit rounded-lg relative",
          message.isUser
            ? "bg-primary text-primary-foreground"
            : "bg-secondary text-secondary-foreground",
          message.isError ? "bg-red-500 text-white" : ""
        )}
      >
        {!message.isUser && message.agent && (
          <>
            <div className="flex justify-between items-center px-4 pt-2 text-xs">
              <span className="font-semibold">{message.agent}</span>
              {message.startTime && <Timer startTime={message.startTime} endTime={message.endTime} />}
            </div>
            {agentImage && (
              <img
                src={agentImage}
                alt={message.agent}
                className="absolute -bottom-4 -left-4 h-10 w-10 rounded-full border-2 border-white dark:border-gray-800"
              />
            )}
          </>
        )}
        <CardContent className={cn("p-4", !message.isUser && message.agent ? "pt-1 pl-10" : "")}>
          {renderContent()}
        </CardContent>
      </Card>
    </div>
  );
}