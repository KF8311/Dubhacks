---
title: Open Questions
type: questions
updated: 2026-10-17
---

# Open Questions

Resolve these with a mentor, a judge, or a two-minute team huddle. When one is answered, move it to `decisions.md` if it changes the build, or delete it if it doesn't.

## For a Visa mentor

- [ ] **UX weight:** the rubric table says 20% for User Experience, the bullet list says 25%. Which is authoritative? Assume 25% and design accordingly.
- [ ] **Sandbox labeling:** is a clearly labeled simulated Intelligent Commerce flow acceptable, or does the track expect a real sandbox API? We are assuming clearly labeled is fine.
- [ ] **Video judging:** is the 3-minute video the only Visa judging artifact, or do judges also see the live demo? Assume video-only and script accordingly.
- [ ] **Receipt framing:** does a "trust receipt" read as a Visa-relevant artifact, or should it be framed as a merchant-verification record?

## Product

- [ ] Should allowlisted merchants show a score of 0 (per spec) or a "Verified merchant" badge instead? Current plan: badge, with 0 stored for the rule.
- [ ] When no listing is trusted, do we show the empty state as a success ("we protected you") or an error? Current plan: success with a reason.
- [ ] Do we show skipped checks to the user, or only in the receipt? Current plan: show them with a "could not verify" label.
- [ ] Is the savings number (trusted median − best price) meaningful with only 8 listings? Current plan: yes, but label it "vs. trusted median."

## Technical

- [ ] **SerpAPI key:** do we have one? Go/no-go at 1:15 PM Saturday.
- [x] **Deploy target:** decided — Fly.io always-on 256 MB (D-010). Cloud Run and Render free were the alternatives.
- [ ] **MongoDB Atlas (owner: B, D-016):** who creates the cluster, and is the IP allowlist `0.0.0.0/0` acceptable for the event? Not needed until Block 6.
- [ ] **Gemini key:** do we have quota for 2–3 calls per session, or should templates be the default path?
- [ ] **Safe Browsing key:** do we have one, or do we ship the static denylist with `source: "unavailable"`?

## Track selection

- [ ] Confirm the Visa title track is selected in Devpost.
- [ ] Pick up to 3 sponsored side tracks (T-Mobile, SideShift, Cloudforce, Photon, VEYZL, Perceptron, SpaceXAI).
- [ ] Select non-sponsored tracks: DubHacks NEXT, MLH Gemini, MongoDB, DEV Writing.
- [ ] Does the MongoDB track require a specific integration depth, or is Atlas usage enough?
