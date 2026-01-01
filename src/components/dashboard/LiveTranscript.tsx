import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, Bot } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
  timestamp: Date;
}

const mockMessages: Omit<Message, "id" | "timestamp">[] = [
  { role: "agent", content: "Hello! Thank you for calling TechSupport. How can I assist you today?" },
  { role: "user", content: "Hi, I'm having trouble with my internet connection. It keeps dropping every few minutes." },
  { role: "agent", content: "I'm sorry to hear that. Let me help you troubleshoot this issue. Can you tell me what router model you're using?" },
  { role: "user", content: "It's a Netgear R7000. I've tried restarting it but the problem persists." },
  { role: "agent", content: "I understand. The R7000 is a solid router. Let's check a few things. First, have you noticed if the issue happens at specific times of day?" },
  { role: "user", content: "Yes, actually it seems worse in the evenings around 7-9 PM." },
  { role: "agent", content: "That's helpful information. Peak usage times can cause congestion. I'd recommend we check your channel settings and possibly update your firmware." },
];

export function LiveTranscript() {
  const [messages, setMessages] = useState<Message[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Simulate live messages coming in
    let index = 0;
    const interval = setInterval(() => {
      if (index < mockMessages.length) {
        const newMessage: Message = {
          ...mockMessages[index],
          id: `msg-${Date.now()}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, newMessage]);
        index++;
      } else {
        clearInterval(interval);
      }
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div
      ref={scrollRef}
      className="h-80 overflow-y-auto scrollbar-thin space-y-4 p-4"
    >
      <AnimatePresence mode="popLayout">
        {messages.map((message) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className={cn(
              "flex gap-3",
              message.role === "user" ? "flex-row-reverse" : ""
            )}
          >
            <div
              className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                message.role === "agent"
                  ? "bg-primary/20 text-primary"
                  : "bg-accent/20 text-accent"
              )}
            >
              {message.role === "agent" ? (
                <Bot className="w-4 h-4" />
              ) : (
                <User className="w-4 h-4" />
              )}
            </div>
            <div
              className={cn(
                "max-w-[80%] rounded-2xl px-4 py-3",
                message.role === "agent"
                  ? "bg-muted/50 rounded-tl-sm"
                  : "bg-primary/10 rounded-tr-sm"
              )}
            >
              <p className="text-sm text-foreground leading-relaxed">
                {message.content}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {messages.length === 0 && (
        <div className="h-full flex items-center justify-center text-muted-foreground">
          <p className="text-sm">Waiting for call to start...</p>
        </div>
      )}
    </div>
  );
}
