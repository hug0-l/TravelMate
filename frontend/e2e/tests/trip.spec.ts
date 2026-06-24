import { test, expect } from "@playwright/test";

const unique = Date.now();
const baseEmail = `e2e-trip-${unique}`;

test.describe("Trip Management", () => {
  test("create trip and verify trip card appears", async ({ page }) => {
    const email = `${baseEmail}-create@test.dev`;

    // Create user via API
    await page.request.post("/api/auth/register", {
      data: { email, name: "Trip Tester", password: "testpass123" },
    });

    // Login via UI
    await page.goto("/login");
    await page.fill('input[placeholder="you@example.com"]', email);
    await page.fill('input[placeholder="••••••••"]', "testpass123");
    await page.click('button[type="submit"]');
    await page.waitForURL("/");

    // Click new trip button
    await page.getByRole("button", { name: /新行程/ }).click();
    // Fill trip name
    await page.fill(
      'input[placeholder="行程名稱（如：東京賞楓）"]',
      "E2E Test Trip",
    );
    // Fill date
    await page.fill('input[type="date"]', "2026-07-01");
    // Submit
    await page.getByRole("button", { name: "建立" }).last().click();
    // Verify trip card appears
    await expect(page.locator("h3:has-text('E2E Test Trip')")).toBeVisible();
  });

  test("enter trip and verify tabs display", async ({ page }) => {
    const email = `${baseEmail}-tabs@test.dev`;

    // Create user and trip via API
    await page.request.post("/api/auth/register", {
      data: { email, name: "Trip Tester", password: "testpass123" },
    });

    // Login
    await page.goto("/login");
    await page.fill('input[placeholder="you@example.com"]', email);
    await page.fill('input[placeholder="••••••••"]', "testpass123");
    await page.click('button[type="submit"]');
    await page.waitForURL("/");

    // Create trip via UI
    await page.getByRole("button", { name: /新行程/ }).click();
    await page.fill(
      'input[placeholder="行程名稱（如：東京賞楓）"]',
      "E2E Trip for Tabs",
    );
    await page.fill('input[type="date"]', "2026-07-01");
    await page.getByRole("button", { name: "建立" }).last().click();

    // Click the trip card
    await page.locator("h3:has-text('E2E Trip for Tabs')").click();

    // Verify tabs display
    await expect(
      page.locator('button:has-text("行程"):not(:has-text("預算"))'),
    ).toBeVisible();
    await expect(page.locator('button:has-text("地圖")')).toBeVisible();
    await expect(page.locator('button:has-text("預算")')).toBeVisible();
    await expect(page.locator('button:has-text("回憶")')).toBeVisible();
    await expect(page.locator('button:has-text("景點")')).toBeVisible();
  });
});
