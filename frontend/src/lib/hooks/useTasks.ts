import { useState, useEffect, useCallback } from "react";
import api from "../api";

export type Task = {
  id: number;
  content: string;
  completed: boolean;
};

type Session = {
  user?: {
    id: string;
    email?: string;
    name?: string;
    image?: string | null;
  };
  session?: {
    id: string;
    token: string;
  };
} | null;

type UseTasksResult = {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  addTask: (content: string) => Promise<void>;
  updateTask: (taskId: number, content: string) => Promise<void>;
  toggleComplete: (taskId: number) => Promise<void>;
  deleteTask: (taskId: number) => Promise<void>;
  refetch: () => Promise<void>;
};

// Helper to get JWT token from Better Auth
async function getJwtToken(): Promise<string | null> {
  try {
    const url = `${process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"}/api/auth/token`;
    const response = await fetch(url, {
      credentials: "include",
    });
    if (!response.ok) {
      return null;
    }
    const data = await response.json();
    return data.token || null;
  } catch {
    return null;
  }
}

export const useTasks = (session: Session): UseTasksResult => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [jwtToken, setJwtToken] = useState<string | null>(null);

  const userId = session?.user?.id;

  // Fetch JWT token when session changes
  useEffect(() => {
    if (userId) {
      getJwtToken().then(setJwtToken);
    } else {
      setJwtToken(null);
    }
  }, [userId]);

  const fetchTasks = useCallback(async () => {
    if (!userId || !jwtToken) {
      setTasks([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const fetchedTasks = await api.get<Task[]>(jwtToken, `/api/${userId}/tasks`);
      if (Array.isArray(fetchedTasks)) {
        setTasks(fetchedTasks);
      } else {
        setTasks([]);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch tasks.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [userId, jwtToken]);

  useEffect(() => {
    if (userId && jwtToken) {
      fetchTasks();
    } else if (!userId) {
      setTasks([]);
      setLoading(false);
    }
  }, [userId, jwtToken, fetchTasks]);

  const addTask = async (content: string) => {
    if (!userId || !jwtToken) {
      setError("Not authenticated. Please sign in again.");
      setLoading(false);
      return;
    }

    // Optimistic update - add task immediately with temp id
    const tempId = Date.now();
    const newTask: Task = { id: tempId, content, completed: false };
    setTasks(prev => [...prev, newTask]);
    setError(null);

    try {
      await api.post<Task>(jwtToken, `/api/${userId}/tasks`, { content });
      // Refresh to get the real task with correct ID
      await fetchTasks();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to add task.";
      setError(errorMessage);
      // Remove the optimistic task on error
      setTasks(prev => prev.filter(t => t.id !== tempId));
      setLoading(false);
    }
  };

  const updateTask = async (taskId: number, content: string) => {
    if (!userId || !jwtToken) return;
    try {
      // Optimistic update
      setTasks(prev => prev.map(t =>
        t.id === taskId ? { ...t, content } : t
      ));
      setError(null);
      await api.put<Task>(jwtToken, `/api/${userId}/tasks/${taskId}`, { content });
    } catch {
      setError("Failed to update task.");
      await fetchTasks(); // Revert on error
    }
  };

  const toggleComplete = async (taskId: number) => {
    if (!userId || !jwtToken) return;
    try {
      // Optimistic update
      setTasks(prev => prev.map(t =>
        t.id === taskId ? { ...t, completed: !t.completed } : t
      ));
      setError(null);
      await api.patch<Task>(jwtToken, `/api/${userId}/tasks/${taskId}/complete`);
    } catch {
      setError("Failed to toggle task completion.");
      await fetchTasks(); // Revert on error
    }
  };

  const deleteTask = async (taskId: number) => {
    if (!userId || !jwtToken) return;
    try {
      // Optimistic update
      setTasks(prev => prev.filter(t => t.id !== taskId));
      setError(null);
      await api.delete(jwtToken, `/api/${userId}/tasks/${taskId}`);
    } catch {
      setError("Failed to delete task.");
      await fetchTasks(); // Revert on error
    }
  };

  return {
    tasks,
    loading,
    error,
    addTask,
    updateTask,
    toggleComplete,
    deleteTask,
    refetch: fetchTasks,
  };
};
