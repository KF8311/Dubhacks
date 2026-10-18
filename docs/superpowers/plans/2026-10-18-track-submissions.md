# Track Submissions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the three chosen non-sponsored tracks — MLH Best Use of Gemini API, MLH Best Use of MongoDB Atlas, MLH DEV Writing — into claims the submission can defend with code and artifacts.

**Architecture:** Two small code changes and two written artifacts. Gemini gets a visible provenance marker on every AI-written sentence, so a judge can see the model working and see where the deterministic fallback takes over. Atlas gets the payment path's inputs (listings, investigations) persisted, so a checkout survives a backend restart. The DEV article and the Devpost metadata carry the story.

**Tech Stack:** FastAPI, Pydantic, Motor/MongoDB Atlas, React 19, Zustand, Vitest, pytest, Devpost, DEV.to.

**Spec:** `info/nonsponser-tracks.txt`, `info/sponsered-tracks.txt`, `info/title-tracks.txt`, `docs/devpost-form.md`, `docs/decisions.md` (D-017–D-019, D-025, D-026).

## Global Constraints

- Exactly **one** title track: **Visa: Reimagine Shopping** (locked).
- At most **3** sponsored side tracks; **unlimited** non-sponsored side tracks.
- The LLM never scores, selects checks, or touches payability (D-017–D-019). A build test enforces it.
- Money is integer cents; the sandbox line is `Sandbox — simulated Visa Intelligent Commerce flow.`
- One Uvicorn worker. No new infrastructure.
- Every commit carries the author's name only.
- Deadline: **10:00 AM Sunday** hard lock; a video is mandatory; judging starts 10:30 AM.
  Cut line: if Task 2 runs past 90 minutes, abandon it — the Atlas claim already stands on D-026.

## Review Focus

- An explanation returned by the template path must never be labelled `gemini`; a judge clicking "Explain" with no API key must see `From evidence`.
- A checkout created before a restart must still confirm after it, or the app must refuse with `INVESTIGATION_STALE` — never a 500.
- A missing listing id must not make `_get_listing` raise; the catalog fallback stays last.
- The DEV article must not claim a feature the repo does not have.
- The Gemini project number must come from the account that owns the key — not a placeholder.

---

### Task 1: Gemini provenance on check explanations

**Files:**
- Modify: `backend/app/services/llm.py` (add `explain_check_with_source`, keep `explain_check`)
- Modify: `backend/app/api/routes_sessions.py:95-101`
- Modify: `frontend/src/lib/api.ts:133-147`
- Modify: `frontend/src/features/results/CheckRow.tsx:27-55`
- Test: `backend/tests/unit/test_llm.py`
- Test: `frontend/src/features/results/CheckRow.test.tsx`
- Doc: `docs/contracts.md` (additive field on the explain response)

**Interfaces:**
- Produces: `async def explain_check_with_source(check: TrustCheckResult, *, complete: CompleteFn | None = None) -> tuple[str, str]` — the second element is `"gemini"` or `"template"`.
- Produces: `POST /api/sessions/{id}/explain` returns `{"listing_id", "check_id", "explanation", "source"}`.
- Produces: `explainCheck(...)` returns `{ text: string; source: "gemini" | "template" }`.

- [ ] **Step 1: Write the failing backend tests**

```python
@pytest.mark.asyncio
async def test_explain_check_reports_template_source_when_no_model(monkeypatch):
    monkeypatch.setattr("app.services.llm.get_settings", lambda: _settings(offline=True))
    text, source = await explain_check_with_source(_check())
    assert source == "template"
    assert text == _check().summary


@pytest.mark.asyncio
async def test_explain_check_reports_gemini_source_when_the_model_answers():
    async def fake(_prompt: str) -> str:
        return '{"explanation": "The certificate is valid for the domain."}'

    text, source = await explain_check_with_source(_check(), complete=fake)
    assert source == "gemini"
    assert text == "The certificate is valid for the domain."
```

Add `_check()` returning a passed `TrustCheckResult` with `summary="ok"` in the same file.

- [ ] **Step 2: Run them and confirm they fail**

Run: `cd backend && .\.venv\Scripts\python.exe -m pytest tests/unit/test_llm.py -q`
Expected: `ImportError` / `NameError` for `explain_check_with_source`.

- [ ] **Step 3: Implement the source-aware call**

In `llm.py`, rename the body of `explain_check` to `explain_check_with_source`, return `(text, "gemini")` on a parsed answer and `(fallback, "template")` on every failure path. Re-add `explain_check` as a one-line wrapper returning `(await explain_check_with_source(check, complete=complete))[0]`.

- [ ] **Step 4: Run the backend tests**

Run: `cd backend && .\.venv\Scripts\python.exe -m pytest tests/unit/test_llm.py -q`
Expected: all pass.

- [ ] **Step 5: Return the source from the route**

In `routes_sessions.explain_check_route`, call `explain_check_with_source` and add `"source": source` to the returned dict.

- [ ] **Step 6: Write the failing frontend test**

In `CheckRow.test.tsx`, extend the existing explain test's mock to resolve `{ text: "AI sentence", source: "gemini" }` and assert the row renders `AI-generated`. Add a second case resolving `{ text: "Evidence sentence", source: "template" }` and assert `From evidence`.

- [ ] **Step 7: Run it and confirm it fails**

Run: `cd frontend && npx vitest run src/features/results/CheckRow.test.tsx`
Expected: FAIL — no `AI-generated` text.

- [ ] **Step 8: Implement the client and the chip**

`api.ts`: return `{ text: body.explanation, source: body.source }`; mock mode returns `{ text: "...", source: "template" }`.
`CheckRow.tsx`: hold `{ text, source } | null`; render the sentence, plus a `text-xs` chip reading `AI-generated` when `source === "gemini"` and `From evidence` otherwise.

- [ ] **Step 9: Run the frontend tests**

Run: `cd frontend && npx vitest run src/features/results/CheckRow.test.tsx`
Expected: pass.

- [ ] **Step 10: Add the field to `docs/contracts.md` and commit**

Add `"source": "gemini" | "template"` to the explain response contract.

```bash
git add backend/app/services/llm.py backend/app/api/routes_sessions.py backend/tests/unit/test_llm.py \
  frontend/src/lib/api.ts frontend/src/features/results/CheckRow.tsx frontend/src/features/results/CheckRow.test.tsx \
  docs/contracts.md
git commit -m "Mark AI-written explanations with their source"
```

---

### Task 2: Make the payment path survive a restart (Atlas)

**Files:**
- Modify: `backend/app/services/repository.py` (add `get_listing` to the protocol and both adapters)
- Modify: `backend/app/sessions/orchestrator.py:147` and `:303`
- Modify: `backend/app/api/routes_checkout.py:53-64` and the four call sites
- Test: `backend/tests/integration/test_repositories.py`
- Test: `backend/tests/integration/test_orchestrator.py`

**Interfaces:**
- Produces: `async def get_listing(self, listing_id: str) -> Listing | None` on `Repository`, `InMemoryRepository`, `MongoRepository`.
- Produces: `async def get_investigation_for(self, session_id: str, listing_id: str) -> Investigation | None` on every adapter (Mongo queries `{"session_id": sid, "listing_id": lid}` newest-first by `created_at`; memory scans its values).
- Produces: `async def _get_listing(listing_id: str) -> Listing | None` and `async def _get_investigation(session_id: str, listing_id: str) -> Investigation | None` in `routes_checkout.py` (order: registry → repository → catalog).

- [ ] **Step 1: Write the failing repository test**

```python
@pytest.mark.asyncio
async def test_mongo_round_trips_a_listing():
    from app.services.repository import MongoRepository

    db = _FakeDB()
    repo = MongoRepository(db)
    listing = _listing()
    await repo.save_listing(listing)
    loaded = await repo.get_listing(listing.id)
    assert loaded is not None
    assert loaded.product_url == listing.product_url
```

Reuse a small `_listing()` factory built like the one in `test_memory_repo_round_trips_a_receipt_share_id`.

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd backend && .\.venv\Scripts\python.exe -m pytest tests/integration/test_repositories.py -q`
Expected: FAIL — `MongoRepository` has no `get_listing`.

- [ ] **Step 3: Implement `get_listing` in the protocol and both adapters**

`InMemoryRepository.get_listing` returns `self._listings.get(listing_id)` under the lock. `MongoRepository.get_listing` returns `_hydrate(Listing, await self.db.listings.find_one({"_id": listing_id}))`.

- [ ] **Step 4: Run the repository tests**

Run: `cd backend && .\.venv\Scripts\python.exe -m pytest tests/integration/test_repositories.py -q`
Expected: pass.

- [ ] **Step 5: Write the failing orchestrator test**

```python
@pytest.mark.asyncio
async def test_orchestrator_persists_listings_and_investigations(...):
    # run the offline orchestrator as the existing tests do
    ...
    repo = get_repository()
    saved = await repo.get_listing(listings[0].id)
    assert saved is not None
    assert await repo.get_investigation(inv.id) is not None
```

- [ ] **Step 6: Run it and confirm it fails**

Run: `cd backend && .\.venv\Scripts\python.exe -m pytest tests/integration/test_orchestrator.py -q`
Expected: FAIL — `get_listing` returns None (nothing persisted).

- [ ] **Step 7: Write through in the orchestrator**

After `self.store.replace_listings(...)`, save each listing. After `self.store.attach_investigation(...)`, save the investigation. Import `get_repository` at module level.

- [ ] **Step 8: Run the orchestrator tests**

Run: `cd backend && .\.venv\Scripts\python.exe -m pytest tests/integration/test_orchestrator.py -q`
Expected: pass.

- [ ] **Step 9: Write the failing lookup tests**

```python
@pytest.mark.asyncio
async def test_get_listing_returns_none_for_an_unknown_id():
    from app.services.repository import InMemoryRepository
    assert await InMemoryRepository().get_listing("lst_missing") is None


@pytest.mark.asyncio
async def test_get_investigation_for_matches_session_and_listing():
    from app.services.repository import InMemoryRepository
    repo = InMemoryRepository()
    inv = _investigation(session_id="ses_1", listing_id="lst_1")
    await repo.save_investigation(inv)
    assert await repo.get_investigation_for("ses_1", "lst_1") is not None
    assert await repo.get_investigation_for("ses_2", "lst_1") is None
```

- [ ] **Step 10: Run them and confirm they fail**

Run: `cd backend && .\.venv\Scripts\python.exe -m pytest tests/integration/test_repositories.py -q`
Expected: FAIL — `get_investigation_for` is missing on the adapters.

- [ ] **Step 11: Make the checkout lookups async with a repository fallback**

`_get_listing`: registry → `await repo.get_listing(...)` → catalog. `_get_investigation`: registry → `await repo.get_investigation_for(...)`. Await both at all four call sites and change the `monkeypatch.setattr` stubs in `tests/integration/test_checkout_api.py` to `async def`.

- [ ] **Step 12: Write the restart-survival test**

```python
@pytest.mark.asyncio
async def test_a_checkout_can_be_confirmed_after_the_registry_is_cleared(monkeypatch):
    # build session + listing + investigation, create the checkout through the API,
    # write the listing and investigation into the repository, then registry.clear()
    response = client.post(f"/api/checkout/{checkout_id}/confirm", json=payload)
    assert response.status_code == 200
    assert response.json()["receipt_id"].startswith("rcp_")
```

- [ ] **Step 13: Run the backend suite**

Run: `cd backend && .\.venv\Scripts\python.exe -m pytest -q`
Expected: all pass.

- [ ] **Step 14: Prove it against Atlas over HTTP**

Create a checkout, restart the backend, confirm it. Record the ids in `docs/status.md` under the Atlas proof block.

- [ ] **Step 15: Commit**

```bash
git add backend/app/services/repository.py backend/app/sessions/orchestrator.py backend/app/api/routes_checkout.py \
  backend/tests/integration/test_repositories.py backend/tests/integration/test_orchestrator.py \
  backend/tests/integration/test_checkout_api.py docs/status.md
git commit -m "Persist listings and investigations so a checkout survives a restart"
```

---

### Task 3: DEV Writing Challenge article

**Files:**
- Create: `docs/devpost-article.md`
- Doc: `docs/devpost-form.md` (link the published URL)

- [ ] **Step 1: Write the article (1,200–1,800 words)**

Sections: the problem (agents can pay anyone); the decision (deterministic scoring, LLM has no vote); the honest failure (D-025); the two bugs only a real database found (D-026, with the exact errors); what we would build next.
Constraints: no invented features, no customer data, every number from `docs/status.md`.

- [ ] **Step 2: Publish on DEV**

Publish as a post tagged `hackathon`, `ai`, `python`, `mongodb`. Copy the public URL.

- [ ] **Step 3: Link it**

Add the URL under the Devpost "Try it out / Additional info" links and to `docs/devpost-form.md`.

- [ ] **Step 4: Commit**

```bash
git add docs/devpost-article.md docs/devpost-form.md
git commit -m "Add the DEV Writing Challenge article"
```

---

### Task 4: Track slate and Devpost metadata

**Files:**
- Modify: `docs/decisions.md` (append D-027)
- Modify: `docs/devpost-form.md`
- Modify: `docs/checklist.md`

- [ ] **Step 1: Record D-027 — the slate**

Title: **Visa: Reimagine Shopping**.
Sponsored (3): **SideShift** (Best Startup Idea — no build requirement), **Cloudforce** (entry is a raffle ticket; Most Interesting is a judges' pick), and a third slot held for **VEYZL** if the audit app is actually installable, otherwise **Photon** if a channel can be provisioned inside two hours, otherwise left empty.
Not selected: T-Mobile (their track is wireless commerce; this build is headphones), SpaceXAI (needs Cursor + Grok), Perceptron (robotics workshop already closed).
Non-sponsored: **MLH Gemini**, **MLH MongoDB Atlas**, **MLH DEV Writing**, **DubHacks NEXT**, **MLH Commit Fellowship**.

- [ ] **Step 2: Select the checkboxes in `devpost-form.md`**

Add the sponsored three and the non-sponsored list; keep VEYZL out.

- [ ] **Step 3: Get the Gemini project number**

The owner of `GEMINI_API_KEY` opens `aistudio.google.com/apikey`, copies the project **number** (not the key), and pastes it into the Devpost field. Never commit it.

- [ ] **Step 4: Update the checklist**

Replace the "B — docs, claims, Devpost" MLH line with a link to this plan and mark the Atlas claim supported.

- [ ] **Step 5: Commit**

```bash
git add docs/decisions.md docs/devpost-form.md docs/checklist.md
git commit -m "Pick the track slate and record D-027"
```

---

### Task 5: Final gate

- [ ] **Step 1: Run every gate**

```powershell
cd backend;  .\.venv\Scripts\python.exe -m pytest -q
cd ..\frontend; npx vitest run; npm run build
cd ..; backend\.venv\Scripts\python.exe scripts\replay_offline.py
```

- [ ] **Step 2: Confirm the submission artifacts exist**

Three screenshots, one recording under 3 minutes, the public URL, the DEV link, the Gemini project number.

- [ ] **Step 3: Update `docs/status.md` and submit**

Set the track row to the final slate, then submit before 10:00 AM and screenshot the confirmation.
