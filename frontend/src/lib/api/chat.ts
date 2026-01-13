/**
 * Chat API client for AI-powered task management
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

export interface ToolCall {
  tool_name: string;
  arguments: Record<string, any>;
  result: any;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
}

export interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface Conversation {
  id: number;
  user_id: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ConversationSummary {
  id: number;
  created_at: string;
  updated_at: string;
  message_count: number;
}

/**
 * Get JWT token from Better Auth token endpoint
 */
async function getAuthToken(): Promise<string | null> {
  try {
    const baseURL =
      process.env.NEXT_PUBLIC_BASE_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:3000";
    const response = await fetch(`${baseURL}/api/auth/token`, {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data.token || data.accessToken || data.jwt || null;
    }

    return null;
  } catch (error) {
    console.error("Failed to get auth token:", error);
    return null;
  }
}

/**
 * Send a message to the chat API
 */
export async function sendChatMessage(
  message: string,
  conversationId?: number
): Promise<{
  conversation_id: number;
  response: string;
  tool_calls: Array<{ tool_name: string; arguments: any; result: any }>;
}> {
  const token = await getAuthToken();

  if (!token) {
    throw new Error("Not authenticated");
  }

  const response = await fetch(`${API_URL}/api/v1/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId || null,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to send message" }));
    throw new Error(error.detail || "Failed to send message");
  }

  return response.json();
}
