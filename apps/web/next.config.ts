import type { NextConfig } from "next";

const isDev = process.env.NODE_ENV === "development";
const API_URL = process.env.API_URL ?? "http://localhost:3001";

// Geen scripts van derden, geen externe fonts (zelf gehost), geen frames.
const csp = [
  "default-src 'self'",
  `script-src 'self' 'unsafe-inline'${isDev ? " 'unsafe-eval'" : ""}`,
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self'",
  "connect-src 'self'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
  ...(isDev ? [] : ["upgrade-insecure-requests"]),
].join("; ");

const nextConfig: NextConfig = {
  poweredByHeader: false,
  reactStrictMode: true,
  experimental: { sri: { algorithm: "sha256" } },
  async headers() {
    return [{
      source: "/(.*)",
      headers: [
        { key: "Content-Security-Policy", value: csp },
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        { key: "X-Frame-Options", value: "DENY" },
        { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), interest-cohort=()" },
        { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
      ],
    }];
  },
  // Lokaal: SVG's via de website-origin. In productie routeert Cloudflare /v1/assets naar het CDN.
  async rewrites() {
    return [{ source: "/v1/assets/:path*", destination: `${API_URL}/v1/assets/:path*` }];
  },
};

export default nextConfig;
