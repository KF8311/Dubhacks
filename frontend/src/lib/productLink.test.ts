import { productLink } from "./productLink.ts"

test("a merchant URL is labelled with the merchant domain", () => {
  expect(
    productLink({
      product_url: "https://www.bestbuy.com/site/sony-xm5/123.p",
      merchant_domain: "bestbuy.com",
    }),
  ).toEqual({ href: "https://www.bestbuy.com/site/sony-xm5/123.p", label: "View at bestbuy.com" })
})

test("a Google Shopping URL says where it really goes", () => {
  expect(
    productLink({
      product_url: "https://www.google.com/search?udm=28&q=xm5",
      merchant_domain: "bestbuy.com",
    }),
  ).toEqual({
    href: "https://www.google.com/search?udm=28&q=xm5",
    label: "View on Google Shopping",
  })
})

test("an empty or non-http URL has no link", () => {
  expect(productLink({ product_url: "", merchant_domain: "bestbuy.com" })).toBeNull()
  expect(productLink({ product_url: "target.com/item/1", merchant_domain: "target.com" })).toBeNull()
})

test("an unparseable URL has no link", () => {
  expect(productLink({ product_url: "http://", merchant_domain: "x.com" })).toBeNull()
})
