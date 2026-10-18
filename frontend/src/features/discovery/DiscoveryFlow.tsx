import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { createSession, getSnapshot, submitAnswers } from "@/lib/api.ts"
import type { Answer, Question } from "@/lib/types.ts"
import { useSessionStore } from "@/store/sessionStore.ts"

type Props = {
  onStarted: (sessionId: string) => void
}

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

  const question = questions[index]

  async function onFindProducts() {
    const trimmed = query.trim()
    if (!trimmed) return
    setQuery(trimmed)
    setError(null)
    setPhase("submitting")
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
      setPhase("query")
      setError("The search could not reach the server. Leave this page open and try again.")
    }
  }

  function currentAnswer(): Answer | null {
    if (!question) return null
    if (picked) return { question_id: question.id, option_id: picked }
    if (freeText.trim()) return { question_id: question.id, text: freeText.trim() }
    return null
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
    setPhase("submitting")
    setError(null)
    try {
      const submitted = await submitAnswers(sessionId, {
        answers: nextAnswers,
        skip_remaining: false,
      })
      const snapshot = await getSnapshot(submitted.session_id)
      startSession(snapshot)
      onStarted(snapshot.session_id)
    } catch (caught) {
      setPhase("questions")
      setError(caught instanceof Error ? caught.message : "Something went wrong")
    }
  }

  if (phase === "submitting") {
    return (
      <div className="space-y-4" aria-busy="true">
        <p className="text-lg">Looking at retailers…</p>
        <Skeleton className="h-28 w-full" />
        <Skeleton className="h-28 w-full" />
        <Skeleton className="h-28 w-full" />
      </div>
    )
  }

  if (phase === "query" || !question) {
    return (
      <form
        className="mx-auto max-w-xl space-y-4"
        onSubmit={(event) => {
          event.preventDefault()
          void onFindProducts()
        }}
      >
        <label className="block text-lg font-medium" htmlFor="query">
          What do you want to buy?
        </label>
        <Input
          id="query"
          value={query}
          placeholder="What are you looking for?"
          onChange={(event) => setLocalQuery(event.target.value)}
        />
        <Button type="submit" disabled={query.trim().length === 0}>
          Find products
        </Button>
        {error ? (
          <p className="text-sm text-red-800" role="alert">
            {error}
          </p>
        ) : null}
      </form>
    )
  }

  const ready = picked !== null || freeText.trim().length > 0
  const last = index === questions.length - 1

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <p className="text-sm text-stone-500">
        Question {index + 1} of {questions.length}
      </p>
      <h2 className="text-2xl font-semibold">{question.prompt}</h2>
      <div className="flex flex-wrap gap-2">
        {question.options.map((option) => {
          const selected = picked === option.id
          return (
            <Button
              key={option.id}
              type="button"
              variant={selected ? "default" : "outline"}
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
      {question.allow_free_text ? (
        <Input
          value={freeText}
          placeholder="Or type your own answer"
          onChange={(event) => {
            setFreeText(event.target.value)
            setPicked(null)
          }}
        />
      ) : null}
      {error ? (
        <p className="text-sm text-red-800" role="alert">
          {error}
        </p>
      ) : null}
      <Button type="button" disabled={!ready} onClick={() => void onNext()}>
        {last ? "See results" : "Next"}
      </Button>
    </div>
  )
}
