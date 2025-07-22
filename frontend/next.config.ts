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
};

export default nextConfig;
