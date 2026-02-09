import { useState, useEffect, useCallback } from "react";
import api from "../api";
import { authClient } from "../auth-client";

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
    image?: string;
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
    // The JWT plugin exposes a /api/auth/token endpoint
    const url = `${process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"}/api/auth/token`;
    console.log("Fetching JWT token from:", url);
    const response = await fetch(url, {
      credentials: "include",
    });
    console.log("Token response status:", response.status);
    if (!response.ok) {
      console.error("Token fetch failed:", response.status, response.statusText);
      return null;
    }
    const data = await response.json();
    console.log("Token response data:", data);
    return data.token || null;
  } catch (err) {
    console.error("Token fetch error:", err);
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
      console.log("Fetching tasks for user:", userId);
      const fetchedTasks = await api.get(jwtToken, `/api/${userId}/tasks`);
      console.log("Fetched tasks:", fetchedTasks);
      if (Array.isArray(fetchedTasks)) {
        setTasks(fetchedTasks);
      } else {
        console.warn("Unexpected response format:", fetchedTasks);
        setTasks([]);
      }
    } catch (err: any) {
      console.error("Failed to fetch tasks:", err);
      setError(err.message || "Failed to fetch tasks.");
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
    console.log("addTask called:", { userId, jwtToken: jwtToken ? "exists" : "null", content });
    if (!userId || !jwtToken) {
      console.error("Cannot add task: missing userId or jwtToken");
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
      const result = await api.post(jwtToken, `/api/${userId}/tasks`, { content });
      console.log("Task created:", result);

      // Refresh to get the real task with correct ID
      await fetchTasks();
    } catch (err: any) {
      console.error("Failed to add task:", err);
      setError(err.message || "Failed to add task.");
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
      await api.put(jwtToken, `/api/${userId}/tasks/${taskId}`, { content });
    } catch (err) {
      console.error("Failed to update task:", err);
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
      await api.patch(jwtToken, `/api/${userId}/tasks/${taskId}/complete`);
    } catch (err) {
      console.error("Failed to toggle task completion:", err);
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
    } catch (err) {
      console.error("Failed to delete task:", err);
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
