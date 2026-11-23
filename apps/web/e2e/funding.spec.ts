import { expect, test } from "@playwright/test"

test("the account funds itself with no sign-in, takes a top-up, and keeps other hosts and origins out", async ({
  page,
  context,
}) => {
  test.skip(
    process.env.ASL_TEST_ISOLATED !== "1" ||
      !process.env.ASL_DB_NAME?.startsWith("asl_m1_browser_"),
    "Requires a fresh disposable browser database"
  )
  let mutationUrl: string | undefined
  page.on("request", (request) => {
    if (request.method() === "POST" && request.url().includes("_server"))
      mutationUrl = request.url()
  })

  await page.goto("/settings")
  const hostileHost = await page.request.get("/", {
    headers: { Host: "untrusted.example" },
  })
  expect(hostileHost.status()).toBe(421)
  // ExecPlan 0042: no sign-in and no setup. The API posted the starting 10,000 USDT when it
  // started, so Settings opens on the funded account with the top-up.
  await expect(page.getByRole("heading", { name: "Top-up" })).toBeVisible()
  await expect(page.getByLabel(/passphrase|setup key/i)).toHaveCount(0)
  await expect(
    page.getByRole("button", { name: /sign (in|out)/i })
  ).toHaveCount(0)
  await expect(
    page.getByRole("button", { name: /initial contribution/i })
  ).toHaveCount(0)
  await expect(
    page.getByText("10,000.00 USDT", { exact: false }).first()
  ).toBeVisible()
  const history = page
    .getByText("Funding history", { exact: true })
    .locator("xpath=ancestor::*[@data-slot='card'][1]")
  await expect(history.getByRole("row")).toHaveCount(2)
  await expect(history.getByRole("row").nth(1)).toContainText(
    "Initial contribution"
  )
  await expect(history.getByRole("row").nth(1)).toContainText("POSTED")
  expect(await context.cookies()).toEqual(
    expect.not.arrayContaining([expect.objectContaining({ name: "asl_owner" })])
  )

  const cdp = await context.newCDPSession(page)
  await cdp.send("Accessibility.enable")
  const axTree = await cdp.send("Accessibility.getFullAXTree")
  expect(
    axTree.nodes.some(
      (node) => node.role?.value === "heading" && node.name?.value === "Top-up"
    )
  ).toBe(true)
  const headingContrast = await page
    .getByRole("heading", { name: "Top-up" })
    .evaluate((element) => {
      const channels = (value: string) => {
        const canvas = document.createElement("canvas")
        canvas.width = canvas.height = 1
        const canvasContext = canvas.getContext("2d")!
        canvasContext.fillStyle = value
        canvasContext.fillRect(0, 0, 1, 1)
        return Array.from(canvasContext.getImageData(0, 0, 1, 1).data)
      }
      const luminance = (rgb: number[]) =>
        rgb
          .map((channel) => {
            const normalized = channel / 255
            return normalized <= 0.04045
              ? normalized / 12.92
              : ((normalized + 0.055) / 1.055) ** 2.4
          })
          .reduce(
            (sum, channel, index) =>
              sum + channel * [0.2126, 0.7152, 0.0722][index],
            0
          )
      const foreground = luminance(
        channels(getComputedStyle(element).color).slice(0, 3)
      )
      let backgroundElement: Element | null = element
      while (
        backgroundElement &&
        channels(getComputedStyle(backgroundElement).backgroundColor)[3] === 0
      )
        backgroundElement = backgroundElement.parentElement
      const background = luminance(
        channels(
          getComputedStyle(backgroundElement ?? document.body).backgroundColor
        ).slice(0, 3)
      )
      return (
        (Math.max(foreground, background) + 0.05) /
        (Math.min(foreground, background) + 0.05)
      )
    })
  expect(headingContrast).toBeGreaterThanOrEqual(4.5)

  const dialog = page.getByRole("alertdialog")
  await page.getByLabel("Amount in USDT").fill("1e3")
  await page.getByRole("button", { name: "Review top-up" }).click()
  await expect(
    page.getByText("Enter a positive decimal", { exact: false })
  ).toBeVisible()
  await page.getByLabel("Amount in USDT").fill("2200.00")
  await page.getByRole("button", { name: "Review top-up" }).click()
  await expect(
    dialog.getByText("2,200.00 USDT", { exact: false })
  ).toBeVisible()
  await page.keyboard.press("Escape")
  await expect(dialog).toBeHidden()
  // The review was a POST server function: another site's page cannot send one.
  expect(mutationUrl).toBeDefined()
  const hostileOrigin = await page.request.post(mutationUrl!, {
    headers: {
      Origin: "http://untrusted.example",
      "Content-Type": "application/json",
    },
    data: {},
  })
  expect(hostileOrigin.status()).toBe(403)

  await page.getByRole("button", { name: "Review top-up" }).click()
  await expect(
    dialog.getByRole("heading", { name: "Confirm top-up" })
  ).toBeVisible()
  await dialog.getByRole("button", { name: "Confirm funding" }).click()
  await expect(dialog).toBeHidden()
  await expect(
    page.getByText("12,200.00 USDT", { exact: false }).first()
  ).toBeVisible()
  await expect(page.getByText("Funding posted.")).toBeVisible()
  await expect(
    page.getByText("0.00 USDT", { exact: false }).first()
  ).toBeVisible()
  await expect(history.getByRole("row")).toHaveCount(3)

  // A reload reads the same account: nothing to sign in to, nothing lost.
  await page.reload()
  await expect(page.getByRole("heading", { name: "Top-up" })).toBeVisible()
  await expect(
    page.getByText("12,200.00 USDT", { exact: false }).first()
  ).toBeVisible()
})
