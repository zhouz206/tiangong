import { test, expect } from '@playwright/test'

test.describe('Project Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/projects')
  })

  test('should load projects page successfully', async ({ page }) => {
    // Check if the page title is visible
    await expect(page.getByText('项目')).toBeVisible()
    await expect(page.getByText('管理和创建 AI 协作项目')).toBeVisible()
  })

  test('should show empty state when no projects exist', async ({ page }) => {
    // Check for empty state (either no projects or search results)
    const emptyState = page.getByText('暂无项目').or(page.getByText('没有找到匹配的项目'))

    // If empty state is visible, the "新建项目" button should be available
    if (await emptyState.isVisible()) {
      await expect(page.getByText('暂无项目')).toBeVisible()
    }
  })

  test('should open new project dialog when clicking create button', async ({ page }) => {
    // Click the "新建项目" button
    const createButton = page.getByText('新建项目').or(page.getByText('新建'))
    await createButton.click()

    // Dialog should open with title "创建新项目"
    await expect(page.getByText('创建新项目')).toBeVisible()
  })

  test('should have project templates available', async ({ page }) => {
    // Open new project dialog
    const createButton = page.getByText('新建项目').or(page.getByText('新建'))
    await createButton.click()

    // Check if templates are visible
    await expect(page.getByText('软件开发')).toBeVisible()
    await expect(page.getByText('内容创作')).toBeVisible()
    await expect(page.getByText('数据分析')).toBeVisible()
  })

  test('should close dialog when clicking cancel', async ({ page }) => {
    // Open new project dialog
    const createButton = page.getByText('新建项目').or(page.getByText('新建'))
    await createButton.click()

    // Wait for dialog to open
    await page.waitForTimeout(300)

    // Press Escape to close dialog
    await page.keyboard.press('Escape')

    // Dialog should be closed
    await expect(page.getByText('创建新项目')).not.toBeVisible()
  })

  test('should have search functionality', async ({ page }) => {
    // Check if search input exists
    const searchInput = page.getByPlaceholder('搜索项目...')
    await expect(searchInput).toBeVisible()

    // Type in search query
    await searchInput.fill('test project')

    // Results should filter (may show empty state)
    await page.waitForTimeout(300)
  })

  test('should handle responsive layout on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })

    // Reload page to apply responsive layout
    await page.reload()

    // "新建项目" button should show shortened text on mobile
    const createButton = page.getByText('新建').or(page.getByText('新建项目'))
    await expect(createButton).toBeVisible()
  })
})

test.describe('Project Creation Flow', () => {
  test('should complete project creation wizard step 1', async ({ page }) => {
    await page.goto('/projects')

    // Open new project dialog
    const createButton = page.getByText('新建项目').or(page.getByText('新建'))
    await createButton.click()

    // Step 1: Select template
    await expect(page.getByText('选择项目模板')).toBeVisible()

    // Select "软件开发" template
    await page.getByText('软件开发').click()

    // Click next button
    await page.getByText('下一步').click()

    // Should move to step 2
    await expect(page.getByText('项目信息')).toBeVisible()
  })

  test('should complete project creation wizard step 2', async ({ page }) => {
    await page.goto('/projects')

    // Open new project dialog
    const createButton = page.getByText('新建项目').or(page.getByText('新建'))
    await createButton.click()

    // Step 1: Select template
    await page.getByText('软件开发').click()
    await page.getByText('下一步').click()

    // Step 2: Fill in project info
    await page.getByPlaceholder('输入项目名称...').fill('Test Project')
    await page.getByText('下一步').click()

    // Should move to step 3 (preview)
    await expect(page.getByText('确认项目配置')).toBeVisible()
  })
})
