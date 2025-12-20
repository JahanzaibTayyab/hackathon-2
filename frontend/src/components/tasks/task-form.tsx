"use client";

import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Task, TaskCreate, TaskUpdate } from "@/types/task";
import { useCreateTask, useUpdateTask } from "@/lib/hooks/use-tasks";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { X } from "lucide-react";

interface TaskFormProps {
  task?: Task;
  onCancel: () => void;
  onSuccess: () => void;
}

export function TaskForm({ task, onCancel, onSuccess }: TaskFormProps) {
  const [title, setTitle] = useState(task?.title || "");
  const [description, setDescription] = useState(task?.description || "");
  const createTask = useCreateTask();
  const updateTask = useUpdateTask();

  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || "");
    }
  }, [task]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      return;
    }

    try {
      if (task) {
        await updateTask.mutateAsync({
          id: task.id,
          data: {
            title: title.trim(),
            description: description.trim() || null,
          },
        });
      } else {
        await createTask.mutateAsync({
          title: title.trim(),
          description: description.trim() || null,
        });
      }
      onSuccess();
    } catch (error) {
      // Error handling is done in the hooks
    }
  };

  const isLoading = createTask.isPending || updateTask.isPending;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{task ? "Edit Task" : "Create New Task"}</CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter task title"
              required
              maxLength={200}
              disabled={isLoading}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter task description (optional)"
              maxLength={1000}
              rows={3}
              disabled={isLoading}
            />
          </div>
        </CardContent>
        <CardFooter className="flex justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading || !title.trim()}>
            {isLoading
              ? task
                ? "Updating..."
                : "Creating..."
              : task
              ? "Update"
              : "Create"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
