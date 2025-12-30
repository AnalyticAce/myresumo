#!/bin/bash

echo "Testing PowerCV Multi-Provider AI Support"
echo "=========================================="

# Check if N8N_API_KEY is set
if [ -z "$N8N_API_KEY" ]; then
    echo "❌ N8N_API_KEY environment variable not set"
    echo "Please set it in your .env file or export it"
    exit 1
fi

# Check if services are running
echo "🔍 Checking if PowerCV service is accessible..."
if curl -s http://localhost:8080/api/n8n/health > /dev/null; then
    echo "✅ PowerCV service is running"
else
    echo "❌ PowerCV service is not accessible at http://localhost:8080"
    echo "Make sure to run: docker-compose up -d"
    exit 1
fi

echo ""

# Test Deepseek provider
echo "🧪 Testing Deepseek provider..."
export AI_PROVIDER=deepseek
response=$(curl -s -X POST http://localhost:8080/api/n8n/optimize \
  -H "X-API-Key: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"cv_text":"Python Developer with 5 years experience in Django, Flask, FastAPI. Proficient in PostgreSQL, Redis, Docker.","jd_text":"Senior Python Developer needed. Must have experience with web frameworks, databases, and containerization.","user_id":"test_deepseek"}')

if echo "$response" | jq -e '.success' > /dev/null 2>&1; then
    echo "✅ Deepseek provider: $(echo "$response" | jq -r '.success')"
    echo "   Model used: $(echo "$response" | jq -r '.metadata.model_used')"
else
    echo "❌ Deepseek provider failed or API key not configured"
    echo "   Response: $response"
fi

echo ""

# Test Cerebras provider
echo "🧪 Testing Cerebras provider..."
export AI_PROVIDER=cerebras
response=$(curl -s -X POST http://localhost:8080/api/n8n/optimize \
  -H "X-API-Key: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"cv_text":"Python Developer with 5 years experience in Django, Flask, FastAPI. Proficient in PostgreSQL, Redis, Docker.","jd_text":"Senior Python Developer needed. Must have experience with web frameworks, databases, and containerization.","user_id":"test_cerebras"}')

if echo "$response" | jq -e '.success' > /dev/null 2>&1; then
    echo "✅ Cerebras provider: $(echo "$response" | jq -r '.success')"
    echo "   Model used: $(echo "$response" | jq -r '.metadata.model_used')"
else
    echo "❌ Cerebras provider failed or API key not configured"
    echo "   Response: $response"
fi

echo ""

# Test provider switching endpoint
echo "🔄 Testing provider switching..."
response=$(curl -s -X POST http://localhost:8080/api/n8n/switch-provider \
  -H "X-API-Key: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"provider":"cerebras","test_connection":false}')

if echo "$response" | jq -e '.success' > /dev/null 2>&1; then
    echo "✅ Provider switching works"
    echo "   Current provider: $(echo "$response" | jq -r '.provider')"
    echo "   Current model: $(echo "$response" | jq -r '.model')"
else
    echo "❌ Provider switching failed"
    echo "   Response: $response"
fi

echo ""

# Test providers list endpoint
echo "📋 Testing providers list..."
response=$(curl -s http://localhost:8080/api/n8n/providers \
  -H "X-API-Key: $N8N_API_KEY")

if echo "$response" | jq -e '.current_provider' > /dev/null 2>&1; then
    echo "✅ Providers list endpoint works"
    echo "   Current provider: $(echo "$response" | jq -r '.current_provider')"
    echo "   Available providers:"
    echo "$response" | jq -r '.available_providers[] | "     - \(.name): \(.model) (configured: \(.configured))"'
else
    echo "❌ Providers list endpoint failed"
    echo "   Response: $response"
fi

echo ""
echo "🎯 Test completed!"
echo "Note: Make sure you have set API_KEY and CEREBRAS_API_KEY in your .env file"
echo "OPENAI_API_KEY is optional for OpenAI provider support"
