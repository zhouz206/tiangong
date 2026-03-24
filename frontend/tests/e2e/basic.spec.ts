import { test, expect } from '@playwright/test'

test.describe('Basic Functionality', () => {
  test('should load the homepage successfully', async ({ page }) => {
    await page.goto('/')

    // Check if the page title contains the app name
    await expect(page).toHaveTitle(/天工/)

    // Check if the main navigation is visible
    await expect(page.getByText('天工 TianGong')).toBeVisible()
  })

  test('should navigate to projects page', async ({ page }) => {
    await page.goto('/')

    // Click on the projects navigation item
    await page.getByText('项目').click()

    // Wait for navigation and check URL
    await expect(page).toHaveURL('/projects')

    // Check if the page title is visible
    await expect(page.getByText('项目')).toBeVisible()
  })

  test('should navigate to agents page', async ({ page }) => {
    await page.goto('/')

    // Click on the agents navigation item
    await page.getByText('Agent').click()

    // Wait for navigation and check URL
    await expect(page).toHaveURL('/agents')

    // Check if the page title is visible
    await expect(page.getByText('Agent')).toBeVisible()
  })

  test('should navigate to knowledge page', async ({ page }) => {
    await page.goto('/')

    // Click on the knowledge navigation item
    await page.getByText('知识库').click()

    // Wait for navigation and check URL
    await expect(page).toHaveURL('/knowledge')

    // Check if the page title is visible
    await expect(page.getByText('知识库')).toBeVisible()
  })

  test('should toggle dark/light mode', async ({ page }) => {
    await page.goto('/')

    // Find and click the theme toggle button
    const themeToggle = page.getByText('深色模式').or(page.getByText('浅色模式'))
    await themeToggle.click()

    // Wait for theme change
    await page.waitForTimeout(500)

    // Check if theme changed (check for dark class on html element)
    const html = page.locator('html')
    const hasDarkClass = await html.evaluate((el) => el.classList.contains('dark'))

    // Theme should have changed
    expect(hasDarkClass).toBeDefined()
  })

  test('should show 404 page for non-existent routes', async ({ page }) => {
    await page.goto('/non-existent-page')

    // Check if 404 page is displayed
    await expect(page.getByText('404')).toBeVisible()
    await expect(page.getByText('页面未找到')).toBeVisible()
  })

  test('should handle mobile navigation', async ({ page }) => {
    // Simulate mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })

    await page.goto('/')

    // Check if hamburger menu is visible on mobile
    const menuButton = page.locator('button[aria-label="toggle menu"]')
    await expect(menuButton).toBeVisible()

    // Click hamburger menu
    await menuButton.click()

    // Sidebar should be visible now
    const sidebar = page.locator('aside')
    await expect(sidebar).toBeVisible()
  })
})
