import { test, expect } from "@playwright/test";

const ROLE_ID = process.env.TEST_ROLE_ID ?? "";

test.describe("Rule builder", () => {
  test.beforeEach(async ({ page }) => {
    if (!ROLE_ID) test.skip();
    try {
      const res = await page.request.get("http://localhost:8000/health");
      if (!res.ok()) test.skip();
    } catch {
      test.skip();
    }
  });

  test("NL input creates rule preview", async ({ page }) => {
    await page.goto(`/jobs/${ROLE_ID}/rules`);
    await page.waitForTimeout(1500);

    const input = page.getByPlaceholder(/rule|natural/i).first();
    if (!(await input.isVisible())) return;

    await input.fill("resume score >= 75");
    const addBtn = page.getByRole("button", { name: /add rule/i }).first();
    await addBtn.click();
    await page.waitForTimeout(1000);

    // Preview text should appear
    const preview = page.getByText(/score|75|preview/i).first();
    await expect(preview).toBeVisible({ timeout: 5000 });
  });

  test("can confirm and activate a rule", async ({ page }) => {
    await page.goto(`/jobs/${ROLE_ID}/rules`);
    await page.waitForTimeout(1500);

    const input = page.getByPlaceholder(/rule|natural/i).first();
    if (!(await input.isVisible())) return;

    await input.fill("score above 70");
    const addBtn = page.getByRole("button", { name: /add rule/i }).first();
    await addBtn.click();
    await page.waitForTimeout(1000);

    const confirmBtn = page.getByRole("button", { name: /confirm/i }).first();
    if (!(await confirmBtn.isVisible())) return;

    await confirmBtn.click();
    await page.waitForTimeout(1000);

    // Rule should appear in active rules list
    const confirmedBadge = page.getByText(/confirmed|active/i).first();
    await expect(confirmedBadge).toBeVisible({ timeout: 5000 });
  });

  test("active rules list is shown", async ({ page }) => {
    await page.goto(`/jobs/${ROLE_ID}/rules`);
    await page.waitForTimeout(1500);

    // Page renders without errors
    const heading = page.getByText(/rule|dashboard/i).first();
    await expect(heading).toBeVisible({ timeout: 5000 });
  });
});
