import { expect, test } from "@playwright/test";

test.describe("Authentication", () => {
  test("should redirect to login when not authenticated", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL(/.*login/);
  });

  test("should show signup form", async ({ page }) => {
    await page.goto("/signup");
    await expect(page.getByRole("heading", { name: /sign up/i })).toBeVisible();
    await expect(page.getByPlaceholderText(/email/i)).toBeVisible();
    await expect(page.getByPlaceholderText(/password/i)).toBeVisible();
  });

  test("should show login form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
    await expect(page.getByPlaceholderText(/email/i)).toBeVisible();
    await expect(page.getByPlaceholderText(/password/i)).toBeVisible();
  });

  test("should navigate between login and signup", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("link", { name: /sign up/i }).click();
    await expect(page).toHaveURL(/.*signup/);

    await page.getByRole("link", { name: /sign in/i }).click();
    await expect(page).toHaveURL(/.*login/);
  });
});
