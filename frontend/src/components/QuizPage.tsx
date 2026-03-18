import { type FormEvent, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

interface Question {
  id: number
  topic: string
  question: string
  options: string[]
  correct_index: number
}

export function QuizPage() {
  const navigate = useNavigate()
  const [questions, setQuestions] = useState<Question[]>([])
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [result, setResult] = useState<{
    score: number
    topic_strengths: Record<string, string>
    topic_confidence: Record<string, number>
  } | null>(null)

  const topicsFromPlanner = useMemo(() => {
    try {
      const raw = localStorage.getItem('ai_exam_planner_topics') || ''
      return raw
        .split('\n')
        .map((t) => t.trim())
        .filter((t) => t.length > 0)
    } catch {
      return []
    }
  }, [])

  useEffect(() => {
    // Quiz must be based on topics entered by the student in Planner.
    // We store them in localStorage from PlannerForm.
    if (!topicsFromPlanner.length) {
      setQuestions([])
      return
    }

    fetch('http://localhost:5000/api/quiz/questions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topics: topicsFromPlanner }),
    })
      .then((r) => r.json())
      .then((data) => setQuestions(data.questions || []))
      .catch(() => setQuestions([]))
  }, [topicsFromPlanner])

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const payloadAnswers = questions.map((q) => ({
      id: q.id,
      topic: q.topic,
      correct_index: q.correct_index,
      selected_index: answers[q.id] ?? -1,
    }))

    const topics = Array.from(new Set(questions.map((q) => q.topic)))

    const resp = await fetch('https://flask1-backend.onrender.com/api/quiz/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers: payloadAnswers, topics }),
    })
    const data = await resp.json()
    setResult(data || null)

    // Save quiz-derived performance so Planner can auto-fill.
    try {
      localStorage.setItem('ai_exam_planner_quiz_results', JSON.stringify(data))
    } catch {
      // ignore
    }
  }

  return (
    <section>
      <h2>Quick quiz (optional)</h2>
      {!topicsFromPlanner.length ? (
        <div>
          <p>Please enter your topics in the Planner first, then come back here for a topic-based quiz.</p>
          <button onClick={() => navigate('/')}>Go to planner</button>
        </div>
      ) : !questions.length ? (
        <p>Loading quiz…</p>
      ) : (
        <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {questions.map((q) => (
            <div key={q.id} style={{ border: '1px solid #eee', padding: '0.5rem' }}>
              <p>
                <strong>{q.topic}:</strong> {q.question}
              </p>
              {q.options.map((opt, idx) => (
                <label key={idx} style={{ display: 'block' }}>
                  <input
                    type="radio"
                    name={`q-${q.id}`}
                    value={idx}
                    checked={answers[q.id] === idx}
                    onChange={() =>
                      setAnswers((prev) => ({
                        ...prev,
                        [q.id]: idx,
                      }))
                    }
                  />
                  {opt}
                </label>
              ))}
            </div>
          ))}
          <button type="submit">Evaluate strengths</button>
        </form>
      )}

      {result && (
        <div style={{ marginTop: '1rem' }}>
          <h3>Quiz results</h3>
          <p>
            <strong>Score:</strong> {result.score}%
          </p>
          <h4>Topic strengths (with confidence)</h4>
          <ul>
            {Object.entries(result.topic_strengths || {}).map(([topic, strength]) => (
              <li key={topic}>
                <strong>{topic}</strong>: {strength} ({result.topic_confidence?.[topic] ?? 0}%)
              </li>
            ))}
          </ul>
          <p style={{ fontSize: '0.9rem' }}>
            Now go back to Planner — your strength/confidence will be auto-filled.
          </p>
          <button onClick={() => navigate('/')}>Back to planner</button>
        </div>
      )}
    </section>
  )
}
