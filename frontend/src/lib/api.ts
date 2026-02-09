const getApiUrl = () => {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
};

// Helper to add timeout to fetch requests
// Set to 60 seconds to handle Neon database wake-up
const fetchWithTimeout = async (url: string, options: RequestInit, timeout = 60000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    console.log(`[API] Fetching: ${url}`);
    console.log(`[API] Options:`, options);
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    console.log(`[API] Response status: ${response.status}`);
    clearTimeout(timeoutId);
    return response;
  } catch (error: any) {
    clearTimeout(timeoutId);
    console.error(`[API] Fetch failed for ${url}:`, error);
    console.error(`[API] Error type: ${typeof error}`);
    console.error(`[API] Error name: ${error?.name}`);
    console.error(`[API] Error message: ${error?.message}`);
    console.error(`[API] Error stack:`, error?.stack);

    if (error?.name === 'AbortError') {
      throw new Error('Request timeout - server took too long to respond');
    }
    if (error?.message === 'Failed to fetch' || error?.message?.includes('fetch')) {
      const detailedError = `Cannot connect to backend at ${url}.\n\nPossible reasons:\n1. Backend server is not running\n2. CORS is blocking the request\n3. Network/firewall issue\n\nCheck:\n- Backend is running on http://localhost:8000\n- Browser console for CORS errors\n- Backend terminal for errors`;
      throw new Error(detailedError);
    }
    throw error;
  }
};

const api = {
  async get(token: string | undefined, path: string) {
    console.log(`API GET: ${getApiUrl()}${path}`);
    console.log(`Token (first 50 chars): ${token?.substring(0, 50)}...`);
    if (!token) {
      console.error("No token provided for API GET request!");
      throw new Error("No authentication token");
    }
    const res = await fetchWithTimeout(`${getApiUrl()}${path}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) {
      const errorBody = await res.text();
      console.error(`API GET failed: ${res.status} ${res.statusText}`, errorBody);
      throw new Error(`API error: ${res.status}`);
    }
    return res.json();
  },

  async post(token: string | undefined, path: string, data: any) {
    console.log(`API POST: ${getApiUrl()}${path}`, data);
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
      console.error(`API POST failed: ${res.status} ${res.statusText}`, errorText);
      throw new Error(`API error: ${res.status} - ${errorText}`);
    }
    return res.json();
  },

  async put(token: string | undefined, path: string, data: any) {
    console.log(`API PUT: ${getApiUrl()}${path}`, data);
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
      console.error(`API PUT failed: ${res.status} ${res.statusText}`, errorText);
      throw new Error(`API error: ${res.status} - ${errorText}`);
    }
    return res.json();
  },

  async delete(token: string | undefined, path: string) {
    console.log(`API DELETE: ${getApiUrl()}${path}`);
    const res = await fetchWithTimeout(`${getApiUrl()}${path}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok && res.status !== 204) {
      console.error(`API DELETE failed: ${res.status} ${res.statusText}`);
      throw new Error(`API error: ${res.status}`);
    }
  },

  async patch(token: string | undefined, path: string) {
    console.log(`API PATCH: ${getApiUrl()}${path}`);
    const res = await fetchWithTimeout(`${getApiUrl()}${path}`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) {
      console.error(`API PATCH failed: ${res.status} ${res.statusText}`);
      throw new Error(`API error: ${res.status}`);
    }
    return res.json();
  },
};

export default api;
