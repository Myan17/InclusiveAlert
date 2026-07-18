import type { NextConfig } from "next";

// GitHub Pages serves project sites under a sub-path (e.g. /InclusiveAlert).
// basePath/assetPrefix are driven by NEXT_PUBLIC_BASE_PATH so local `next dev`
// (unset → "") and the Pages build (set → "/InclusiveAlert") both work.
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig: NextConfig = {
  // Emit a fully static site into `out/` so it can be hosted on GitHub Pages.
  output: "export",
  basePath,
  assetPrefix: basePath || undefined,
  trailingSlash: true,
  // next/image optimization needs a server; disable it for static export.
  images: { unoptimized: true },
};

export default nextConfig;
