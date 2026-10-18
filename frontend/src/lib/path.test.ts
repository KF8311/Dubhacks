import { activeSectionPath } from "./path.ts"

function rects(map: Record<string, { top: number; bottom: number }>) {
  return (id: string) => map[id] ?? null
}

test("shop is current at the top of the page", () => {
  expect(
    activeSectionPath(
      rects({
        shop: { top: 76, bottom: 820 },
        how: { top: 820, bottom: 2200 },
        about: { top: 2200, bottom: 3000 },
      }),
    ),
  ).toBe("/")
})

test("how it works is current once its top crosses the header line", () => {
  expect(
    activeSectionPath(
      rects({
        shop: { top: -700, bottom: 80 },
        how: { top: 80, bottom: 1460 },
        about: { top: 1460, bottom: 2260 },
      }),
    ),
  ).toBe("/how")
})

test("how it works stays current while scrolling through a tall how section", () => {
  expect(
    activeSectionPath(
      rects({
        shop: { top: -1400, bottom: -620 },
        how: { top: -620, bottom: 840 },
        about: { top: 840, bottom: 1640 },
      }),
    ),
  ).toBe("/how")
})

test("about is current after how has scrolled past the header", () => {
  expect(
    activeSectionPath(
      rects({
        shop: { top: -2100, bottom: -1320 },
        how: { top: -1320, bottom: 90 },
        about: { top: 90, bottom: 890 },
      }),
    ),
  ).toBe("/about")
})
