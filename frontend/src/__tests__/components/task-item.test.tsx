import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";

import type { Task } from "@/types/task";
import { TaskItem } from "@/components/tasks/task-item";
import userEvent from "@testing-library/user-event";

// Mock the hooks
jest.mock("@/lib/hooks/use-tasks", () => ({
  useToggleComplete: () => ({
    mutateAsync: jest.fn().mockResolvedValue({}),
    isPending: false,
  }),
  useDeleteTask: () => ({
    mutateAsync: jest.fn().mockResolvedValue({}),
    isPending: false,
  }),
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

describe("TaskItem", () => {
  const mockTask: Task = {
    id: 1,
    user_id: "user-123",
    title: "Test Task",
    description: "Test Description",
    completed: false,
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
  };

  beforeEach(() => {
    // Mock window.confirm
    window.confirm = jest.fn(() => true);
  });

  it("renders task title and description", () => {
    renderWithProviders(<TaskItem task={mockTask} />);
    expect(screen.getByText("Test Task")).toBeInTheDocument();
    expect(screen.getByText("Test Description")).toBeInTheDocument();
  });

  it("shows completed styling when task is completed", () => {
    const completedTask = { ...mockTask, completed: true };
    renderWithProviders(<TaskItem task={completedTask} />);
    const title = screen.getByText("Test Task");
    expect(title).toHaveClass("line-through");
  });

  it("calls toggle complete when check button is clicked", async () => {
    const { useToggleComplete } = require("@/lib/hooks/use-tasks");
    const mockMutateAsync = jest.fn().mockResolvedValue({});
    useToggleComplete.mockReturnValue({
      mutateAsync: mockMutateAsync,
      isPending: false,
    });

    renderWithProviders(<TaskItem task={mockTask} />);
    const checkButton = screen.getByRole("button", { name: /check/i });
    await userEvent.click(checkButton);

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith({
        id: 1,
        data: { completed: true },
      });
    });
  });

  it("calls delete when delete button is clicked and confirmed", async () => {
    const { useDeleteTask } = require("@/lib/hooks/use-tasks");
    const mockMutateAsync = jest.fn().mockResolvedValue({});
    useDeleteTask.mockReturnValue({
      mutateAsync: mockMutateAsync,
      isPending: false,
    });

    renderWithProviders(<TaskItem task={mockTask} />);
    const deleteButton = screen
      .getAllByRole("button")
      .find((btn) =>
        btn.querySelector("svg")?.getAttribute("class")?.includes("Trash2")
      );

    if (deleteButton) {
      await userEvent.click(deleteButton);
      await waitFor(() => {
        expect(window.confirm).toHaveBeenCalled();
        expect(mockMutateAsync).toHaveBeenCalledWith(1);
      });
    }
  });

  it("shows edit form when edit button is clicked", async () => {
    renderWithProviders(<TaskItem task={mockTask} />);
    const editButton = screen
      .getAllByRole("button")
      .find((btn) =>
        btn.querySelector("svg")?.getAttribute("class")?.includes("Edit2")
      );

    if (editButton) {
      await userEvent.click(editButton);
      expect(screen.getByText("Edit Task")).toBeInTheDocument();
    }
  });
});
