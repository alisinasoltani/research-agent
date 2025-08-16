// src/components/dev-panel.tsx
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";

interface DevPanelProps {
  onToggle: () => void;
}

export function DevPanel({ onToggle }: DevPanelProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between pb-4">
        <h3 className="text-lg font-semibold">Developer Panel</h3>
        <Button variant="ghost" size="icon" onClick={onToggle}>
          <X className="h-4 w-4" />
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto text-sm text-gray-500">
        <p>Raw WebSocket events will be displayed here.</p>
      </div>
    </div>
  );
}
