"use client";

import { APIError, api } from "@/lib/api";
import type {
  Task,
  TaskComplete,
  TaskCreate,
  TaskFilters,
  TaskOrder,
  TaskSort,
  TaskStatus,
  TaskUpdate,
  ToggleCompleteResponse,
} from "@/types/task";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

async function getAuthToken(): Promise<string | null> {
  try {
    // Better Auth with JWT plugin provides tokens via the /api/auth/token endpoint
    const baseURL =
      process.env.NEXT_PUBLIC_BASE_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:3000";
    const response = await fetch(`${baseURL}/api/auth/token`, {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      // Better Auth returns token in different formats, check common fields
      return data.token || data.accessToken || data.jwt || null;
    }

    return null;
  } catch (error) {
    console.error("Failed to get auth token:", error);
    return null;
  }
}

// Main hook with advanced filters
export function useTasksWithFilters(filters: TaskFilters = {}) {
  return useQuery({
    queryKey: ["tasks", filters],
    queryFn: async () => {
      const token = await getAuthToken();
      if (!token) {
        throw new APIError("Not authenticated", 401);
      }
      return api.tasks.list(filters, getAuthToken);
    },
  });
}

// Legacy hook for backwards compatibility
export function useTasks(
  status: TaskStatus = "all",
  sort: TaskSort = "created",
  order: TaskOrder = "desc"
) {
  // Map legacy sort values to new sort_by values
  const sortByMap: Record<string, TaskFilters["sort_by"]> = {
    created: "created_at",
    title: "title",
    updated: "created_at", // updated is mapped to created_at for now
  };

  const filters: TaskFilters = {
    status,
    sort_by: sortByMap[sort],
    order,
  };

  return useQuery({
    queryKey: ["tasks", status, sort, order],
    queryFn: async () => {
      const token = await getAuthToken();
      if (!token) {
        throw new APIError("Not authenticated", 401);
      }
      return api.tasks.list(filters, getAuthToken);
    },
  });
}

export function useTask(id: number) {
  return useQuery({
    queryKey: ["task", id],
    queryFn: async () => {
      const token = await getAuthToken();
      if (!token) {
        throw new APIError("Not authenticated", 401);
      }
      return api.tasks.get(id, getAuthToken);
    },
    enabled: !!id,
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: TaskCreate) => {
      const token = await getAuthToken();
      if (!token) {
        throw new APIError("Not authenticated", 401);
      }
      return api.tasks.create(data, getAuthToken);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["tags"] });
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: TaskUpdate }) => {
      const token = await getAuthToken();
      if (!token) {
        throw new APIError("Not authenticated", 401);
      }
      return api.tasks.update(id, data, getAuthToken);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["task", variables.id] });
      queryClient.invalidateQueries({ queryKey: ["tags"] });
    },
  });
}

export function useToggleComplete() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: number;
      data?: TaskComplete;
    }): Promise<ToggleCompleteResponse> => {
      const token = await getAuthToken();
      if (!token) {
        throw new APIError("Not authenticated", 401);
      }
      return api.tasks.toggleComplete(id, data, getAuthToken);
    },
    onSuccess: (response, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["task", variables.id] });
      // If a recurring task created a next task, it will be in the tasks list
      if (response.next_task) {
        queryClient.invalidateQueries({ queryKey: ["tasks"] });
      }
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const token = await getAuthToken();
      if (!token) {
        throw new APIError("Not authenticated", 401);
      }
      return api.tasks.delete(id, getAuthToken);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

// Hook for fetching all unique tags
export function useTags() {
  return useQuery({
    queryKey: ["tags"],
    queryFn: async () => {
      const token = await getAuthToken();
      if (!token) {
        throw new APIError("Not authenticated", 401);
      }
      return api.tasks.getTags(getAuthToken);
    },
  });
}
