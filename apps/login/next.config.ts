import path from "node:path";
import type { NextConfig } from "next";

// Eigen inlogpagina (ADR 0018). Strenge CSP: alles van hier, geen externe scripts of lettertypen.
const isDev = process.env.NODE_ENV === "development";
const csp = [
  "default-src 'self'", `script-src 'self' 'unsafe-inline'${isDev ? " 'unsafe-eval'" : ""}`, "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data:", "font-src 'self'", "connect-src 'self'", "object-src 'none'", "base-uri 'self'",
  // Formulieren posten hier; na inloggen stuurt de server door naar Zitadel (callback) en zo terug naar de site.
  "form-action 'self' https://*.zitadel.cloud https://kleurhoek.nl https://*.kleurhoek.nl", "frame-ancestors 'none'",
].join("; ");

const nextConfig: NextConfig = {
  poweredByHeader: false,
  output: "standalone",
  outputFileTracingRoot: path.join(__dirname, "../.."),
  transpilePackages: ["@kleurhoek/theme"],
  async headers() {
    return [{ source: "/(.*)", headers: [
      { key: "Content-Security-Policy", value: csp },
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "Referrer-Policy", value: "no-referrer" },
      { key: "X-Frame-Options", value: "DENY" },
      { key: "X-Robots-Tag", value: "noindex, nofollow" },
      { key: "Cache-Control", value: "no-store" },
      { key: "Permissions-Policy", value: "publickey-credentials-get=(self), publickey-credentials-create=(self)" },
    ] }];
  },
};
export default nextConfig;
