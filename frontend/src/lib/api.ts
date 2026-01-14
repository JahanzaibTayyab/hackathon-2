import type {
  Task,
  TaskComplete,
  TaskCreate,
  TaskFilters,
  TaskListResponse,
  TaskOrder,
  TaskSort,
  TaskStatus,
  TaskUpdate,
  ToggleCompleteResponse,
} from "@/types/task";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class APIError extends Error {
  constructor(message: string, public status: number, public data?: any) {
    super(message);
    this.name = "APIError";
  }
}

async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {},
  getToken?: () => Promise<string | null>
): Promise<Response> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (getToken) {
    const token = await getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Unknown error" }));
    throw new APIError(
      error.detail || "API request failed",
      response.status,
      error
    );
  }

  return response;
}

export const api = {
  // Task operations
  tasks: {
    list: async (
      filters: TaskFilters = {},
      getToken?: () => Promise<string | null>
    ): Promise<TaskListResponse> => {
      const params = new URLSearchParams();

      // Add filter parameters
      if (filters.status && filters.status !== "all") {
        params.append("status", filters.status);
      }
      if (filters.priority) {
        params.append("priority", filters.priority);
      }
      if (filters.tags && filters.tags.length > 0) {
        filters.tags.forEach((tag) => params.append("tags", tag));
      }
      if (filters.due_before) {
        params.append("due_before", filters.due_before);
      }
      if (filters.due_after) {
        params.append("due_after", filters.due_after);
      }
      if (filters.search) {
        params.append("search", filters.search);
      }
      if (filters.sort_by) {
        params.append("sort_by", filters.sort_by);
      }
      if (filters.order) {
        params.append("order", filters.order);
      }

      const queryString = params.toString();
      const response = await fetchWithAuth(
        `/api/v1/tasks${queryString ? `?${queryString}` : ""}`,
        {},
        getToken
      );
      return response.json();
    },

    // Legacy list method for backwards compatibility
    listLegacy: async (
      status: TaskStatus = "all",
      sort: TaskSort = "created",
      order: TaskOrder = "desc",
      getToken?: () => Promise<string | null>
    ): Promise<TaskListResponse> => {
      // Map legacy sort values to new sort_by values
      const sortByMap: Record<string, string> = {
        created: "created_at",
        title: "title",
        updated: "updated_at",
      };
      return api.tasks.list(
        {
          status,
          sort_by: sortByMap[sort] as TaskFilters["sort_by"],
          order,
        },
        getToken
      );
    },

    get: async (
      id: number,
      getToken?: () => Promise<string | null>
    ): Promise<Task> => {
      const response = await fetchWithAuth(`/api/v1/tasks/${id}`, {}, getToken);
      return response.json();
    },

    create: async (
      data: TaskCreate,
      getToken?: () => Promise<string | null>
    ): Promise<Task> => {
      const response = await fetchWithAuth(
        "/api/v1/tasks",
        {
          method: "POST",
          body: JSON.stringify(data),
        },
        getToken
      );
      return response.json();
    },

    update: async (
      id: number,
      data: TaskUpdate,
      getToken?: () => Promise<string | null>
    ): Promise<Task> => {
      const response = await fetchWithAuth(
        `/api/v1/tasks/${id}`,
        {
          method: "PUT",
          body: JSON.stringify(data),
        },
        getToken
      );
      return response.json();
    },

    toggleComplete: async (
      id: number,
      data: TaskComplete | undefined,
      getToken?: () => Promise<string | null>
    ): Promise<ToggleCompleteResponse> => {
      const response = await fetchWithAuth(
        `/api/v1/tasks/${id}/complete`,
        {
          method: "PATCH",
          body: JSON.stringify(data || {}),
        },
        getToken
      );
      return response.json();
    },

    delete: async (
      id: number,
      getToken?: () => Promise<string | null>
    ): Promise<void> => {
      await fetchWithAuth(
        `/api/v1/tasks/${id}`,
        {
          method: "DELETE",
        },
        getToken
      );
    },

    // Get all unique tags for the user
    getTags: async (
      getToken?: () => Promise<string | null>
    ): Promise<string[]> => {
      const response = await fetchWithAuth(`/api/v1/tasks/tags`, {}, getToken);
      return response.json();
    },
  },
};

export { APIError };
