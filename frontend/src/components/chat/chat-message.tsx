/**
 * Chat message component
 */

import { cn } from "@/lib/utils";
import type { Message } from "@/lib/api/chat";
import { Bot, User } from "lucide-react";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 mb-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-background shadow">
          <Bot className="h-4 w-4" />
        </div>
      )}
      <div
        className={cn(
          "rounded-lg px-4 py-2 max-w-[80%]",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        )}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        <span className="text-xs opacity-50 mt-1 block">
          {new Date(message.created_at).toLocaleTimeString()}
        </span>
      </div>
      {isUser && (
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-primary text-primary-foreground shadow">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
}
