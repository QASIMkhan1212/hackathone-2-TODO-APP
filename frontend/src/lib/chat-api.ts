/**
 * Chat API client for sending messages to the AI chatbot.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatMessage {
  message: string;
}

export interface ToolCall {
  name: string;
  arguments: Record<string, any>;
  result: any;
}

export interface ChatResponse {
  response: string;
  tool_calls: ToolCall[];
}

/**
 * Send a chat message to the AI assistant
 */
export async function sendChatMessage(
  userId: string,
  token: string,
  message: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/${userId}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Chat request failed: ${error}`);
  }

  return response.json();
}
