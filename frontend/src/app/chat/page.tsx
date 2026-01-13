/**
 * Chat page for AI-powered task management
 */

import { ChatInterface } from "@/components/chat/chat-interface";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function ChatPage() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
        <h1 className="text-3xl font-bold">AI Task Assistant</h1>
        <p className="text-muted-foreground mt-2">
          Chat with your AI assistant to manage tasks naturally
        </p>
      </div>
      <ChatInterface />
    </div>
  );
}
