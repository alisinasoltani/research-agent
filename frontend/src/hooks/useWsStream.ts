// src/hooks/useWsStream.ts
import { useEffect, useState, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSession } from "next-auth/react";
import { apiClient } from "@/lib/apiClient";

// Define the shape of our chat messages
export interface ChatMessage {
  id: string;
  isUser: boolean;
  content: string;
  isStreaming?: boolean;
}

// Define the types for the incoming WebSocket events
interface AgentStartEvent {
  event: "agent_start";
  agent: string;
  status: string;
}

interface AgentOutputEvent {
  event: "agent_output";
  agent_name: string;
  content: string;
}

interface FinalAnswerEvent {
  event: "final_answer";
  content: string;
}

interface ErrorEvent {
  event: "error" | "system_abort";
  message: string;
}

interface ThoughtsAndTasksEvent {
  event: "thoughts_and_tasks";
  content: string;
  tasks: { [key: string]: string };
}

interface TaskDelegatedEvent {
  event: "task_delegated";
  agent_name: string;
  task: string;
}

interface LoopRetryEvent {
  event: "loop_retry";
  message: string;
}


type WsEvent =
  | AgentStartEvent
  | AgentOutputEvent
  | FinalAnswerEvent
  | ErrorEvent
  | ThoughtsAndTasksEvent
  | TaskDelegatedEvent
  | LoopRetryEvent
  | any;

interface UseWsStreamProps {
  threadId: string | null;
  onEvent?: (event: WsEvent) => void;
}

interface Conversation {
  thread_id: string;
  messages: ChatMessage[];
}

/**
 * A custom hook to manage a WebSocket connection and stream chat messages.
 * This hook is now self-contained, handling both initial data fetching and streaming.
 * @param props The props for the hook.
 * @returns An object with the list of messages, connection status, and functions to send/restart.
 */
export function useWsStream({ threadId, onEvent }: UseWsStreamProps) {
  const [status, setStatus] = useState<"idle" | "connecting" | "streaming" | "error">("idle");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streamQueue, setStreamQueue] = useState<string>('');
  const wsRef = useRef<WebSocket | null>(null);
  const typingRef = useRef<NodeJS.Timeout | null>(null);
  const { data: session } = useSession();

  // Fetch initial conversation history using TanStack Query
  const { data: conversationHistory, isLoading } = useQuery<Conversation>({
    queryKey: ["conversation", threadId],
    queryFn: () => {
      if (!session || !threadId) {
        return Promise.resolve({ thread_id: "", messages: [] });
      }
      return apiClient<Conversation>(`/conversation/${threadId}`, "GET", session);
    },
    enabled: !!session && !!threadId,
  });

  // Use a separate effect to update messages when conversationHistory changes
  useEffect(() => {
    if (conversationHistory) {
      setMessages(conversationHistory.messages);
    } else {
      setMessages([]);
    }
  }, [conversationHistory]);

  // Typing effect for streamed content
  useEffect(() => {
    if (streamQueue.length > 0 && !typingRef.current) {
      typingRef.current = setInterval(() => {
        setStreamQueue((prevQueue) => {
          if (prevQueue.length === 0) {
            if (typingRef.current) clearInterval(typingRef.current);
            typingRef.current = null;
            return '';
          }

          const nextChar = prevQueue[0];
          const newQueue = prevQueue.slice(1);

          setMessages((prevMessages) => {
            const lastMessage = prevMessages[prevMessages.length - 1];
            if (lastMessage && lastMessage.isStreaming) {
              return [
                ...prevMessages.slice(0, -1),
                { ...lastMessage, content: lastMessage.content + nextChar },
              ];
            }
            return prevMessages;
          });

          return newQueue;
        });
      }, 20); // ~50 chars/sec; adjust for desired speed
    }

    return () => {
      if (typingRef.current) {
        clearInterval(typingRef.current);
        typingRef.current = null;
      }
    };
  }, [streamQueue]);

  const connect = (initialPrompt?: string) => {
    setStatus("connecting");
    // Ensure this URL is correctly configured to your agentic server's WS endpoint
    const wsUrl = `ws://${window.location.hostname}:8000/ws`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected.");
      setStatus("streaming");
      // If there's an initial prompt, send it to the server
      if (initialPrompt) {
        ws.send(JSON.stringify({ prompt: initialPrompt, user_id: "Alisina" }));
      }
    };

    ws.onmessage = (event) => {
      try {
        const data: WsEvent = JSON.parse(event.data);
        console.log("Received WebSocket event:", data); // Log all events
        onEvent?.(data);

        // Handle specific event types
        switch (data.event) {
          case "agent_start":
            setMessages((prev) => [
              ...prev,
              {
                id: `${data.agent}-${Date.now().toString()}`,
                isUser: false,
                content: `${data.agent} started...`,
              },
            ]);
            break;
          case "thoughts_and_tasks":
            setMessages((prev) => [
              ...prev,
              {
                id: `thoughts-${Date.now().toString()}`,
                isUser: false,
                content: `Architect created tasks: ${Object.values(data.tasks).join(", ")}`,
              },
            ]);
            break;
          case "task_delegated":
            setMessages((prev) => [
              ...prev,
              {
                id: `task-${data.agent_name}-${Date.now().toString()}`,
                isUser: false,
                content: `Task assigned to ${data.agent_name}.`,
              },
            ]);
            break;
          case "agent_output":
            setMessages((prev) => [
              ...prev,
              {
                id: `agent_output-${data.agent_name || ''}-${Date.now().toString()}`,
                isUser: false,
                content: data.content,
              },
            ]);
            break;
          case "loop_retry":
            setMessages((prev) => [
              ...prev,
              {
                id: `loop_retry-${Date.now().toString()}`,
                isUser: false,
                content: data.message || data.content,
              },
            ]);
            break;

          case "final_answer":
            setMessages((prev) => {
              const updatedMessages = [...prev];
              const lastMessage = updatedMessages[updatedMessages.length - 1];
              if (lastMessage && lastMessage.isStreaming) {
                updatedMessages[updatedMessages.length - 1] = {
                  ...lastMessage,
                  content: data.content,
                  isStreaming: false,
                };
              } else {
                updatedMessages.push({
                  id: Date.now().toString(),
                  isUser: false,
                  content: data.content,
                  isStreaming: false,
                });
              }
              return updatedMessages;
            });
            setStreamQueue(''); // Clear queue on final answer
            break;

          case "system_abort":
          case "error":
            setStatus("error");
            console.error("WebSocket Error:", data.message);
            // Optional: Update state to show a user-friendly error toast
            break;

          default:
            // For model_output_raw or other streamed text, append to the queue for typing effect
            setStreamQueue((prev) => prev + (data.content || ""));
            break;
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket closed.");
      setStatus("idle");
    };

    ws.onerror = (e) => {
      console.error("WebSocket error:", e);
      setStatus("error");
    };
  };

  useEffect(() => {
    // Clean up the WebSocket connection when the component unmounts
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (typingRef.current) {
        clearInterval(typingRef.current);
      }
    };
  }, []);

  const sendMessage = (prompt: string) => {
    // Add the user message and a streaming agent message to the chat immediately
    setMessages((prev) => [
      ...prev,
      { id: Date.now().toString(), isUser: true, content: prompt },
      { id: `agent-streaming-${Date.now().toString()}`, isUser: false, content: "", isStreaming: true },
    ]);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ prompt }));
    } else {
      // If the connection is not open, connect and then send the message
      connect(prompt);
    }
  };

  return { messages, status, sendMessage, isLoading };
}