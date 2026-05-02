/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable built-in gzip compression on the Next.js Node.js origin server.
  // This ensures every response is compressed before it reaches the CDN.
  compress: true,

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
   * HTTP response headers applied at the Next.js layer.
   * These instruct Cloudflare and the browser how to cache and decompress assets.
   */
  async headers() {
    return [
      // ── Next.js immutable hashed bundles ──────────────────────────────────
      // Content-hashed filenames → safe to cache forever.
      {
        source: '/_next/static/:path*',
        headers: [
          { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
          { key: 'Vary', value: 'Accept-Encoding' },
        ],
      },

      // ── Next.js image optimisation route ──────────────────────────────────
      {
        source: '/_next/image',
        headers: [
          { key: 'Cache-Control', value: 'public, max-age=86400, stale-while-revalidate=604800' },
          { key: 'Vary', value: 'Accept-Encoding' },
        ],
      },

      // ── All pages and API routes ───────────────────────────────────────────
      // :path* is the correct Next.js wildcard (no capturing groups allowed).
      {
        source: '/:path*',
        headers: [
          { key: 'Cache-Control', value: 'public, max-age=0, must-revalidate' },
          { key: 'Vary', value: 'Accept-Encoding' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ]
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

