// src/lib/apiClient.ts
import { Session } from "next-auth";

// Define the base URL for the external agentic server from environment variables
const AGENT_SERVER_BASE_URL = process.env.NEXT_PUBLIC_AGENT_SERVER_BASE_URL;

/**
 * A client-side fetch wrapper for making API calls to the agentic server.
 * It automatically includes the user's ID from the session in a header.
 * @param endpoint The API endpoint to call (e.g., "/history").
 * @param method The HTTP method (e.g., "GET", "POST").
 * @param session The NextAuth session object.
 * @param data Optional body data for POST/PUT requests.
 * @returns A promise that resolves to the response data.
 */
export async function apiClient<T>(
  endpoint: string,
  method: "GET" | "POST",
  session: Session,
  data?: object
): Promise<T> {
  // Ensure we have a valid base URL and session
  if (!AGENT_SERVER_BASE_URL) {
    throw new Error("AGENT_SERVER_BASE_URL is not defined.");
  }
  if (!session?.user?.id) {
    throw new Error("User session is not available.");
  }

  const url = `${AGENT_SERVER_BASE_URL}${endpoint}`;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    // Use the X-User-Id header to pass the user's ID to the server
    "X-User-Id": session.user.id,
  };

  const config: RequestInit = {
    method,
    headers,
    body: data ? JSON.stringify(data) : undefined,
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      // Handle non-2xx HTTP responses
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        `API call failed with status ${response.status}: ${
          errorData.message || response.statusText
        }`
      );
    }
    return response.json();
  } catch (error) {
    console.error(`Error fetching from ${url}:`, error);
    throw error;
  }
}
