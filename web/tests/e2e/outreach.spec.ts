import { test, expect } from "@playwright/test";

const ROLE_ID = process.env.TEST_ROLE_ID ?? "";

test.describe("Outreach timeline", () => {
  test.beforeEach(async ({ page }) => {
    if (!ROLE_ID) test.skip();
    try {
      const res = await page.request.get("http://localhost:8000/health");
      if (!res.ok()) test.skip();
    } catch {
      test.skip();
    }
  });

  test("renders outreach page", async ({ page }) => {
    await page.goto(`/jobs/${ROLE_ID}/outreach`);
    await page.waitForTimeout(1500);

    // The page title or main content should be visible
    const heading = page.getByText(/outreach|message|candidate/i).first();
    await expect(heading).toBeVisible({ timeout: 5000 });
  });

  test("candidate list sidebar appears", async ({ page }) => {
    await page.goto(`/jobs/${ROLE_ID}/outreach`);
    await page.waitForTimeout(1500);

    // Sidebar should have at least a list or empty state
    const sidebar = page.locator(".surface, [class*='border']").first();
    await expect(sidebar).toBeVisible({ timeout: 5000 });
  });

  test("clicking candidate shows timeline panel", async ({ page }) => {
    await page.goto(`/jobs/${ROLE_ID}/outreach`);
    await page.waitForTimeout(1500);

    // Try to find a candidate name in the sidebar
    const candidateItem = page.locator("button, [role='button']").filter({ hasText: /[A-Z][a-z]+ [A-Z][a-z]+/ }).first();
    if (!(await candidateItem.isVisible({ timeout: 2000 }).catch(() => false))) {
      // No candidates loaded — verify empty state is shown instead
      const emptyState = page.getByText(/no candidate|select|empty/i).first();
      await expect(emptyState).toBeVisible({ timeout: 3000 });
      return;
    }

    await candidateItem.click();
    await page.waitForTimeout(800);

    // Timeline panel should render
    const timeline = page.getByText(/timeline|event|no outreach/i).first();
    await expect(timeline).toBeVisible({ timeout: 5000 });
  });
});
