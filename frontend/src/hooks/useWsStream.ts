// src/hooks/useWsStream.ts
import { useEffect, useState, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSession } from "next-auth/react";
import { apiClient } from "@/lib/apiClient";

export interface ChatMessage {
  id: string;
  isUser: boolean;
  content: string;
  isStreaming?: boolean;
  isWaiting?: boolean;
  startTime?: number;
  endTime?: number;
  agent?: string;
  isError?: boolean;
}

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

interface SimplificationCompleteEvent {
  event: "simplification_complete";
  agent_name: string;
  content: string;
}

interface ValidationScoreEvent {
  event: "validation_score";
  agent_name: string;
  score: number;
}

type WsEvent =
  | AgentStartEvent
  | AgentOutputEvent
  | FinalAnswerEvent
  | ErrorEvent
  | ThoughtsAndTasksEvent
  | TaskDelegatedEvent
  | LoopRetryEvent
  | SimplificationCompleteEvent
  | ValidationScoreEvent
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
 * Manages WebSocket connection and streams chat messages.
 * Handles initial data fetching and streaming with typing effect.
 * @param props The props for the hook.
 * @returns Messages, connection status, and send function.
 */
export function useWsStream({ threadId, onEvent }: UseWsStreamProps) {
  const [status, setStatus] = useState<"idle" | "connecting" | "streaming" | "error">("idle");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streamQueue, setStreamQueue] = useState<string>("");
  const wsRef = useRef<WebSocket | null>(null);
  const typingRef = useRef<NodeJS.Timeout | null>(null);
  const idCounter = useRef(0);
  const { data: session } = useSession();

  const specialAgents = ["Architect Agent", "Task Agents", "Simplifier Agent", "Validator Agent", "Final Synthesizer"];

  // Map server agent names to display names (adjust if server sends different names)
  const agentNameMap: Record<string, string> = {
    "Architect Agent": "Eleanor",
    "Task Agents": "Layla", // Individual task agents get their own names via task_delegated
    "Simplifier Agent": "Nova",
    "Validator Agent": "Isaac",
    "Final Synthesizer": "Final Synthesizer",
  };

  const generateUniqueId = (prefix: string) => {
    idCounter.current += 1;
    return `${prefix}-${Date.now()}-${idCounter.current}-${Math.random().toString(36).substring(2, 7)}`;
  };

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

  useEffect(() => {
    if (conversationHistory) {
      setMessages(conversationHistory.messages);
    } else {
      setMessages([]);
    }
  }, [conversationHistory]);

  useEffect(() => {
    if (streamQueue.length > 0 && !typingRef.current) {
      typingRef.current = setInterval(() => {
        setStreamQueue((prevQueue) => {
          if (prevQueue.length === 0) {
            if (typingRef.current) clearInterval(typingRef.current);
            typingRef.current = null;
            return "";
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
      }, 20);
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
    const wsUrl = `ws://${window.location.hostname}:8000/ws`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected.");
      setStatus("streaming");
      if (initialPrompt) {
        ws.send(JSON.stringify({ prompt: initialPrompt }));
      }
    };

    ws.onmessage = (event) => {
      try {
        const data: WsEvent = JSON.parse(event.data);
        console.log("Received WebSocket event:", data);
        onEvent?.(data);

        switch (data.event) {
          case "agent_start":
            if (
              specialAgents.includes(data.agent) &&
              data.agent !== "Task Agents" &&
              data.agent !== "Architect Agent" &&
              data.agent !== "Validator Agent"
            ) {
              setMessages((prev) => [
                ...prev,
                {
                  id: generateUniqueId(data.agent),
                  isUser: false,
                  agent: agentNameMap[data.agent] || data.agent,
                  content: "",
                  isWaiting: true,
                  startTime: Date.now(),
                },
              ]);
            }
            break;
          case "thoughts_and_tasks":
            // Do not display in main chat; only log to dev panel via onEvent
            break;
          case "task_delegated":
            setMessages((prev) => [
              ...prev,
              {
                id: generateUniqueId(`task-${data.agent_name}`),
                isUser: false,
                agent: data.agent_name, // Assume server sends correct names like "Layla"
                content: "",
                isWaiting: true,
                startTime: Date.now(),
              },
            ]);
            break;
          case "agent_output":
            setMessages((prev) => {
              return prev.map((msg) => {
                if (msg.agent === data.agent_name && msg.isWaiting) {
                  return {
                    ...msg,
                    content: data.content,
                    isWaiting: false,
                    endTime: Date.now(),
                  };
                }
                return msg;
              });
            });
            break;
          case "simplification_complete":
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.isWaiting && last.agent === agentNameMap["Simplifier Agent"]) {
                updated[updated.length - 1] = {
                  ...last,
                  content: data.content,
                  isWaiting: false,
                  endTime: Date.now(),
                };
                return updated;
              } else {
                updated.push({
                  id: generateUniqueId("simplification"),
                  isUser: false,
                  agent: agentNameMap["Simplifier Agent"],
                  content: data.content,
                });
                return updated;
              }
            });
            break;
          case "validation_score":
            // Do not display in main chat; only log to dev panel via onEvent
            break;
          case "loop_retry":
            // Do not display in main chat; only log to dev panel via onEvent
            break;
          case "final_answer":
            setMessages((prev) => {
              const updatedMessages = [...prev];
              const lastMessage = updatedMessages[updatedMessages.length - 1];
              if (lastMessage && (lastMessage.isStreaming || lastMessage.isWaiting)) {
                updatedMessages[updatedMessages.length - 1] = {
                  ...lastMessage,
                  content: data.content,
                  isStreaming: false,
                  isWaiting: false,
                  endTime: lastMessage.startTime ? Date.now() : undefined,
                };
              } else {
                updatedMessages.push({
                  id: generateUniqueId("final"),
                  isUser: false,
                  agent: agentNameMap["Final Synthesizer"],
                  content: data.content,
                  isStreaming: false,
                });
              }
              return updatedMessages;
            });
            setStreamQueue("");
            break;
          case "system_abort":
          case "error":
            setStatus("error");
            console.error("WebSocket Error:", data.message);
            setMessages((prev) => [
              ...prev,
              {
                id: generateUniqueId("error"),
                isUser: false,
                content: data.message,
                isError: true,
              },
            ]);
            break;
          default:
            // Handle streamed content (model_output_raw)
            setMessages((prev) => {
              let updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.isWaiting) {
                updated[updated.length - 1] = {
                  ...last,
                  content: "",
                  isWaiting: false,
                  isStreaming: true,
                };
              } else if (!last || last.isUser || (!last.isStreaming && !last.isWaiting)) {
                // If no suitable last message, add a new streaming message without agent
                updated.push({
                  id: generateUniqueId("streaming"),
                  isUser: false,
                  content: "",
                  isStreaming: true,
                  startTime: Date.now(),
                });
              }
              return updated;
            });
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
    // Add only the user message; let WS events drive assistant bubbles
    setMessages((prev) => [
      ...prev,
      { id: generateUniqueId("user"), isUser: true, content: prompt },
    ]);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ prompt }));
    } else {
      connect(prompt);
    }
  };

  return { messages, status, sendMessage, isLoading };
}