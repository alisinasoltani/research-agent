// src/hooks/useScrollPosition.ts
import { useEffect, useRef } from "react";

/**
 * A custom hook to persist and restore the scroll position of an element.
 * @param threadId The ID of the current conversation thread.
 */
export function useScrollPosition(threadId: string | null) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const scrollPositionKey = threadId ? `scroll-pos-${threadId}` : "scroll-pos-new";

  // Effect to save the scroll position on unmount or thread change
  useEffect(() => {
    const saveScrollPosition = () => {
      if (scrollRef.current) {
        localStorage.setItem(scrollPositionKey, scrollRef.current.scrollTop.toString());
      }
    };

    return () => {
      saveScrollPosition();
    };
  }, [scrollPositionKey]);

  // Effect to restore the scroll position when the thread changes
  useEffect(() => {
    if (scrollRef.current) {
      const storedScrollPosition = localStorage.getItem(scrollPositionKey);
      if (storedScrollPosition) {
        scrollRef.current.scrollTop = parseInt(storedScrollPosition, 10);
      } else {
        // Scroll to the bottom for new chats
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
      }
    }
  }, [threadId, scrollPositionKey]);

  return scrollRef;
}
