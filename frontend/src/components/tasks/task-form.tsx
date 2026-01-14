"use client";

import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type {
  RecurrencePattern,
  Task,
  TaskCreate,
  TaskPriority,
  TaskUpdate,
} from "@/types/task";
import { useCreateTask, useUpdateTask } from "@/lib/hooks/use-tasks";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { DatePicker } from "./date-picker";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PrioritySelect } from "./priority-select";
import { RecurrencePicker } from "./recurrence-picker";
import { TagInput } from "./tag-input";
import { Textarea } from "@/components/ui/textarea";

interface TaskFormProps {
  task?: Task;
  onCancel: () => void;
  onSuccess: () => void;
  availableTags?: string[];
}

export function TaskForm({
  task,
  onCancel,
  onSuccess,
  availableTags = [],
}: TaskFormProps) {
  const [title, setTitle] = useState(task?.title || "");
  const [description, setDescription] = useState(task?.description || "");
  const [priority, setPriority] = useState<TaskPriority>(
    task?.priority || "medium"
  );
  const [dueDate, setDueDate] = useState<string | null>(task?.due_date || null);
  const [tags, setTags] = useState<string[]>(task?.tags || []);
  const [recurrencePattern, setRecurrencePattern] =
    useState<RecurrencePattern | null>(task?.recurrence_pattern || null);

  const createTask = useCreateTask();
  const updateTask = useUpdateTask();

  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || "");
      setPriority(task.priority || "medium");
      setDueDate(task.due_date || null);
      setTags(task.tags || []);
      setRecurrencePattern(task.recurrence_pattern || null);
    }
  }, [task]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      return;
    }

    try {
      const taskData = {
        title: title.trim(),
        description: description.trim() || null,
        priority,
        due_date: dueDate,
        tags,
        recurrence_pattern: recurrencePattern,
      };

      if (task) {
        await updateTask.mutateAsync({
          id: task.id,
          data: taskData,
        });
      } else {
        await createTask.mutateAsync(taskData);
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

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Priority</Label>
              <PrioritySelect
                value={priority}
                onChange={setPriority}
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label>Due Date</Label>
              <DatePicker
                value={dueDate}
                onChange={setDueDate}
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Tags</Label>
            <TagInput
              value={tags}
              onChange={setTags}
              disabled={isLoading}
              suggestions={availableTags}
            />
          </div>

          <div className="space-y-2">
            <Label>Repeat</Label>
            <RecurrencePicker
              value={recurrencePattern}
              onChange={setRecurrencePattern}
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
