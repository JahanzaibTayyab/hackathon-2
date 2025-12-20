"use client";

import { authClient } from "@/lib/auth-client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    authClient.getSession().then((session) => {
      if (session?.data?.session) {
        router.push("/dashboard");
      } else {
        router.push("/login");
      }
    });
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <p>Loading...</p>
    </div>
  );
}
