import type {
  Task,
  TaskComplete,
  TaskCreate,
  TaskListResponse,
  TaskOrder,
  TaskSort,
  TaskStatus,
  TaskUpdate,
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
      status: TaskStatus = "all",
      sort: TaskSort = "created",
      order: TaskOrder = "desc",
      getToken?: () => Promise<string | null>
    ): Promise<TaskListResponse> => {
      const params = new URLSearchParams({ status, sort, order });
      const response = await fetchWithAuth(
        `/api/v1/tasks?${params}`,
        {},
        getToken
      );
      return response.json();
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
    ): Promise<Task> => {
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
  },
};

export { APIError };
