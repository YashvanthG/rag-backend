📘 LPU RAG API — Developer Documentation

Base URL

https://rag-backend-37jk.onrender.com
🧾 Overview

This API provides a Retrieval-Augmented Generation (RAG) backend for answering user queries using a document knowledge base. It combines semantic search and large language models to generate contextual, accurate responses. The /chat endpoint returns streaming responses.

🔐 Authentication
🔑 API Key (Required for /chat)

All requests to /chat must include:

X-API-Key: <your_api_key>
🔐 Admin Key (Required for /admin/* and /docs)
X-Admin-Key: <your_admin_key>
⚠️ Security Requirements
API keys must not be exposed in client-side code
Always use a backend proxy (server-side) when calling this API from a frontend
Store keys in environment variables
🌐 Endpoints
🔹 Health Check
GET /health

Response

{
  "status": "Backend has started .."
}
🤖 Chat API
POST /chat

Generates an answer using RAG and returns a streaming text response.

Headers
Content-Type: application/json
X-API-Key: <your_api_key>
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
Request Fields
Field	Type	Required	Description
question	string	Yes	User query
history	array	No	Conversation history
Message Format
{
  "role": "user | assistant | system",
  "content": "string"
}
Response
Content-Type: text/plain
Format: Streaming (chunked response)

Example:

LPU is a private university located in Punjab...
Notes
Response is streamed token-by-token
Not a JSON response
Client must handle streaming
🔐 Admin API

All endpoints require:

X-Admin-Key: <your_admin_key>
📄 Upload Text
POST /admin/upload
{
  "text": "Your content here"
}
📄 Upload PDF
POST /admin/upload-pdf
Content-Type: multipart/form-data
Field: file
📄 List Documents
GET /admin/documents
📄 Delete Document
DELETE /admin/delete
{
  "source": "filename.pdf"
}
📄 Delete All Documents
DELETE /admin/delete-all
📄 Stats
GET /admin/stats
{
  "documents": 5,
  "chunks": 120
}
📄 Retrieval Debug
POST /admin/test-retrieval
{
  "query": "LPU admission process"
}
📡 Streaming Usage
JavaScript Example
const res = await fetch("/api/chat", {
  method: "POST",
  body: JSON.stringify({
    question: "What is LPU?",
    history: []
  })
});

const reader = res.body.getReader();
const decoder = new TextDecoder();

let output = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  output += decoder.decode(value);
  console.log(output);
}
⚠️ Frontend Integration Guidelines
❌ Do NOT call API directly from browser
fetch("https://rag-backend-37jk.onrender.com/chat", {
  headers: {
    "X-API-Key": "your_key"
  }
})

This exposes your API key.

✅ Recommended Architecture
Frontend (Browser)
    ↓
Backend (Vercel / Server)
    ↓
RAG API (/chat)
Example Backend Proxy
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
❗ Error Handling
403 Unauthorized
{
  "detail": "Invalid API Key"
}
422 Validation Error
{
  "detail": "Invalid input"
}
500 Internal Error
Server error.
🔐 Best Practices
Use environment variables for all keys
Never expose keys in frontend
Use backend proxy for all requests
Validate request payloads before sending
Handle streaming properly on client side
📦 Summary
/chat → main API (streaming response, requires API key)
/admin/* → document management (requires admin key)
Responses are streamed text, not JSON
Requires server-side integration for production use
