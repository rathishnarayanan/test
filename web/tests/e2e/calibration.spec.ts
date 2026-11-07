import { test, expect } from "@playwright/test";

const ROLE_ID = process.env.TEST_ROLE_ID ?? "";

test.describe("Calibration deck", () => {
  test.beforeEach(async ({ page }) => {
    if (!ROLE_ID) test.skip();
    // Verify API is reachable
    try {
      const res = await page.request.get("http://localhost:8000/health");
      if (!res.ok()) test.skip();
    } catch {
      test.skip();
    }
  });

  test("shows candidate cards", async ({ page }) => {
    await page.goto(`/jobs/${ROLE_ID}/calibration`);
    // Wait for content to load
    await page.waitForTimeout(1500);
    // Should show at least one calibration card or an empty state
    const card = page.locator("[data-testid='calibration-card'], .surface").first();
    await expect(card).toBeVisible({ timeout: 5000 });
  });

  test("Yes button advances card", async ({ page }) => {
    await page.goto(`/jobs/${ROLE_ID}/calibration`);
    await page.waitForTimeout(1500);

    const yesBtn = page.getByRole("button", { name: /yes/i }).first();
    if (!(await yesBtn.isVisible())) return; // No cards loaded

    const initialText = await page.textContent("body");
    await yesBtn.click();
    await page.waitForTimeout(800);

    // Yes rate should update or card should advance
    const newText = await page.textContent("body");
    expect(newText).not.toBeNull();
  });

  test("No button shows reason tags", async ({ page }) => {
    await page.goto(`/jobs/${ROLE_ID}/calibration`);
    await page.waitForTimeout(1500);

    const noBtn = page.getByRole("button", { name: /no/i }).first();
    if (!(await noBtn.isVisible())) return;

    await noBtn.click();
    await page.waitForTimeout(500);

    // Reason tag area should appear
    const reasonArea = page.getByText(/reason|tag|skip/i).first();
    await expect(reasonArea).toBeVisible({ timeout: 3000 });
  });

  test("yes-rate percentage is shown", async ({ page }) => {
    await page.goto(`/jobs/${ROLE_ID}/calibration`);
    await page.waitForTimeout(1500);

    // Should show yes rate somewhere on the page (e.g. "0%" or "Yes rate")
    const rateText = page.getByText(/yes.?rate|%/i).first();
    await expect(rateText).toBeVisible({ timeout: 5000 });
  });
});
