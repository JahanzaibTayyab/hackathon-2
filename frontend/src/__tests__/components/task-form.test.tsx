import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";

import type { Task } from "@/types/task";
import { TaskForm } from "@/components/tasks/task-form";
import userEvent from "@testing-library/user-event";

// Mock the hooks
const mockCreateMutateAsync = jest.fn().mockResolvedValue({});
const mockUpdateMutateAsync = jest.fn().mockResolvedValue({});

jest.mock("@/lib/hooks/use-tasks", () => ({
  useCreateTask: jest.fn(() => ({
    mutateAsync: mockCreateMutateAsync,
    isPending: false,
  })),
  useUpdateTask: jest.fn(() => ({
    mutateAsync: mockUpdateMutateAsync,
    isPending: false,
  })),
}));

const createQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
};

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
};

describe("TaskForm", () => {
  const mockOnCancel = jest.fn();
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders create form when no task provided", () => {
    renderWithProviders(
      <TaskForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />
    );
    expect(screen.getByText("Create New Task")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Enter task title")).toBeInTheDocument();
  });

  it("renders edit form when task is provided", () => {
    const mockTask: Task = {
      id: 1,
      user_id: "user-123",
      title: "Existing Task",
      description: "Existing Description",
      completed: false,
      created_at: "2025-01-01T00:00:00Z",
      updated_at: "2025-01-01T00:00:00Z",
    };

    renderWithProviders(
      <TaskForm
        task={mockTask}
        onCancel={mockOnCancel}
        onSuccess={mockOnSuccess}
      />
    );
    expect(screen.getByText("Edit Task")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Existing Task")).toBeInTheDocument();
    expect(
      screen.getByDisplayValue("Existing Description")
    ).toBeInTheDocument();
  });

  it("calls onSuccess after successful create", async () => {
    renderWithProviders(
      <TaskForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />
    );

    const titleInput = screen.getByPlaceholderText("Enter task title");
    await userEvent.type(titleInput, "New Task");
    await userEvent.click(screen.getByText("Create"));

    await waitFor(() => {
      expect(mockCreateMutateAsync).toHaveBeenCalledWith({
        title: "New Task",
        description: null,
        due_date: null,
        priority: "medium",
        tags: [],
        recurrence_pattern: null,
      });
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it("calls onCancel when cancel button is clicked", async () => {
    renderWithProviders(
      <TaskForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />
    );

    await userEvent.click(screen.getByText("Cancel"));
    expect(mockOnCancel).toHaveBeenCalled();
  });

  it("disables submit button when title is empty", () => {
    renderWithProviders(
      <TaskForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />
    );

    const submitButton = screen.getByText("Create");
    expect(submitButton).toBeDisabled();
  });

  it("allows submitting with just title", async () => {
    renderWithProviders(
      <TaskForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />
    );

    const titleInput = screen.getByPlaceholderText("Enter task title");
    await userEvent.type(titleInput, "Task Without Description");
    await userEvent.click(screen.getByText("Create"));

    await waitFor(() => {
      expect(mockCreateMutateAsync).toHaveBeenCalledWith({
        title: "Task Without Description",
        description: null,
        due_date: null,
        priority: "medium",
        tags: [],
        recurrence_pattern: null,
      });
    });
  });
});
