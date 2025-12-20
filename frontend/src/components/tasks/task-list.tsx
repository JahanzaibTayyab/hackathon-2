"use client";

import type { Task } from "@/types/task";
import { TaskItem } from "./task-item";

interface TaskListProps {
  tasks: Task[];
  isLoading?: boolean;
}

export function TaskList({ tasks, isLoading }: TaskListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-lg font-medium text-muted-foreground">
          No tasks found
        </p>
        <p className="mt-2 text-sm text-muted-foreground">
          Create your first task to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <TaskItem key={task.id} task={task} />
      ))}
    </div>
  );
}
