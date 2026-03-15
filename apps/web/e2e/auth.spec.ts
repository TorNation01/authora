import { test, expect } from '@playwright/test';

test.describe('Auth flow', () => {
  test('register and redirect to onboarding', async ({ page }) => {
    const email = `test-${Date.now()}@example.com`;
    await page.goto('/register');
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'password123');
    await page.getByRole('button', { name: /create account/i }).click();
    await expect(page).toHaveURL(/\/(onboarding|dashboard)/);
  });

  test('login with invalid credentials shows error', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'nonexistent@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page.getByText(/invalid|failed|error/i)).toBeVisible({ timeout: 5000 });
  });
});
