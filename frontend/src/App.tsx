import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Index from "./pages/Index.tsx";
import ProcessingPage from "./pages/ProcessingPage.tsx";
import ReportPage from "./pages/ReportPage.tsx";
import TemplatesPage from "./pages/TemplatesPage.tsx";
import HistoryPage from "./pages/HistoryPage.tsx";
import LoginPage from "./pages/LoginPage.tsx";
import NotFound from "./pages/NotFound.tsx";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/processing" element={<ProcessingPage />} />
          <Route path="/report" element={<ReportPage />} />
          <Route path="/report/:id" element={<ReportPage />} />
          <Route path="/templates" element={<TemplatesPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/saved" element={<HistoryPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/new-analysis" element={<Index />} />
          <Route path="/research" element={<Index />} />
          <Route path="/insights" element={<Index />} />
          <Route path="/strategy" element={<Index />} />
          <Route path="/campaign" element={<Index />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
