import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Remove standalone for Vercel (Vercel handles this automatically)
  // output: "standalone",

  images: {
    // Vercel supports image optimization
    unoptimized: false,
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
};

export default nextConfig;
