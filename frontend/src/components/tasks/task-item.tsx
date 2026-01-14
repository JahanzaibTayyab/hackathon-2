"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Check, Edit2, Trash2 } from "lucide-react";
import { useDeleteTask, useToggleComplete } from "@/lib/hooks/use-tasks";

import { Button } from "@/components/ui/button";
import { DueDateDisplay } from "./date-picker";
import { PriorityBadge } from "./priority-select";
import { RecurrenceBadge } from "./recurrence-picker";
import type { Task } from "@/types/task";
import { TagDisplay } from "./tag-input";
import { TaskForm } from "./task-form";
import { useState } from "react";

interface TaskItemProps {
  task: Task;
  availableTags?: string[];
}

export function TaskItem({ task, availableTags = [] }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const toggleComplete = useToggleComplete();
  const deleteTask = useDeleteTask();

  const handleToggle = async () => {
    await toggleComplete.mutateAsync({
      id: task.id,
      data: { completed: !task.completed },
    });
  };

  const handleDelete = async () => {
    if (confirm("Are you sure you want to delete this task?")) {
      await deleteTask.mutateAsync(task.id);
    }
  };

  if (isEditing) {
    return (
      <TaskForm
        task={task}
        onCancel={() => setIsEditing(false)}
        onSuccess={() => setIsEditing(false)}
        availableTags={availableTags}
      />
    );
  }

  return (
    <Card
      className={`${task.completed ? "opacity-60" : ""} ${
        task.is_overdue && !task.completed ? "border-red-500/50" : ""
      }`}
    >
      <CardContent className="flex items-start gap-4 p-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleToggle}
          disabled={toggleComplete.isPending}
          className="mt-1"
        >
          <Check
            className={`h-5 w-5 ${
              task.completed ? "text-primary" : "text-muted-foreground"
            }`}
          />
        </Button>
        <div className="flex-1 space-y-2">
          <div className="flex items-start gap-2">
            <h3
              className={`font-medium flex-1 ${
                task.completed ? "line-through text-muted-foreground" : ""
              }`}
            >
              {task.title}
            </h3>
            <PriorityBadge priority={task.priority} />
          </div>
          {task.description && (
            <p className="text-sm text-muted-foreground">{task.description}</p>
          )}

          {/* Tags */}
          <TagDisplay tags={task.tags} />

          {/* Metadata row */}
          <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
            <DueDateDisplay
              dueDate={task.due_date}
              isOverdue={task.is_overdue || false}
            />
            <RecurrenceBadge pattern={task.recurrence_pattern} />
            <span>
              Created: {new Date(task.created_at).toLocaleDateString()}
            </span>
            {task.updated_at !== task.created_at && (
              <span>
                Updated: {new Date(task.updated_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsEditing(true)}
            disabled={deleteTask.isPending}
          >
            <Edit2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleDelete}
            disabled={deleteTask.isPending}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
