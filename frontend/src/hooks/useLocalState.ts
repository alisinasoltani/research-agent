// src/hooks/useLocalState.ts
import { useState, useEffect } from "react";

/**
 * A custom hook to persist state to localStorage.
 * @param key The key to use for localStorage.
 * @param initialState The initial state value.
 * @returns A tuple with the state and a function to update it.
 */
export function useLocalState<T>(key: string, initialState: T): [T, (value: T) => void] {
  // Use a function to initialize state from localStorage
  const [state, setState] = useState<T>(() => {
    try {
      const storedValue = localStorage.getItem(key);
      return storedValue ? JSON.parse(storedValue) : initialState;
    } catch (error) {
      console.error("Failed to read from localStorage", error);
      return initialState;
    }
  });

  // Use useEffect to write to localStorage whenever the state changes
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(state));
    } catch (error) {
      console.error("Failed to write to localStorage", error);
    }
  }, [key, state]);

  return [state, setState];
}
