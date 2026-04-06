export const BASE_URL = process.env.NEXT_PUBLIC_API_URL

export async function runSystem(data: any) {
  console.log('BASE URL:', BASE_URL)

  const res = await fetch(`${BASE_URL}/run-system`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  const result = await res.json()
  return result
}
