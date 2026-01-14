"use client";

import { Repeat, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { RecurrencePattern, RecurrenceType } from "@/types/task";

interface RecurrencePickerProps {
  value: RecurrencePattern | null;
  onChange: (value: RecurrencePattern | null) => void;
  disabled?: boolean;
}

const DAYS_OF_WEEK = [
  { value: 0, label: "Mon" },
  { value: 1, label: "Tue" },
  { value: 2, label: "Wed" },
  { value: 3, label: "Thu" },
  { value: 4, label: "Fri" },
  { value: 5, label: "Sat" },
  { value: 6, label: "Sun" },
];

export function RecurrencePicker({
  value,
  onChange,
  disabled,
}: RecurrencePickerProps) {
  const [open, setOpen] = useState(false);
  const [type, setType] = useState<RecurrenceType>(value?.type || "weekly");
  const [interval, setInterval] = useState(value?.interval || 1);
  const [daysOfWeek, setDaysOfWeek] = useState<number[]>(
    value?.days_of_week || [0]
  );

  const handleSave = () => {
    const pattern: RecurrencePattern = {
      type,
      interval,
    };
    if (type === "weekly") {
      pattern.days_of_week = daysOfWeek;
    }
    onChange(pattern);
    setOpen(false);
  };

  const handleClear = () => {
    onChange(null);
    setType("weekly");
    setInterval(1);
    setDaysOfWeek([0]);
    setOpen(false);
  };

  const toggleDay = (day: number) => {
    if (daysOfWeek.includes(day)) {
      if (daysOfWeek.length > 1) {
        setDaysOfWeek(daysOfWeek.filter((d) => d !== day));
      }
    } else {
      setDaysOfWeek([...daysOfWeek, day].sort());
    }
  };

  const getDisplayText = () => {
    if (!value) return "No recurrence";

    const typeText = {
      daily: "day",
      weekly: "week",
      monthly: "month",
      yearly: "year",
    }[value.type];

    let text = `Every ${value.interval === 1 ? "" : value.interval + " "}${typeText}${
      (value.interval || 1) > 1 ? "s" : ""
    }`;

    if (value.type === "weekly" && value.days_of_week) {
      const dayNames = value.days_of_week.map(
        (d) => DAYS_OF_WEEK.find((day) => day.value === d)?.label
      );
      text += ` on ${dayNames.join(", ")}`;
    }

    return text;
  };

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
          <Repeat className="mr-2 h-4 w-4" />
          {getDisplayText()}
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
      <PopoverContent className="w-80 p-4" align="start">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Repeat</Label>
            <Select value={type} onValueChange={(v) => setType(v as RecurrenceType)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="yearly">Yearly</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Every</Label>
            <div className="flex items-center gap-2">
              <Input
                type="number"
                min={1}
                max={365}
                value={interval}
                onChange={(e) => setInterval(parseInt(e.target.value) || 1)}
                className="w-20"
              />
              <span className="text-sm text-muted-foreground">
                {type === "daily"
                  ? "day(s)"
                  : type === "weekly"
                  ? "week(s)"
                  : type === "monthly"
                  ? "month(s)"
                  : "year(s)"}
              </span>
            </div>
          </div>

          {type === "weekly" && (
            <div className="space-y-2">
              <Label>On days</Label>
              <div className="flex flex-wrap gap-1">
                {DAYS_OF_WEEK.map((day) => (
                  <Button
                    key={day.value}
                    type="button"
                    variant={daysOfWeek.includes(day.value) ? "default" : "outline"}
                    size="sm"
                    className="w-10"
                    onClick={() => toggleDay(day.value)}
                  >
                    {day.label}
                  </Button>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-2 pt-2">
            <Button variant="outline" className="flex-1" onClick={handleClear}>
              Clear
            </Button>
            <Button className="flex-1" onClick={handleSave}>
              Save
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

// Display badge for recurring tasks
export function RecurrenceBadge({ pattern }: { pattern: RecurrencePattern | null }) {
  if (!pattern) return null;

  return (
    <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
      <Repeat className="h-3 w-3" />
      {pattern.type}
    </span>
  );
}
