import { useState } from "react";
import { Phone, PhoneOff, Bell, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function AppHeader() {
  const [isCallActive, setIsCallActive] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const handleTestCall = async () => {
    if (isCallActive) {
      setIsCallActive(false);
      return;
    }

    setIsConnecting(true);
    
    // Simulate connection delay
    setTimeout(() => {
      setIsConnecting(false);
      setIsCallActive(true);
    }, 1500);
  };

  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-xl flex items-center justify-between px-6 sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-foreground">Dashboard</h2>
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/50 border border-border">
          <span className="status-dot status-dot-live" />
          <span className="text-xs text-muted-foreground">All systems operational</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Test Call Button */}
        <Button
          onClick={handleTestCall}
          variant={isCallActive ? "destructive" : "default"}
          className={cn(
            "gap-2 transition-all duration-300",
            isCallActive && "animate-pulse-glow",
            !isCallActive && !isConnecting && "bg-gradient-to-r from-primary to-accent hover:opacity-90"
          )}
          disabled={isConnecting}
        >
          {isConnecting ? (
            <>
              <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              <span>Connecting...</span>
            </>
          ) : isCallActive ? (
            <>
              <PhoneOff className="w-4 h-4" />
              <span>End Test Call</span>
            </>
          ) : (
            <>
              <Phone className="w-4 h-4" />
              <span>Start Test Call</span>
            </>
          )}
        </Button>

        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="w-5 h-5 text-muted-foreground" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full" />
        </Button>

        {/* User Avatar */}
        <Button variant="ghost" size="icon" className="rounded-full">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <User className="w-4 h-4 text-primary-foreground" />
          </div>
        </Button>
      </div>
    </header>
  );
}
