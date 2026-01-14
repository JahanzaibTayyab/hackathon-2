// Priority levels
export type TaskPriority = "low" | "medium" | "high" | "urgent";

// Recurrence types
export type RecurrenceType = "daily" | "weekly" | "monthly" | "yearly";

export interface RecurrencePattern {
  type: RecurrenceType;
  interval?: number;
  days_of_week?: number[]; // 0=Monday, 6=Sunday
  day_of_month?: number;
  end_date?: string;
  occurrences?: number;
}

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  // Phase V: Advanced fields
  due_date: string | null;
  priority: TaskPriority;
  tags: string[];
  recurrence_pattern: RecurrencePattern | null;
  next_occurrence: string | null;
  reminder_sent: boolean;
  is_overdue: boolean;
  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  due_date?: string | null;
  priority?: TaskPriority;
  tags?: string[];
  recurrence_pattern?: RecurrencePattern | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  due_date?: string | null;
  priority?: TaskPriority;
  tags?: string[];
  recurrence_pattern?: RecurrencePattern | null;
}

export interface TaskComplete {
  completed?: boolean;
}

export interface ToggleCompleteResponse extends Task {
  next_task?: Task | null;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

// Filter types
export type TaskStatus = "all" | "pending" | "completed";
export type TaskSortBy = "created_at" | "due_date" | "priority" | "title";
export type TaskOrder = "asc" | "desc";

// Legacy sort type for backward compatibility
export type TaskSort = "created" | "title" | "updated";

export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  tags?: string[];
  due_before?: string;
  due_after?: string;
  search?: string;
  sort_by?: TaskSortBy;
  order?: TaskOrder;
}

// Priority display configuration
export const PRIORITY_CONFIG: Record<TaskPriority, { label: string; color: string; bgColor: string }> = {
  low: { label: "Low", color: "text-gray-600", bgColor: "bg-gray-100" },
  medium: { label: "Medium", color: "text-blue-600", bgColor: "bg-blue-100" },
  high: { label: "High", color: "text-orange-600", bgColor: "bg-orange-100" },
  urgent: { label: "Urgent", color: "text-red-600", bgColor: "bg-red-100" },
};
