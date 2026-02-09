// frontend/src/lib/auth-client.ts
import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  // Use the app URL for auth API calls
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  plugins: [jwtClient()],
  fetchOptions: {
    credentials: "include", // Ensure cookies are sent with requests
  },
});
