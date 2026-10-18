import { describe, expect, test } from "bun:test";

import {
  formatMoney,
  formatQuestion,
  formatResults,
  isSearchable,
  parseChoice,
  toQuery,
  type Snapshot,
} from "./agent";

describe("toQuery", () => {
  test("drops polite framing", () => {
    expect(toQuery("hey can you find me noise cancelling headphones")).toBe(
      "noise cancelling headphones",
    );
  });

  test("keeps a plain product", () => {
    expect(toQuery("  noise cancelling headphones  ")).toBe("noise cancelling headphones");
  });

  test("strips trailing punctuation", () => {
    expect(toQuery("running shoes.")).toBe("running shoes");
  });

  test("leaves the product alone", () => {
    expect(toQuery("airpods pro 2")).toBe("airpods pro 2");
  });
});

describe("isSearchable", () => {
  test("rejects greetings and tests", () => {
    expect(isSearchable("hi")).toBe(false);
    expect(isSearchable("test")).toBe(false);
    expect(isSearchable("ok")).toBe(false);
  });

  test("accepts a product", () => {
    expect(isSearchable("mechanical keyboard")).toBe(true);
  });
});

const options = [
  { id: "100", label: "Under $150" },
  { id: "250", label: "$150–$300" },
  { id: "500", label: "$300–$600" },
];

describe("parseChoice", () => {
  test("accepts a number", () => {
    expect(parseChoice(options, "2")?.id).toBe("250");
  });

  test("accepts the label", () => {
    expect(parseChoice(options, "$300–$600")?.id).toBe("500");
  });

  test("rejects a number outside the list", () => {
    expect(parseChoice(options, "7")).toBeNull();
  });

  test("rejects unrelated text", () => {
    expect(parseChoice(options, "just show me the best one")).toBeNull();
  });
});

describe("formatQuestion", () => {
  test("numbers the options and asks for a number", () => {
    const text = formatQuestion({ id: "q_budget", prompt: "What's your ceiling?", options, allow_free_text: true });
    expect(text).toContain("What's your ceiling?");
    expect(text).toContain("2. $150–$300");
    expect(text).toContain("Reply with a number.");
  });
});

describe("formatResults", () => {
  const snapshot: Snapshot = {
    session_id: "ses_1",
    stage: "ready",
    listings: [
      {
        id: "lst_1",
        title: "Sony WH-1000XM5",
        price_cents: 24900,
        merchant_name: "Best Buy",
        merchant_domain: "bestbuy.com",
        product_url: "https://www.google.com/search?ibp=oshop&q=xm5",
      },
    ],
    recommendation: {
      recommended_listing_id: "lst_1",
      reason: "Cheapest trusted listing.",
      no_trusted_option: false,
    },
    stats: { trusted: 8, caution: 0, danger: 1 },
  };

  test("leads with the pick, price, merchant, and link", () => {
    const text = formatResults(snapshot);
    expect(text).toContain("Sony WH-1000XM5");
    expect(text).toContain("$249 at bestbuy.com");
    expect(text).toContain("Cheapest trusted listing.");
    expect(text).toContain("https://www.google.com/search?ibp=oshop&q=xm5");
    expect(text).toContain("8 trusted · 0 caution · 1 flagged");
  });

  test("refuses a search with no trusted option", () => {
    const text = formatResults({
      ...snapshot,
      stage: "no_trusted_option",
      recommendation: { no_trusted_option: true },
    });
    expect(text).toContain("will not recommend a purchase");
    expect(text).not.toContain("Sony");
  });

  test("is honest when live search failed", () => {
    expect(formatResults({ ...snapshot, stage: "failed" })).toContain("did not substitute");
  });
});

test("formatMoney drops zero cents", () => {
  expect(formatMoney(24900)).toBe("$249");
  expect(formatMoney(2147)).toBe("$21.47");
});
