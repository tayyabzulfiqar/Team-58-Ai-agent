import { NextResponse } from 'next/server'

const CONFIGURED_API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.BACKEND_URL ||
  ''

const API_URL = CONFIGURED_API_URL || 'http://127.0.0.1:8000'

export async function POST(request: Request) {
  try {
    if (!CONFIGURED_API_URL && process.env.NODE_ENV === 'production') {
      return NextResponse.json(
        {
          error:
            'NEXT_PUBLIC_API_URL is not configured. Add your Render backend URL in Vercel, for example https://your-backend.onrender.com',
        },
        { status: 500 }
      )
    }

    const body = await request.json().catch(() => ({}))
    const response = await fetch(`${API_URL}/api/run-system`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      cache: 'no-store',
    })

    const data = await response.json()

    if (!response.ok) {
      console.error('Backend request failed', {
        status: response.status,
        apiUrl: API_URL,
        response: data,
      })

      return NextResponse.json(
        {
          error: data?.error || `Backend error: ${response.status}`,
          backendUrl: API_URL,
          details: data,
        },
        { status: response.status }
      )
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      {
        error: 'Backend request failed',
        backendUrl: API_URL,
      },
      { status: 500 }
    )
  }
}
