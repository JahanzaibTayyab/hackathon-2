# Better Auth Setup Guide

## Current Implementation Status

✅ **Completed:**

- Better Auth installed and configured
- Database adapter (Drizzle + PostgreSQL) configured
- Authentication routes set up (`/api/auth/[...all]`)
- Login and Signup pages implemented
- Auth client configured for React

⚠️ **Needs Configuration:**

1. **Database Schema**: Run `npx @better-auth/cli generate` to create the database schema
2. **Environment Variables**: Set up `.env.local` with:

   - `BETTER_AUTH_SECRET` - Secret key (min 32 chars)
   - `DATABASE_URL` - PostgreSQL connection string (same as backend or separate)
   - `NEXT_PUBLIC_BASE_URL` - Frontend URL (http://localhost:3000)

3. **JWT Token Extraction**: The current implementation tries to get tokens from:
   - `/api/auth/token` endpoint (Better Auth provides this)
   - Session token from auth client

## Next Steps

1. **Generate Database Schema:**

   ```bash
   cd frontend
   npx @better-auth/cli generate
   # Answer 'y' to generate schema
   ```

2. **Apply Database Migrations:**

   ```bash
   # If using Drizzle migrations
   npx drizzle-kit generate
   npx drizzle-kit migrate
   ```

3. **Update Backend JWT Verification:**

   - Ensure backend uses the same `BETTER_AUTH_SECRET`
   - Backend should verify tokens using HS256 algorithm
   - Extract user_id from token payload (typically in `sub` or `user_id` field)

4. **Test Authentication Flow:**
   - Sign up a new user
   - Sign in
   - Verify JWT token is issued
   - Test API calls with token

## Better Auth Documentation

- https://better-auth.com/docs
- https://better-auth.com/docs/adapters/drizzle
- https://better-auth.com/docs/plugins/jwt
