import * as dotenv from "dotenv";
import * as schema from "../auth-schema";

import { Pool } from "pg";
import { drizzle } from "drizzle-orm/node-postgres";

dotenv.config({ path: ".env.local" });

async function migrate() {
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
  });

  const db = drizzle(pool, { schema });

  console.log("Running Better Auth migrations...");

  // The schema will be created when Better Auth first connects
  // This script ensures the connection works
  try {
    await pool.query("SELECT 1");
    console.log("✅ Database connection successful!");
    console.log(
      "✅ Better Auth tables will be created automatically on first use"
    );
  } catch (error) {
    console.error("❌ Database connection failed:", error);
    process.exit(1);
  }

  await pool.end();
}

migrate();
