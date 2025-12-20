import * as dotenv from "dotenv";
import * as schema from "../auth-schema";

import { Pool } from "pg";
import { drizzle } from "drizzle-orm/node-postgres";

dotenv.config({ path: ".env.local" });

async function createAuthTables() {
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
  });

  const db = drizzle(pool, { schema });

  console.log("Creating Better Auth tables...");

  try {
    // Create all tables from the schema
    // Drizzle will create tables based on the schema
    await db.execute(
      `CREATE TABLE IF NOT EXISTS "user" (
        "id" TEXT PRIMARY KEY,
        "name" TEXT NOT NULL,
        "email" TEXT NOT NULL UNIQUE,
        "email_verified" BOOLEAN NOT NULL DEFAULT false,
        "image" TEXT,
        "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
        "updated_at" TIMESTAMP NOT NULL DEFAULT NOW()
      )`
    );

    await db.execute(
      `CREATE TABLE IF NOT EXISTS "session" (
        "id" TEXT PRIMARY KEY,
        "expires_at" TIMESTAMP NOT NULL,
        "token" TEXT NOT NULL UNIQUE,
        "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
        "updated_at" TIMESTAMP NOT NULL DEFAULT NOW(),
        "ip_address" TEXT,
        "user_agent" TEXT,
        "user_id" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE
      )`
    );

    await db.execute(
      `CREATE INDEX IF NOT EXISTS "session_userId_idx" ON "session"("user_id")`
    );

    await db.execute(
      `CREATE TABLE IF NOT EXISTS "account" (
        "id" TEXT PRIMARY KEY,
        "account_id" TEXT NOT NULL,
        "provider_id" TEXT NOT NULL,
        "user_id" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
        "access_token" TEXT,
        "refresh_token" TEXT,
        "id_token" TEXT,
        "access_token_expires_at" TIMESTAMP,
        "refresh_token_expires_at" TIMESTAMP,
        "scope" TEXT,
        "password" TEXT,
        "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
        "updated_at" TIMESTAMP NOT NULL DEFAULT NOW()
      )`
    );

    await db.execute(
      `CREATE INDEX IF NOT EXISTS "account_userId_idx" ON "account"("user_id")`
    );

    await db.execute(
      `CREATE TABLE IF NOT EXISTS "verification" (
        "id" TEXT PRIMARY KEY,
        "identifier" TEXT NOT NULL,
        "value" TEXT NOT NULL,
        "expires_at" TIMESTAMP NOT NULL,
        "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
        "updated_at" TIMESTAMP NOT NULL DEFAULT NOW()
      )`
    );

    await db.execute(
      `CREATE INDEX IF NOT EXISTS "verification_identifier_idx" ON "verification"("identifier")`
    );

    await db.execute(
      `CREATE TABLE IF NOT EXISTS "jwks" (
        "id" TEXT PRIMARY KEY,
        "public_key" TEXT NOT NULL,
        "private_key" TEXT NOT NULL,
        "created_at" TIMESTAMP NOT NULL,
        "expires_at" TIMESTAMP
      )`
    );

    console.log("✅ Better Auth tables created successfully!");
  } catch (error: any) {
    if (error.code === "42P07") {
      // Table already exists
      console.log("✅ Better Auth tables already exist!");
    } else {
      console.error("❌ Error creating tables:", error.message);
      throw error;
    }
  } finally {
    await pool.end();
  }
}

createAuthTables().catch(console.error);
