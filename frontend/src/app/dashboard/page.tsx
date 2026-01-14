"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LogOut, MessageSquare, Plus } from "lucide-react";
import type { TaskFilters as TaskFiltersType } from "@/types/task";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { TaskFilters } from "@/components/tasks/task-filters";
import { TaskForm } from "@/components/tasks/task-form";
import { TaskList } from "@/components/tasks/task-list";
import { TaskSearch } from "@/components/tasks/task-search";
import { authClient } from "@/lib/auth-client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTags, useTasksWithFilters } from "@/lib/hooks/use-tasks";

export default function DashboardPage() {
  const router = useRouter();
  const [filters, setFilters] = useState<TaskFiltersType>({
    status: "all",
    sort_by: "created_at",
    order: "desc",
  });
  const [showForm, setShowForm] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const { data, isLoading, error } = useTasksWithFilters(filters);
  const { data: availableTags = [] } = useTags();

  useEffect(() => {
    // Check authentication
    authClient.getSession().then((session) => {
      if (!session.data?.session) {
        router.push("/login");
      } else {
        setIsAuthenticated(true);
      }
    });
  }, [router]);

  const handleLogout = async () => {
    await authClient.signOut();
    router.push("/login");
  };

  const handleSearchChange = (search: string) => {
    setFilters((prev) => ({ ...prev, search: search || undefined }));
  };

  if (!isAuthenticated) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-4xl p-4 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">My Tasks</h1>
            <p className="mt-2 text-muted-foreground">
              Manage your tasks and stay organized
            </p>
          </div>
          <div className="flex gap-2">
            <Link href="/chat">
              <Button variant="outline">
                <MessageSquare className="mr-2 h-4 w-4" />
                AI Chat
              </Button>
            </Link>
            <Button variant="outline" onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>

        <div className="mb-6 space-y-4">
          {/* Search bar */}
          <TaskSearch
            value={filters.search || ""}
            onChange={handleSearchChange}
            placeholder="Search tasks by title or description..."
          />

          {/* Filters */}
          <TaskFilters
            filters={filters}
            onFiltersChange={setFilters}
            availableTags={availableTags}
          />

          {!showForm && (
            <Button
              onClick={() => setShowForm(true)}
              className="w-full sm:w-auto"
            >
              <Plus className="mr-2 h-4 w-4" />
              Create New Task
            </Button>
          )}

          {showForm && (
            <TaskForm
              onCancel={() => setShowForm(false)}
              onSuccess={() => setShowForm(false)}
              availableTags={availableTags}
            />
          )}
        </div>

        {error && (
          <Card className="mb-4 border-destructive">
            <CardContent className="pt-6">
              <p className="text-sm text-destructive">
                {error instanceof Error
                  ? error.message
                  : "Failed to load tasks"}
              </p>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>
              {data?.total !== undefined
                ? `${data.total} task${data.total !== 1 ? "s" : ""}`
                : "Tasks"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <TaskList
              tasks={data?.tasks || []}
              isLoading={isLoading}
              availableTags={availableTags}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
