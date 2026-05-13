import { defineConfig, loadEnv } from 'vite'

function normalizeProxyTarget(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  try {
    const parsed = new URL(raw)
    return `${parsed.protocol}//${parsed.host}`
  } catch {
    return raw.replace(/\/+$/, '').replace(/\/api$/i, '')
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const target = normalizeProxyTarget(env.VITE_API_PROXY_TARGET)
  if (!target) {
    throw new Error('Missing VITE_API_PROXY_TARGET in frontend/.env')
  }

  return {
    server: {
      host: '0.0.0.0',
      port: 5173,
      strictPort: true,
      proxy: {
        '/api': {
          target,
          changeOrigin: true,
          secure: false,
        },
        '/session': {
          target,
          changeOrigin: true,
          secure: false,
          ws: true,
          configure: (proxy) => {
            proxy.on('proxyReqWs', (proxyReq, req) => {
              const cookieHeader = req.headers.cookie || ''
              const cookies = Object.fromEntries(
                String(cookieHeader)
                  .split(';')
                  .map((part) => part.trim())
                  .filter(Boolean)
                  .map((part) => {
                    const idx = part.indexOf('=')
                    if (idx < 0) return [part, '']
                    return [part.slice(0, idx), decodeURIComponent(part.slice(idx + 1))]
                  })
              )
              const wsToken = cookies.qos_ws_token
              const userId = cookies.qos_user_id

              if (wsToken) proxyReq.setHeader('x-ws-token', wsToken)
              if (userId) proxyReq.setHeader('x-user-id', userId)
            })
          },
        },
      },
    },
  }
})
