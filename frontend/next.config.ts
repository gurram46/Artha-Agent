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
    // Add valid experimental options here if needed
  },
  reactStrictMode: false, // Disable strict mode to reduce hydration warnings
  
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()',
          },
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: https:",
              "font-src 'self' data:",
              "connect-src 'self' ws: wss: http://localhost:* https://localhost:*",
              "frame-ancestors 'none'",
              "base-uri 'self'",
              "form-action 'self'",
              "object-src 'none'",
              "media-src 'self'",
            ].join('; '),
          },
        ],
      },
    ];
  },
  
  // HTTPS redirect in production
  async redirects() {
    if (process.env.NODE_ENV === 'production' && process.env.FORCE_HTTPS === 'true') {
      return [
        {
          source: '/(.*)',
          has: [
            {
              type: 'header',
              key: 'x-forwarded-proto',
              value: 'http',
            },
          ],
          destination: 'https://artha-ai.com/:path*',
          permanent: true,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
