import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  PhoneCall,
  BookOpen,
  Settings,
  Mic,
  Radio,
  ListOrdered,
  Database
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/calling-list", icon: ListOrdered, label: "Calling List" },
  { to: "/databases", icon: Database, label: "Databases" },
  { to: "/knowledge-base", icon: BookOpen, label: "Knowledge Base" },
  { to: "/call-logs", icon: PhoneCall, label: "Call Logs" },
];

export function AppSidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 h-screen bg-sidebar border-r border-sidebar-border flex flex-col fixed left-0 top-0 z-40">
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <Mic className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="font-semibold text-foreground">Voice AI</h1>
            <p className="text-xs text-muted-foreground">Command Center</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.to;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={cn(
                "sidebar-link",
                isActive && "sidebar-link-active"
              )}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Status Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="glass-card p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">System Status</span>
            <div className="flex items-center gap-2">
              <span className="status-dot status-dot-live" />
              <span className="text-xs text-success font-medium">Online</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Radio className="w-4 h-4 text-primary animate-pulse" />
            <span className="text-muted-foreground">3 Active Calls</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
