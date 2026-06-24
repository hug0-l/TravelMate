import { test, expect } from "@playwright/test";

const unique = Date.now();

test.describe("Authentication", () => {
  test("register new user via /register form", async ({ page }) => {
    const email = `e2e-register-${unique}@test.dev`;

    await page.goto("/register");
    await page.fill('input[placeholder="你的名字"]', "Test User");
    await page.fill('input[placeholder="you@example.com"]', email);
    await page.fill('input[placeholder="至少 6 碼"]', "testpass123");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/");
  });

  test("login existing user via /login form", async ({ page }) => {
    const email = `e2e-login-${unique}@test.dev`;

    // Create user via API first
    await page.request.post("/api/auth/register", {
      data: { email, name: "Test User", password: "testpass123" },
    });

    await page.goto("/login");
    await page.fill('input[placeholder="you@example.com"]', email);
    await page.fill('input[placeholder="••••••••"]', "testpass123");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/");
  });

  test("dashboard shows after login", async ({ page }) => {
    const email = `e2e-dash-${unique}@test.dev`;

    // Create user via API
    await page.request.post("/api/auth/register", {
      data: { email, name: "Test User", password: "testpass123" },
    });

    await page.goto("/login");
    await page.fill('input[placeholder="you@example.com"]', email);
    await page.fill('input[placeholder="••••••••"]', "testpass123");
    await page.click('button[type="submit"]');
    await page.waitForURL("/");
    await expect(page.locator("text=我的旅程")).toBeVisible();
  });
});
