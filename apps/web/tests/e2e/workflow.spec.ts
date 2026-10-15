import { expect, test } from "@playwright/test";
test("operator observes, changes scenario, optimizes, compares and exports", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Operations overview" }),
  ).toBeVisible();
  await expect(
    page.getByText("Completed journeys", { exact: true }),
  ).toBeVisible();
  await page.getByLabel("Scenario", { exact: true }).selectOption("normal");
  await expect(
    page.getByText("A typical weekday with steady campus travel."),
  ).toBeVisible();
  await page.getByLabel("Scenario", { exact: true }).selectOption("rush");
  await expect(
    page.getByText("Residence departures build before the first lecture."),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Optimization Studio", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Run optimization", exact: true })
    .click();
  await expect(
    page.getByText("Feasible recommendation", { exact: true }),
  ).toBeVisible({ timeout: 60000 });
  await expect(
    page.getByRole("heading", { name: "One scenario. A fair comparison." }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Accept plan", exact: true }).click();
  await expect(page.getByText("accepted", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Overview", exact: true }).click();
  await expect(
    page.getByText("Accepted plan in operation", { exact: false }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Analytics & reports", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Experiment history" }),
  ).toBeVisible();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("link", { name: "CSV", exact: true }).first().click();
  expect((await downloadPromise).suggestedFilename()).toContain(".csv");
});
test("navigation, disruption controls and mobile layout", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByText("Completed journeys", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Fleet & timetable", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Published duties & departure windows" }),
  ).toBeVisible();
  await page.getByLabel("Filter timetable route").selectOption("R2");
  await expect(
    page.getByRole("cell", { name: "T101", exact: false }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Demand intelligence", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Stop-level capacity pressure" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Disruption simulator", exact: true })
    .click();
  await page
    .getByLabel("Vehicle breakdown", { exact: true })
    .selectOption("V01");
  await page
    .getByRole("button", { name: "Run simulation", exact: true })
    .click();
  await expect(
    page.getByText("Simulation saved. Results are ready."),
  ).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Overview", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Operations overview" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});
test("backend failure produces an actionable error state", async ({ page }) => {
  await page.route("**/api/v1/dashboard?*", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        error: { message: "Service temporarily unavailable" },
      }),
    }),
  );
  await page.goto("/");
  await expect(
    page
      .getByRole("alert")
      .filter({ hasText: "Service temporarily unavailable" }),
  ).toContainText("Service temporarily unavailable");
  await expect(
    page.getByRole("button", { name: "Retry", exact: true }),
  ).toBeVisible();
});

test("guided demo validates a frozen proposal and exports paired evidence", async ({
  page,
}) => {
  test.setTimeout(90000);
  await page.goto("/");
  await page
    .getByRole("button", { name: "2-minute demo", exact: true })
    .click();
  await expect(page.getByRole("region", { name: "Guided demo" })).toContainText(
    "DEMO 1 / 4",
  );
  await page.getByRole("button", { name: "Next step", exact: true }).click();
  await page
    .getByRole("button", { name: "Run optimization", exact: true })
    .click();
  await expect(
    page.getByText("Feasible recommendation", { exact: true }),
  ).toBeVisible({ timeout: 60000 });
  await page.getByRole("button", { name: "Next step", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "The original day, in human terms" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Test on 20 new days", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Does the improvement survive different days?",
    }),
  ).toBeVisible({ timeout: 30000 });
  await expect(
    page.getByText("Days with worse transfers", { exact: true }),
  ).toBeVisible();
  const download = page.waitForEvent("download");
  await page.getByRole("link", { name: "Daily CSV", exact: true }).click();
  expect((await download).suggestedFilename()).toContain(".csv");
  const selected = await page.getByLabel("Evidence proposal").inputValue();
  await page.reload();
  await page.getByRole("button", { name: "Evidence lab", exact: true }).click();
  await page.getByLabel("Evidence proposal").selectOption(selected);
  await expect(
    page.getByRole("button", { name: "20-day validation saved" }),
  ).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});
