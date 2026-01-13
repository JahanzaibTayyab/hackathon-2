# Check Environment Variables Skill

Verify all required environment variables are set correctly.

## Usage
```bash
/check-env
```

## What it does
1. Checks backend .env file for required variables
2. Checks frontend .env.local file for required variables
3. Verifies API keys are set (without showing them)
4. Reports missing or invalid configurations

## Commands
```bash
# Check backend env
echo "=== Backend Environment ==="
cd backend
[ -f .env ] && echo "✓ .env file exists" || echo "✗ .env file missing"
grep -q "DATABASE_URL=" .env && echo "✓ DATABASE_URL set" || echo "✗ DATABASE_URL missing"
grep -q "BETTER_AUTH_SECRET=" .env && echo "✓ BETTER_AUTH_SECRET set" || echo "✗ BETTER_AUTH_SECRET missing"
grep -q "OPENAI_API_KEY=" .env && echo "✓ OPENAI_API_KEY set" || echo "✗ OPENAI_API_KEY missing"

# Check frontend env
echo -e "\n=== Frontend Environment ==="
cd frontend
[ -f .env.local ] && echo "✓ .env.local file exists" || echo "✗ .env.local file missing"
grep -q "DATABASE_URL=" .env.local && echo "✓ DATABASE_URL set" || echo "✗ DATABASE_URL missing"
grep -q "BETTER_AUTH_SECRET=" .env.local && echo "✓ BETTER_AUTH_SECRET set" || echo "✗ BETTER_AUTH_SECRET missing"
```

## Success Criteria
- All required environment variables are present
- No missing configurations
- API keys are validated (presence, not content)
