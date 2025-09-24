import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    ok: true,
    timestamp: new Date().toISOString(),
    service: 'QCanvas API',
    version: '1.0.0',
    ui: 'QCanvas',
  })
}
