"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LogOut, Plus } from "lucide-react";
import type { TaskOrder, TaskSort, TaskStatus } from "@/types/task";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { TaskFilters } from "@/components/tasks/task-filters";
import { TaskForm } from "@/components/tasks/task-form";
import { TaskList } from "@/components/tasks/task-list";
import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { useTasks } from "@/lib/hooks/use-tasks";

export default function DashboardPage() {
  const router = useRouter();
  const [status, setStatus] = useState<TaskStatus>("all");
  const [sort, setSort] = useState<TaskSort>("created");
  const [order, setOrder] = useState<TaskOrder>("desc");
  const [showForm, setShowForm] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const { data, isLoading, error } = useTasks(status, sort, order);

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
          <Button variant="outline" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>

        <div className="mb-6 space-y-4">
          <TaskFilters
            status={status}
            sort={sort}
            order={order}
            onStatusChange={setStatus}
            onSortChange={setSort}
            onOrderChange={setOrder}
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
            <TaskList tasks={data?.tasks || []} isLoading={isLoading} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
