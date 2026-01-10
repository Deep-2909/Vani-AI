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
  { role: "agent", content: "Please provide your name for the complaint registration." },
  { role: "user", content: "My name is Rajesh Kumar, and this is regarding a water supply issue in our area." },
  { role: "agent", content: "Please describe the issue in your own words." },
  { role: "user", content: "We haven't had water supply for the past 3 days in our entire street. About 15-20 houses are affected." },
  { role: "agent", content: "Please let me know the urgency of the issue: Low, Medium, or High?" },
  { role: "user", content: "This is definitely High urgency. People are struggling without water for basic needs." },
  { role: "agent", content: "Please specify the exact location of the water leakage." },
  { role: "user", content: "It's not a leakage issue, it's a complete water supply cut in Sector 12, Dwarka, New Delhi." },
  { role: "agent", content: "Your complaint has been registered successfully. Your ticket number is DEL-964A76." },
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
