const getApiUrl = () => {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
};

// Helper to add timeout to fetch requests
// Set to 60 seconds to handle Neon database wake-up
const fetchWithTimeout = async (url: string, options: RequestInit, timeout = 60000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error: unknown) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timeout - server took too long to respond');
      }
      if (error.message === 'Failed to fetch' || error.message?.includes('fetch')) {
        throw new Error(`Cannot connect to backend. Please check if the server is running.`);
      }
    }
    throw error;
  }
};

interface ApiResponse<T = unknown> {
  data?: T;
  error?: string;
}

const api = {
  async get<T = unknown>(token: string | undefined, path: string): Promise<T> {
    if (!token) {
      throw new Error("No authentication token");
    }
    const res = await fetchWithTimeout(`${getApiUrl()}${path}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) {
      throw new Error(`API error: ${res.status}`);
    }
    return res.json();
  },

  async post<T = unknown, D = unknown>(token: string | undefined, path: string, data: D): Promise<T> {
    const res = await fetchWithTimeout(`${getApiUrl()}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`API error: ${res.status} - ${errorText}`);
    }
    return res.json();
  },

  async put<T = unknown, D = unknown>(token: string | undefined, path: string, data: D): Promise<T> {
    const res = await fetchWithTimeout(`${getApiUrl()}${path}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`API error: ${res.status} - ${errorText}`);
    }
    return res.json();
  },

  async delete(token: string | undefined, path: string): Promise<void> {
    const res = await fetchWithTimeout(`${getApiUrl()}${path}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok && res.status !== 204) {
      throw new Error(`API error: ${res.status}`);
    }
  },

  async patch<T = unknown>(token: string | undefined, path: string): Promise<T> {
    const res = await fetchWithTimeout(`${getApiUrl()}${path}`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) {
      throw new Error(`API error: ${res.status}`);
    }
    return res.json();
  },
};

export default api;
