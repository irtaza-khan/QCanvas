/** @type {import('next').NextConfig} */
const nextConfig = {
  // Explicitly enable SWC minification for production builds.
  // Resolves the "un-minified JavaScript" SEO/performance warning.
  // SWC is ~17x faster than Terser and is the Next.js 13+ default.
  swcMinify: true,
  experimental: {
    typedRoutes: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
      },
    ],
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  /**
   * Optional dev path: set NEXT_PUBLIC_CIRQ_USE_NEXT_REWRITE=true and call /cirq-api/...
   * Target defaults to Cirq-RAG on 8001 (QCanvas API stays on 8000).
   */
  async rewrites() {
    const target = (
      process.env.CIRQ_REWRITE_TARGET || 'http://127.0.0.1:8001'
    ).replace(/\/$/, '')
    return [
      {
        source: '/cirq-api/:path*',
        destination: `${target}/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
