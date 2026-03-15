import { test, expect } from '@playwright/test';

test.describe('Smoke tests', () => {
  test('landing page loads', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
  });

  test('login page loads', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: /welcome back|sign in/i })).toBeVisible();
  });

  test('register page loads', async ({ page }) => {
    await page.goto('/register');
    await expect(page.getByRole('heading', { name: /create|account/i })).toBeVisible();
  });

  test('pricing page loads', async ({ page }) => {
    await page.goto('/pricing');
    await expect(page.getByRole('heading', { name: /pricing|plan/i })).toBeVisible({ timeout: 5000 });
  });

  test('features page loads', async ({ page }) => {
    await page.goto('/features');
    await expect(page.locator('h1, h2')).toBeVisible({ timeout: 5000 });
  });

  test('contact page loads', async ({ page }) => {
    await page.goto('/contact');
    await expect(page.getByRole('heading', { name: /contact|get in touch/i })).toBeVisible({ timeout: 5000 });
  });

  test('dashboard redirects to login when unauthenticated', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/(login|register)/, { timeout: 5000 });
  });

  test('404 page renders', async ({ page }) => {
    await page.goto('/nonexistent-page-xyz-404-test');
    await expect(page.getByText(/not found|page doesn't exist|404/i)).toBeVisible({ timeout: 5000 });
  });
});
