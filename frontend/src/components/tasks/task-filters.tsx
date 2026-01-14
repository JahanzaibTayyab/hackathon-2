"use client";

import { Filter, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
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
import type {
  TaskFilters as TaskFiltersType,
  TaskOrder,
  TaskPriority,
  TaskSortBy,
  TaskStatus,
} from "@/types/task";

interface TaskFiltersProps {
  filters: TaskFiltersType;
  onFiltersChange: (filters: TaskFiltersType) => void;
  availableTags?: string[];
}

export function TaskFilters({
  filters,
  onFiltersChange,
  availableTags = [],
}: TaskFiltersProps) {
  const [open, setOpen] = useState(false);

  const updateFilter = <K extends keyof TaskFiltersType>(
    key: K,
    value: TaskFiltersType[K]
  ) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    onFiltersChange({
      status: "all",
      sort_by: "created_at",
      order: "desc",
    });
  };

  const hasActiveFilters =
    filters.priority ||
    (filters.tags && filters.tags.length > 0) ||
    filters.due_before ||
    filters.due_after;

  const activeFilterCount = [
    filters.priority,
    filters.tags?.length,
    filters.due_before,
    filters.due_after,
  ].filter(Boolean).length;

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
      {/* Status filter - always visible */}
      <div className="flex-1 space-y-2">
        <Label htmlFor="status">Status</Label>
        <Select
          value={filters.status || "all"}
          onValueChange={(v) => updateFilter("status", v as TaskStatus)}
        >
          <SelectTrigger id="status">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Tasks</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Sort by - always visible */}
      <div className="flex-1 space-y-2">
        <Label htmlFor="sort">Sort By</Label>
        <Select
          value={filters.sort_by || "created_at"}
          onValueChange={(v) => updateFilter("sort_by", v as TaskSortBy)}
        >
          <SelectTrigger id="sort">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="created_at">Created Date</SelectItem>
            <SelectItem value="due_date">Due Date</SelectItem>
            <SelectItem value="priority">Priority</SelectItem>
            <SelectItem value="title">Title</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Order - always visible */}
      <div className="flex-1 space-y-2">
        <Label htmlFor="order">Order</Label>
        <Select
          value={filters.order || "desc"}
          onValueChange={(v) => updateFilter("order", v as TaskOrder)}
        >
          <SelectTrigger id="order">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="desc">Descending</SelectItem>
            <SelectItem value="asc">Ascending</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Advanced filters popover */}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" className="relative">
            <Filter className="h-4 w-4 mr-2" />
            More Filters
            {activeFilterCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-primary text-primary-foreground text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {activeFilterCount}
              </span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-80 p-4" align="end">
          <div className="space-y-4">
            <h4 className="font-medium">Advanced Filters</h4>

            {/* Priority filter */}
            <div className="space-y-2">
              <Label>Priority</Label>
              <Select
                value={filters.priority || ""}
                onValueChange={(v) =>
                  updateFilter("priority", v ? (v as TaskPriority) : undefined)
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Any priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Any priority</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Tags filter */}
            {availableTags.length > 0 && (
              <div className="space-y-2">
                <Label>Tags</Label>
                <div className="flex flex-wrap gap-1">
                  {availableTags.map((tag) => (
                    <Button
                      key={tag}
                      type="button"
                      variant={filters.tags?.includes(tag) ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        const currentTags = filters.tags || [];
                        if (currentTags.includes(tag)) {
                          updateFilter(
                            "tags",
                            currentTags.filter((t) => t !== tag)
                          );
                        } else {
                          updateFilter("tags", [...currentTags, tag]);
                        }
                      }}
                    >
                      #{tag}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {hasActiveFilters && (
              <Button
                variant="ghost"
                className="w-full text-destructive"
                onClick={clearFilters}
              >
                <X className="h-4 w-4 mr-2" />
                Clear all filters
              </Button>
            )}
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}

// Legacy interface for backward compatibility
interface LegacyTaskFiltersProps {
  status: TaskStatus;
  sort: string;
  order: TaskOrder;
  onStatusChange: (status: TaskStatus) => void;
  onSortChange: (sort: string) => void;
  onOrderChange: (order: TaskOrder) => void;
}

export function LegacyTaskFilters({
  status,
  sort,
  order,
  onStatusChange,
  onSortChange,
  onOrderChange,
}: LegacyTaskFiltersProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
      <div className="flex-1 space-y-2">
        <Label htmlFor="status">Status</Label>
        <Select value={status} onValueChange={onStatusChange}>
          <SelectTrigger id="status">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Tasks</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="flex-1 space-y-2">
        <Label htmlFor="sort">Sort By</Label>
        <Select value={sort} onValueChange={onSortChange}>
          <SelectTrigger id="sort">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="created">Created Date</SelectItem>
            <SelectItem value="title">Title</SelectItem>
            <SelectItem value="updated">Updated Date</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="flex-1 space-y-2">
        <Label htmlFor="order">Order</Label>
        <Select value={order} onValueChange={onOrderChange}>
          <SelectTrigger id="order">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="desc">Descending</SelectItem>
            <SelectItem value="asc">Ascending</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
