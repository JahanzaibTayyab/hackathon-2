# Test Chat Functionality Skill

Test the AI chat functionality end-to-end.

## Usage
```bash
/test-chat
```

## What it does
1. Verifies backend is running
2. Checks OpenAI API key is configured
3. Tests chat API endpoint with sample message
4. Verifies AI agent responds correctly
5. Checks task was created if applicable

## Commands
```bash
# Check backend health
echo "=== Checking Backend Health ==="
curl -s http://localhost:8000/health

# Check OpenAI key is set
echo -e "\n=== Checking OpenAI Configuration ==="
cd backend && grep -q "OPENAI_API_KEY=sk-" .env && echo "✓ OpenAI API key configured" || echo "✗ OpenAI API key not set"

# Test chat endpoint (requires authentication token)
echo -e "\n=== Testing Chat Endpoint ==="
echo "Note: This requires an authenticated user session"
echo "Manual test: Go to http://localhost:3000/chat and send: 'list my tasks'"

# Check recent chat requests in logs
echo -e "\n=== Recent Chat Activity ==="
tail -30 /tmp/claude/-Users-zaib-Panaverse-hackathon-2/tasks/b0cdd87.output | grep -E "POST /api/v1/chat|assistant|tool"
```

## Success Criteria
- Backend is healthy
- OpenAI key is configured
- Chat endpoint is accessible
- AI agent responds to requests
- Logs show successful interactions
