"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Check, Edit2, Trash2 } from "lucide-react";
import { useDeleteTask, useToggleComplete } from "@/lib/hooks/use-tasks";

import { Button } from "@/components/ui/button";
import type { Task } from "@/types/task";
import { TaskForm } from "./task-form";
import { useState } from "react";

interface TaskItemProps {
  task: Task;
}

export function TaskItem({ task }: TaskItemProps) {
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
      />
    );
  }

  return (
    <Card className={task.completed ? "opacity-60" : ""}>
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
        <div className="flex-1 space-y-1">
          <h3
            className={`font-medium ${
              task.completed ? "line-through text-muted-foreground" : ""
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p className="text-sm text-muted-foreground">{task.description}</p>
          )}
          <div className="flex gap-2 text-xs text-muted-foreground">
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
