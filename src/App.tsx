import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { CallingQueueProvider } from "./contexts/CallingQueueContext";
import Index from "./pages/Index";
import CallLogs from "./pages/CallLogs";
import CallingList from "./pages/CallingList";
import Databases from "./pages/Databases";
import KnowledgeBase from "./pages/KnowledgeBase";
import ManagerDashboard from "./pages/ManagerDashboard";
import Complaints from "./pages/Complaints";
import AreaHotspots from "./pages/AreaHotspots";
import OutboundCampaigns from "./pages/OutboundCampaigns";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <CallingQueueProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/call-logs" element={<CallLogs />} />
            <Route path="/calling-list" element={<CallingList />} />
            <Route path="/databases" element={<Databases />} />
            <Route path="/knowledge-base" element={<KnowledgeBase />} />
            <Route path="/manager-dashboard" element={<ManagerDashboard />} />
            <Route path="/complaints" element={<Complaints />} />
            <Route path="/area-hotspots" element={<AreaHotspots />} />
            <Route path="/outbound-campaigns" element={<OutboundCampaigns />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </CallingQueueProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
