import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Hoisted deps live at the repo root; trace from there during production builds.
  outputFileTracingRoot: path.join(__dirname, ".."),
};

export default nextConfig;
