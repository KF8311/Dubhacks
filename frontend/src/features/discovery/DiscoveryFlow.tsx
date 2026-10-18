import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { createSession, getSnapshot, submitAnswers } from "@/lib/api.ts"
import type { Answer, Question } from "@/lib/types.ts"
import { go } from "@/lib/path.ts"
import { useSessionStore } from "@/store/sessionStore.ts"

type Props = {
  onStarted: (sessionId: string) => void
}

const PILLARS = [
  {
    title: "Five trust checks",
    body: "Domain age, SSL, Safe Browsing, Reddit, and page flags on every merchant.",
  },
  {
    title: "Cheapest trusted",
    body: "The pick is the lowest price that passed — not the cheapest listing on the page.",
  },
  {
    title: "Sandbox checkout",
    body: "A simulated Visa mandate, passkey, and receipt. No real card is charged.",
  },
]

const STARTERS = ["Headphones", "Pens", "Water bottles"]

export function DiscoveryFlow({ onStarted }: Props) {
  const setQuery = useSessionStore((state) => state.setQuery)
  const showQuestions = useSessionStore((state) => state.showQuestions)
  const startSession = useSessionStore((state) => state.startSession)
  const [query, setLocalQuery] = useState("")
  const [questions, setQuestions] = useState<Question[]>([])
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [index, setIndex] = useState(0)
  const [phase, setPhase] = useState<"query" | "questions" | "submitting">("query")
  const [picked, setPicked] = useState<string | null>(null)
  const [freeText, setFreeText] = useState("")
  const [answers, setAnswers] = useState<Answer[]>([])
  const [error, setError] = useState<string | null>(null)
  const [asking, setAsking] = useState(false)

  const question = questions[index]

  async function onFindProducts() {
    const trimmed = query.trim()
    if (!trimmed) return
    setQuery(trimmed)
    setError(null)
    setAsking(true)
    try {
      const created = await createSession({ query: trimmed, client_id: "demo" })
      setSessionId(created.session_id)
      setQuestions(created.questions)
      showQuestions(created.questions)
      setIndex(0)
      setPicked(null)
      setFreeText("")
      setPhase("questions")
    } catch {
      setError("The search could not reach the server. Leave this page open and try again.")
    } finally {
      setAsking(false)
    }
  }

  function currentAnswer(): Answer | null {
    if (!question) return null
    if (picked) return { question_id: question.id, option_id: picked }
    if (freeText.trim()) return { question_id: question.id, text: freeText.trim() }
    return null
  }

  async function submit(finalAnswers: Answer[], skipRemaining: boolean) {
    if (!sessionId) return
    setPhase("submitting")
    setError(null)
    try {
      const submitted = await submitAnswers(sessionId, {
        answers: finalAnswers,
        skip_remaining: skipRemaining,
      })
      const snapshot = await getSnapshot(submitted.session_id)
      startSession(snapshot, {
        budgetMaxCents: submitted.search_spec?.budget_max_cents ?? null,
        budgetMinCents: submitted.search_spec?.budget_min_cents ?? null,
      })
      onStarted(snapshot.session_id)
    } catch (caught) {
      setPhase("questions")
      setError(caught instanceof Error ? caught.message : "Something went wrong")
    }
  }

  async function onNext() {
    const answer = currentAnswer()
    if (!question || !answer || !sessionId) return
    const nextAnswers = [...answers, answer]
    setAnswers(nextAnswers)
    setPicked(null)
    setFreeText("")
    if (index < questions.length - 1) {
      setIndex(index + 1)
      return
    }
    await submit(nextAnswers, false)
  }

  if (phase === "submitting") {
    return (
      <div className="ticket mx-auto max-w-2xl space-y-4 rounded-3xl p-6 sm:p-8" aria-busy="true">
        <p className="text-lg font-medium">Looking at retailers…</p>
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    )
  }

  if (phase === "query" || !question) {
    return (
      <section className="mx-auto max-w-3xl">
        <p className="text-sm font-medium text-accent">Sykes shops with you</p>
        <h1 className="mt-2 max-w-xl font-heading text-4xl font-semibold tracking-tight sm:text-5xl">
          Find a deal you can actually pay for
        </h1>
        <form
          className="ticket mt-8 space-y-4 rounded-3xl p-5 sm:p-7"
          onSubmit={(event) => {
            event.preventDefault()
            void onFindProducts()
          }}
        >
          <label className="block text-lg font-semibold tracking-tight" htmlFor="query">
            What do you want to buy?
          </label>
          <p className="max-w-lg text-sm leading-relaxed text-muted-foreground">
            Search real listings, then only offer to pay a merchant the checks can verify.
          </p>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Input
              id="query"
              value={query}
              placeholder="What are you looking for?"
              onChange={(event) => setLocalQuery(event.target.value)}
              disabled={asking}
              className="h-12 flex-1 rounded-full bg-[var(--paper)] px-5 text-base md:text-base"
            />
            <Button
              type="submit"
              disabled={asking || query.trim().length === 0}
              className="h-12 rounded-full px-6 text-base font-semibold"
            >
              {asking ? "Asking a few questions…" : "Find products"}
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {STARTERS.map((starter) => (
              <Button
                key={starter}
                type="button"
                variant="outline"
                className="h-9 rounded-full bg-[var(--paper)]"
                disabled={asking}
                onClick={() => setLocalQuery(starter)}
              >
                {starter}
              </Button>
            ))}
          </div>
          {error ? (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}
        </form>
        <ul className="mt-8 grid gap-6 sm:grid-cols-3">
          {PILLARS.map((pillar) => (
            <li key={pillar.title} className="border-t-2 border-[var(--marigold)] pt-3">
              <p className="text-sm font-semibold">{pillar.title}</p>
              <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{pillar.body}</p>
            </li>
          ))}
        </ul>
        <p className="mt-6 text-sm">
          <button type="button" className="font-medium text-accent underline" onClick={() => go("/how")}>
            How Sykes checks a store
          </button>
        </p>
      </section>
    )
  }

  const ready = picked !== null || freeText.trim().length > 0
  const last = index === questions.length - 1
  const progress = ((index + 1) / questions.length) * 100

  return (
    <div className="ticket mx-auto max-w-xl space-y-5 rounded-3xl p-6 sm:p-8">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">
          Question {index + 1} of {questions.length}
        </p>
        <p className="text-sm font-medium text-accent">A couple of details so the shelves match</p>
      </div>
      <div
        role="progressbar"
        aria-label="Question progress"
        aria-valuemin={1}
        aria-valuemax={questions.length}
        aria-valuenow={index + 1}
        className="h-1.5 overflow-hidden rounded-full bg-muted"
      >
        <div
          className="h-full rounded-full bg-[var(--marigold)] transition-[width]"
          style={{ width: `${progress}%` }}
        />
      </div>
      <h2 className="font-heading text-2xl font-semibold tracking-tight sm:text-3xl">{question.prompt}</h2>
      <div className="flex flex-wrap gap-2">
        {question.options.map((option) => {
          const selected = picked === option.id
          return (
            <Button
              key={option.id}
              type="button"
              variant={selected ? "default" : "outline"}
              className="h-11 rounded-full px-4"
              onClick={() => {
                setPicked(option.id)
                setFreeText("")
              }}
            >
              {option.label}
            </Button>
          )
        })}
      </div>
      <Input
        value={freeText}
        placeholder="Or type your own answer"
        className="h-11 rounded-full bg-[var(--paper)] px-5"
        onChange={(event) => {
          setFreeText(event.target.value)
          setPicked(null)
        }}
      />
      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}
      <div className="flex flex-wrap items-center gap-4">
        <Button type="button" disabled={!ready} className="h-11 rounded-full px-5 font-semibold" onClick={() => void onNext()}>
          {last ? "See results" : "Next"}
        </Button>
        {phase === "questions" ? (
          <button
            type="button"
            className="text-sm font-medium text-muted-foreground underline underline-offset-4"
            onClick={() => void submit(answers, true)}
          >
            Skip questions
          </button>
        ) : null}
      </div>
    </div>
  )
}
