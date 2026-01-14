"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PRIORITY_CONFIG, type TaskPriority } from "@/types/task";

interface PrioritySelectProps {
  value: TaskPriority;
  onChange: (value: TaskPriority) => void;
  disabled?: boolean;
}

const priorities: TaskPriority[] = ["low", "medium", "high", "urgent"];

export function PrioritySelect({ value, onChange, disabled }: PrioritySelectProps) {
  return (
    <Select value={value} onValueChange={onChange} disabled={disabled}>
      <SelectTrigger className="w-full">
        <SelectValue placeholder="Select priority">
          {value && (
            <div className="flex items-center gap-2">
              <span
                className={`w-2 h-2 rounded-full ${
                  value === "low"
                    ? "bg-gray-400"
                    : value === "medium"
                    ? "bg-blue-400"
                    : value === "high"
                    ? "bg-orange-400"
                    : "bg-red-500"
                }`}
              />
              {PRIORITY_CONFIG[value].label}
            </div>
          )}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {priorities.map((p) => (
          <SelectItem key={p} value={p}>
            <div className="flex items-center gap-2">
              <span
                className={`w-2 h-2 rounded-full ${
                  p === "low"
                    ? "bg-gray-400"
                    : p === "medium"
                    ? "bg-blue-400"
                    : p === "high"
                    ? "bg-orange-400"
                    : "bg-red-500"
                }`}
              />
              {PRIORITY_CONFIG[p].label}
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

// Badge version for displaying priority in task items
export function PriorityBadge({ priority }: { priority: TaskPriority | undefined | null }) {
  // Default to medium if priority is not set
  const effectivePriority = priority ?? "medium";
  const config = PRIORITY_CONFIG[effectivePriority];
  if (!config) return null;
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${config.bgColor} ${config.color}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          effectivePriority === "low"
            ? "bg-gray-500"
            : effectivePriority === "medium"
            ? "bg-blue-500"
            : effectivePriority === "high"
            ? "bg-orange-500"
            : "bg-red-500"
        }`}
      />
      {config.label}
    </span>
  );
}
