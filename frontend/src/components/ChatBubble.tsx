"use client";

import { useState, useRef, useEffect } from "react";
import { sendChatMessage, ChatResponse } from "../lib/chat-api";

// Icons
const ChatIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
  </svg>
);

const CloseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
);

const SendIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13"></line>
    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
  </svg>
);

const LoaderIcon = () => (
  <svg className="animate-spin" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="2" x2="12" y2="6"></line>
    <line x1="12" y1="18" x2="12" y2="22"></line>
    <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
    <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
    <line x1="2" y1="12" x2="6" y2="12"></line>
    <line x1="18" y1="12" x2="22" y2="12"></line>
    <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
    <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
  </svg>
);

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatBubbleProps {
  userId: string;
  token: string;
  onTasksChanged: () => void;
}

export const ChatBubble = ({ userId, token, onTasksChanged }: ChatBubbleProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue("");

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response: ChatResponse = await sendChatMessage(userId, token, userMessage);

      // Add assistant response
      setMessages((prev) => [...prev, { role: "assistant", content: response.response }]);

      // If there were tool calls, refresh the task list
      if (response.tool_calls && response.tool_calls.length > 0) {
        onTasksChanged();
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="
          fixed bottom-6 right-6 z-50
          w-14 h-14 rounded-full
          bg-gradient-to-r from-[var(--primary)] to-[var(--primary-hover)]
          text-white shadow-lg
          hover:shadow-xl hover:scale-110
          transition-all duration-200
          flex items-center justify-center
        "
        title="Open AI Assistant"
      >
        <ChatIcon />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 w-96 h-[500px] flex flex-col bg-[var(--card)] border border-[var(--card-border)] rounded-2xl shadow-2xl animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--card-border)] bg-gradient-to-r from-[var(--primary)] to-[var(--primary-hover)] text-white rounded-t-2xl">
        <div className="flex items-center gap-2">
          <ChatIcon />
          <h3 className="font-semibold">AI Assistant</h3>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="p-1 hover:bg-white/20 rounded-lg transition-colors"
          title="Close"
        >
          <CloseIcon />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center text-[var(--muted)] py-8">
            <p className="text-sm">Hi! I can help you manage your tasks.</p>
            <p className="text-xs mt-2">Try: "Add task buy groceries" or "Show my tasks"</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`
                max-w-[80%] px-4 py-2 rounded-2xl text-sm
                ${
                  msg.role === "user"
                    ? "bg-gradient-to-r from-[var(--primary)] to-[var(--primary-hover)] text-white rounded-br-sm"
                    : "bg-[var(--input-bg)] text-[var(--foreground)] rounded-bl-sm"
                }
              `}
            >
              <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-[var(--input-bg)] px-4 py-2 rounded-2xl rounded-bl-sm">
              <LoaderIcon />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSendMessage} className="p-4 border-t border-[var(--card-border)]">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type a message..."
            disabled={isLoading}
            className="
              flex-1 px-4 py-2 rounded-xl
              bg-[var(--input-bg)] border border-[var(--card-border)]
              focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20
              transition-all duration-200
              placeholder:text-[var(--muted)]
              disabled:opacity-50
            "
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="
              px-4 py-2 rounded-xl
              bg-gradient-to-r from-[var(--primary)] to-[var(--primary-hover)]
              text-white
              hover:shadow-lg
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
              flex items-center justify-center
            "
          >
            <SendIcon />
          </button>
        </div>
      </form>
    </div>
  );
};
