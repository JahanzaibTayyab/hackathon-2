"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { TaskOrder, TaskSort, TaskStatus } from "@/types/task";

import { Label } from "@/components/ui/label";

interface TaskFiltersProps {
  status: TaskStatus;
  sort: TaskSort;
  order: TaskOrder;
  onStatusChange: (status: TaskStatus) => void;
  onSortChange: (sort: TaskSort) => void;
  onOrderChange: (order: TaskOrder) => void;
}

export function TaskFilters({
  status,
  sort,
  order,
  onStatusChange,
  onSortChange,
  onOrderChange,
}: TaskFiltersProps) {
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
