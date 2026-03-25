🚀 LPU RAG API — Quick Developer Guide
🔗 Base URL
https://rag-backend-37jk.onrender.com
🔐 Authentication
Required Header (for /chat)
X-API-Key: <your_api_key>
Content-Type: application/json
🤖 Chat Endpoint (Main API)
📌 POST /chat
Request Body
{
  "question": "What is LPU?",
  "history": [
    {
      "role": "user",
      "content": "Tell me about LPU"
    }
  ]
}
Message Format
{
  "role": "user | assistant | system",
  "content": "string"
}
📡 Response
Type: text/plain
Format: Streaming (NOT JSON)

Example output:

LPU is a private university located in Punjab...


⚡ How to Fetch (Frontend via Backend ONLY)
export default async function handler(req, res) {
  const response = await fetch("https://rag-backend-37jk.onrender.com/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": process.env.RAG_API_KEY
    },
    body: JSON.stringify(req.body)
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    res.write(decoder.decode(value));
  }

  res.end();
}
❗ Important Rules
❌ Do NOT call API directly from frontend
compulsory use any technic to not expose the api key in public (must)
❌ Do NOT expose API keys
✅ Store keys in environment variables
⚠️ Response is streamed text, not JSON → handle with ReadableStream
⚠️ Errors
403
{ "detail": "Invalid API Key" }
422
{ "detail": "Invalid input" }
500
Server error
📦 That’s It

👉 Only endpoint you need:

POST /chat

👉 Only thing to remember:

Send question
Handle streaming response
compulsory use any technic to not expose the api key in public (must)
