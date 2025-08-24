// src/hooks/useDraft.ts
import { useState, useEffect, useCallback } from "react";

/**
 * A custom hook to manage a chat draft, persisting it to localStorage only on unmount.
 * @param threadId The ID of the current conversation thread.
 * @returns A tuple with the draft text and a function to update it.
 */
export function useDraft(threadId: string | null) {
  const localStorageKey = threadId ? `draft-${threadId}` : "draft-new";

  const [draft, setDraft] = useState<string>(() => {
    // Initialize state from localStorage
    try {
      const storedValue = localStorage.getItem(localStorageKey);
      return storedValue ? JSON.parse(storedValue) : "";
    } catch (error) {
      console.error("Failed to read from localStorage", error);
      return "";
    }
  });

  // Use a ref to hold the latest draft value to access it in the unmount effect
  const draftRef = useCallback((node: HTMLTextAreaElement | null) => {
    if (node) {
      // Restore the draft from localStorage on mount
      const storedValue = localStorage.getItem(localStorageKey);
      if (storedValue) {
        node.value = JSON.parse(storedValue);
        setDraft(JSON.parse(storedValue));
      }
    }
  }, [localStorageKey]);

  // Save the draft to localStorage when the component unmounts or the key changes
  useEffect(() => {
    return () => {
      try {
        localStorage.setItem(localStorageKey, JSON.stringify(draft));
      } catch (error) {
        console.error("Failed to write to localStorage", error);
      }
    };
  }, [localStorageKey, draft]);

  return { draft, setDraft };
}
