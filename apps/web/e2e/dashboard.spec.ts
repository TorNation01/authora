import { test, expect } from '@playwright/test';

/**
 * Dashboard smoke tests - require full auth flow.
 * Run after register or with seeded test user.
 */
test.describe('Dashboard smoke', () => {
  test('full flow: register -> onboarding -> dashboard -> project', async ({ page }) => {
    const email = `qa-${Date.now()}@example.com`;
    await page.goto('/register');
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'password123');
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL(/\/(onboarding|dashboard)/, { timeout: 10000 });

    // If onboarding, complete or skip
    if (page.url().includes('onboarding')) {
      await expect(page.getByRole('heading', { name: /book type|writing|welcome/i })).toBeVisible({ timeout: 5000 });
      // Click through or submit
      const nextBtn = page.getByRole('button', { name: /next|continue|start|skip/i }).first();
      if (await nextBtn.isVisible()) {
        await nextBtn.click();
      }
    }

    // Should reach dashboard
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
    await expect(page.getByText(/dashboard|projects|notes|journey/i)).toBeVisible({ timeout: 5000 });
  });

  test('dashboard sidebar navigation', async ({ page }) => {
    // Requires auth - use login if you have a test user
    const email = `nav-${Date.now()}@example.com`;
    await page.goto('/register');
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'password123');
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL(/\/(onboarding|dashboard)/, { timeout: 10000 });

    // Skip onboarding if present
    if (page.url().includes('onboarding')) {
      const skip = page.getByRole('link', { name: /skip|dashboard/i }).first();
      if (await skip.isVisible()) await skip.click();
    }

    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);

    // Check sidebar links exist
    const notesLink = page.getByRole('link', { name: /notes/i });
    const exportLink = page.getByRole('link', { name: /export/i });
    await expect(notesLink.or(exportLink)).toBeVisible({ timeout: 5000 });
  });
});
