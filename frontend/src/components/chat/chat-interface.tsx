/**
 * Main chat interface component
 */

"use client";

import { useChat } from "@/lib/hooks/use-chat";
import { ChatInput } from "./chat-input";
import { ChatMessage } from "./chat-message";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, MessageSquare, RefreshCw } from "lucide-react";
import { useEffect, useRef } from "react";

export function ChatInterface() {
  const { messages, sendMessage, clearMessages, isLoading, error } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (message: string) => {
    try {
      await sendMessage(message);
    } catch (err) {
      console.error("Failed to send message:", err);
    }
  };

  return (
    <Card className="w-full h-[calc(100vh-12rem)] flex flex-col">
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Todo Assistant
          </CardTitle>
          {messages.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={clearMessages}
              disabled={isLoading}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              New Chat
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
              <MessageSquare className="h-12 w-12 mb-4 opacity-50" />
              <h3 className="text-lg font-medium mb-2">Start a conversation</h3>
              <p className="text-sm max-w-sm">
                Ask me to help you manage your tasks. I can create, list, update, complete, and delete tasks for you.
              </p>
              <div className="mt-6 space-y-2 text-left max-w-md">
                <p className="text-xs font-medium">Try saying:</p>
                <ul className="text-xs space-y-1 list-disc list-inside">
                  <li>&quot;Add a task to buy groceries&quot;</li>
                  <li>&quot;Show me all my pending tasks&quot;</li>
                  <li>&quot;Mark task 1 as complete&quot;</li>
                  <li>&quot;Delete task 2&quot;</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Thinking...</span>
                </div>
              )}
            </div>
          )}
        </ScrollArea>
        <div className="border-t p-4">
          {error && (
            <div className="mb-2 text-sm text-destructive">
              Error: {error instanceof Error ? error.message : "Failed to send message"}
            </div>
          )}
          <ChatInput onSend={handleSend} disabled={isLoading} />
        </div>
      </CardContent>
    </Card>
  );
}
