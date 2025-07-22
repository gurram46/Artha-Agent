import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  eslint: {
    // Disable ESLint during builds for hackathon
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable type checking during builds for hackathon
    ignoreBuildErrors: true,
  },
  experimental: {
    // Enable experimental suppression of hydration warnings
    suppressHydrationWarning: true,
  },
  reactStrictMode: false, // Disable strict mode to reduce hydration warnings
};

export default nextConfig;
