import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";

import type { Task } from "@/types/task";
import { TaskItem } from "@/components/tasks/task-item";
import userEvent from "@testing-library/user-event";

// Mock the hooks
const mockToggleMutateAsync = jest.fn().mockResolvedValue({});
const mockDeleteMutateAsync = jest.fn().mockResolvedValue({});
const mockCreateMutateAsync = jest.fn().mockResolvedValue({});
const mockUpdateMutateAsync = jest.fn().mockResolvedValue({});

jest.mock("@/lib/hooks/use-tasks", () => ({
  useToggleComplete: jest.fn(() => ({
    mutateAsync: mockToggleMutateAsync,
    isPending: false,
  })),
  useDeleteTask: jest.fn(() => ({
    mutateAsync: mockDeleteMutateAsync,
    isPending: false,
  })),
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
    renderWithProviders(<TaskItem task={mockTask} />);
    // The check button is the first button in the component
    const buttons = screen.getAllByRole("button");
    const checkButton = buttons[0];
    await userEvent.click(checkButton);

    await waitFor(() => {
      expect(mockToggleMutateAsync).toHaveBeenCalledWith({
        id: 1,
        data: { completed: true },
      });
    });
  });

  it("calls delete when delete button is clicked and confirmed", async () => {
    renderWithProviders(<TaskItem task={mockTask} />);
    // Buttons order: check (0), edit (1), delete (2)
    const buttons = screen.getAllByRole("button");
    const deleteButton = buttons[2];

    await userEvent.click(deleteButton);
    await waitFor(() => {
      expect(window.confirm).toHaveBeenCalled();
      expect(mockDeleteMutateAsync).toHaveBeenCalledWith(1);
    });
  });

  it("shows edit form when edit button is clicked", async () => {
    renderWithProviders(<TaskItem task={mockTask} />);
    // Buttons order: check (0), edit (1), delete (2)
    const buttons = screen.getAllByRole("button");
    const editButton = buttons[1];

    await userEvent.click(editButton);
    expect(screen.getByText("Edit Task")).toBeInTheDocument();
  });
});
