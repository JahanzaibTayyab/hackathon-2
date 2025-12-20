export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
}

export interface TaskComplete {
  completed?: boolean;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

export type TaskStatus = "all" | "pending" | "completed";
export type TaskSort = "created" | "title" | "updated";
export type TaskOrder = "asc" | "desc";
