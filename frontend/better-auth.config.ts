import { defineConfig } from "better-auth/next";
import { jwt } from "better-auth/plugin/jwt";

export default defineConfig({
  plugins: [
    jwt({
      secret: process.env.BETTER_AUTH_SECRET!,
    }),
  ],
});
