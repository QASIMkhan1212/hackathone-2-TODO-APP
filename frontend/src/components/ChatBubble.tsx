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
  const [isMobile, setIsMobile] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check if mobile on mount and resize
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 640);
    };
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Prevent body scroll when chat is open on mobile
  useEffect(() => {
    if (isOpen && isMobile) {
      document.body.style.overflow = "hidden";
      document.body.style.position = "fixed";
      document.body.style.width = "100%";
    } else {
      document.body.style.overflow = "";
      document.body.style.position = "";
      document.body.style.width = "";
    }
    return () => {
      document.body.style.overflow = "";
      document.body.style.position = "";
      document.body.style.width = "";
    };
  }, [isOpen, isMobile]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue("");

    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response: ChatResponse = await sendChatMessage(userId, token, userMessage);
      setMessages((prev) => [...prev, { role: "assistant", content: response.response }]);

      if (response.tool_calls && response.tool_calls.length > 0) {
        onTasksChanged();
      }
    } catch {
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

  // Floating button when closed
  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        aria-label="Open AI Assistant"
        style={{
          position: "fixed",
          bottom: "16px",
          right: "16px",
          zIndex: 9999,
          width: "56px",
          height: "56px",
          borderRadius: "50%",
          background: "linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%)",
          color: "white",
          border: "none",
          boxShadow: "0 4px 14px rgba(99, 102, 241, 0.4)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          WebkitTapHighlightColor: "transparent",
          touchAction: "manipulation",
        }}
        title="Open AI Assistant"
      >
        <ChatIcon />
      </button>
    );
  }

  // Mobile styles
  const mobileContainerStyle: React.CSSProperties = {
    position: "fixed",
    bottom: 0,
    left: 0,
    right: 0,
    top: "auto",
    height: "85vh",
    maxHeight: "600px",
    zIndex: 9999,
    display: "flex",
    flexDirection: "column",
    backgroundColor: "var(--card)",
    borderTopLeftRadius: "20px",
    borderTopRightRadius: "20px",
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,
    boxShadow: "0 -4px 30px rgba(0,0,0,0.2)",
    overflow: "hidden",
  };

  // Desktop styles
  const desktopContainerStyle: React.CSSProperties = {
    position: "fixed",
    bottom: "16px",
    right: "16px",
    left: "auto",
    top: "auto",
    width: "380px",
    height: "500px",
    zIndex: 9999,
    display: "flex",
    flexDirection: "column",
    backgroundColor: "var(--card)",
    border: "1px solid var(--card-border)",
    borderRadius: "16px",
    boxShadow: "0 10px 40px rgba(0,0,0,0.15)",
    overflow: "hidden",
  };

  return (
    <>
      {/* Backdrop for mobile */}
      {isMobile && (
        <div
          onClick={() => setIsOpen(false)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            zIndex: 9998,
          }}
        />
      )}

      {/* Chat window */}
      <div style={isMobile ? mobileContainerStyle : desktopContainerStyle}>
        {/* Drag handle for mobile */}
        {isMobile && (
          <div
            style={{
              width: "100%",
              padding: "8px 0",
              display: "flex",
              justifyContent: "center",
              backgroundColor: "var(--card)",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "4px",
                backgroundColor: "var(--muted)",
                borderRadius: "2px",
                opacity: 0.5,
              }}
            />
          </div>
        )}

        {/* Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: isMobile ? "8px 16px 12px" : "14px 16px",
            borderBottom: "1px solid var(--card-border)",
            background: "linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%)",
            color: "white",
            flexShrink: 0,
            borderTopLeftRadius: isMobile ? 0 : "16px",
            borderTopRightRadius: isMobile ? 0 : "16px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <ChatIcon />
            <h3 style={{ fontWeight: 600, fontSize: "15px", margin: 0 }}>AI Assistant</h3>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            aria-label="Close chat"
            style={{
              padding: "8px",
              background: "rgba(255,255,255,0.15)",
              border: "none",
              borderRadius: "8px",
              color: "white",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              WebkitTapHighlightColor: "transparent",
            }}
          >
            <CloseIcon />
          </button>
        </div>

        {/* Messages */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "16px",
            WebkitOverflowScrolling: "touch",
          }}
        >
          {messages.length === 0 && (
            <div style={{ textAlign: "center", color: "var(--muted)", padding: "32px 16px" }}>
              <p style={{ fontSize: "14px", margin: "0 0 8px 0" }}>Hi! I can help you manage your tasks.</p>
              <p style={{ fontSize: "12px", margin: 0, opacity: 0.7 }}>
                Try: "Add task buy groceries" or "Show my tasks"
              </p>
            </div>
          )}
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  display: "flex",
                  justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                }}
              >
                <div
                  style={{
                    maxWidth: "85%",
                    padding: "10px 14px",
                    borderRadius: "16px",
                    fontSize: "14px",
                    lineHeight: "1.5",
                    wordBreak: "break-word",
                    ...(msg.role === "user"
                      ? {
                          background: "linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%)",
                          color: "white",
                          borderBottomRightRadius: "4px",
                        }
                      : {
                          background: "var(--input-bg)",
                          color: "var(--foreground)",
                          borderBottomLeftRadius: "4px",
                        }),
                  }}
                >
                  <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", margin: 0 }}>
                    {msg.content}
                  </pre>
                </div>
              </div>
            ))}
            {isLoading && (
              <div style={{ display: "flex", justifyContent: "flex-start" }}>
                <div
                  style={{
                    background: "var(--input-bg)",
                    padding: "12px 16px",
                    borderRadius: "16px",
                    borderBottomLeftRadius: "4px",
                  }}
                >
                  <LoaderIcon />
                </div>
              </div>
            )}
          </div>
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form
          onSubmit={handleSendMessage}
          style={{
            padding: "12px 16px",
            paddingBottom: isMobile ? "max(12px, env(safe-area-inset-bottom, 12px))" : "12px",
            borderTop: "1px solid var(--card-border)",
            flexShrink: 0,
            backgroundColor: "var(--card)",
          }}
        >
          <div style={{ display: "flex", gap: "10px" }}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type a message..."
              disabled={isLoading}
              autoComplete="off"
              style={{
                flex: 1,
                padding: "12px 16px",
                borderRadius: "12px",
                fontSize: "16px",
                background: "var(--input-bg)",
                border: "1px solid var(--card-border)",
                color: "var(--foreground)",
                outline: "none",
                opacity: isLoading ? 0.5 : 1,
                WebkitAppearance: "none",
              }}
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              aria-label="Send message"
              style={{
                padding: "12px 18px",
                borderRadius: "12px",
                background: "linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%)",
                color: "white",
                border: "none",
                cursor: !inputValue.trim() || isLoading ? "not-allowed" : "pointer",
                opacity: !inputValue.trim() || isLoading ? 0.5 : 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                WebkitTapHighlightColor: "transparent",
              }}
            >
              <SendIcon />
            </button>
          </div>
        </form>
      </div>
    </>
  );
};
