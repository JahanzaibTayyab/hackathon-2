"use client";

import { format, formatDistanceToNow, isPast, parseISO } from "date-fns";
import { Calendar, X } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

interface DatePickerProps {
  value: string | null;
  onChange: (value: string | null) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function DatePicker({
  value,
  onChange,
  disabled,
  placeholder = "Select due date",
}: DatePickerProps) {
  const [open, setOpen] = useState(false);
  const [dateInput, setDateInput] = useState("");
  const [timeInput, setTimeInput] = useState("12:00");

  useEffect(() => {
    if (value) {
      const date = parseISO(value);
      setDateInput(format(date, "yyyy-MM-dd"));
      setTimeInput(format(date, "HH:mm"));
    } else {
      setDateInput("");
      setTimeInput("12:00");
    }
  }, [value]);

  const handleDateChange = (newDate: string) => {
    setDateInput(newDate);
    if (newDate) {
      const datetime = `${newDate}T${timeInput}:00`;
      onChange(datetime);
    }
  };

  const handleTimeChange = (newTime: string) => {
    setTimeInput(newTime);
    if (dateInput) {
      const datetime = `${dateInput}T${newTime}:00`;
      onChange(datetime);
    }
  };

  const handleClear = () => {
    onChange(null);
    setDateInput("");
    setTimeInput("12:00");
  };

  const displayValue = value
    ? format(parseISO(value), "MMM d, yyyy 'at' h:mm a")
    : placeholder;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={`w-full justify-start text-left font-normal ${
            !value ? "text-muted-foreground" : ""
          }`}
          disabled={disabled}
        >
          <Calendar className="mr-2 h-4 w-4" />
          {displayValue}
          {value && (
            <X
              className="ml-auto h-4 w-4 hover:text-destructive"
              onClick={(e) => {
                e.stopPropagation();
                handleClear();
              }}
            />
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-4" align="start">
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Date</label>
            <Input
              type="date"
              value={dateInput}
              onChange={(e) => handleDateChange(e.target.value)}
              className="w-full"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Time</label>
            <Input
              type="time"
              value={timeInput}
              onChange={(e) => handleTimeChange(e.target.value)}
              className="w-full"
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const today = format(new Date(), "yyyy-MM-dd");
                handleDateChange(today);
              }}
            >
              Today
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                handleDateChange(format(tomorrow, "yyyy-MM-dd"));
              }}
            >
              Tomorrow
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const nextWeek = new Date();
                nextWeek.setDate(nextWeek.getDate() + 7);
                handleDateChange(format(nextWeek, "yyyy-MM-dd"));
              }}
            >
              Next Week
            </Button>
          </div>
          {value && (
            <Button
              variant="ghost"
              size="sm"
              className="w-full text-destructive"
              onClick={handleClear}
            >
              Clear date
            </Button>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}

// Display component for showing due date in task items
export function DueDateDisplay({ dueDate, isOverdue }: { dueDate: string | null; isOverdue: boolean }) {
  if (!dueDate) return null;

  const date = parseISO(dueDate);
  const isInPast = isPast(date);
  const relative = formatDistanceToNow(date, { addSuffix: true });

  return (
    <span
      className={`inline-flex items-center gap-1 text-xs ${
        isOverdue || isInPast ? "text-red-600 font-medium" : "text-muted-foreground"
      }`}
    >
      <Calendar className="h-3 w-3" />
      {isOverdue ? "Overdue: " : "Due "}
      {relative}
    </span>
  );
}

// Popover component for UI
export function PopoverUI({
  children,
  ...props
}: React.ComponentProps<typeof Popover>) {
  return <Popover {...props}>{children}</Popover>;
}
