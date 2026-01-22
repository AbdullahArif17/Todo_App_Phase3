// Health check endpoint for frontend
export async function GET() {
  return new Response(JSON.stringify({ status: 'healthy', service: 'frontend', timestamp: Date.now() }), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}