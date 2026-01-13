/**
 * Custom hook for chat functionality
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { sendChatMessage, type Message } from "../api/chat";

export function useChat(initialConversationId?: number) {
  const [conversationId, setConversationId] = useState<number | undefined>(initialConversationId);
  const [messages, setMessages] = useState<Message[]>([]);
  const queryClient = useQueryClient();

  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      return sendChatMessage(message, conversationId);
    },
    onSuccess: (data) => {
      // Update conversation ID if this is a new conversation
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      // Add user message and assistant response to local state
      const userMessage: Message = {
        id: Date.now(), // Temporary ID
        role: "user",
        content: data.response, // This will be replaced
        created_at: new Date().toISOString(),
      };

      const assistantMessage: Message = {
        id: Date.now() + 1, // Temporary ID
        role: "assistant",
        content: data.response,
        created_at: new Date().toISOString(),
      };

      // Invalidate conversations list to refresh
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
  });

  const sendMessage = async (message: string) => {
    // Add user message immediately
    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: message,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await sendMessageMutation.mutateAsync(message);

      // Add assistant message
      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: "assistant",
        content: response.response,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      return response;
    } catch (error) {
      // Remove optimistic user message on error
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
      throw error;
    }
  };

  const clearMessages = () => {
    setMessages([]);
    setConversationId(undefined);
  };

  return {
    messages,
    conversationId,
    sendMessage,
    clearMessages,
    isLoading: sendMessageMutation.isPending,
    error: sendMessageMutation.error,
  };
}
