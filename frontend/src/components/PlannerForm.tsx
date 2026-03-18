import { type FormEvent, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

interface TopicInput {
  name: string
  estimated_hours: number
}

interface TopicPerformance {
  strength: 'weak' | 'medium' | 'strong'
  confidence: number // 0-100
}

export function PlannerForm() {
  const [days, setDays] = useState(7)
  const [topicsText, setTopicsText] = useState('Algebra\nCalculus\nPhysics')
  const [performance, setPerformance] = useState<Record<string, TopicPerformance>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const topicNames = useMemo(
    () =>
      topicsText
        .split('\n')
        .map((t) => t.trim())
        .filter((t) => t.length > 0),
    [topicsText],
  )

  // Persist topics so quiz can generate topic-based questions
  useEffect(() => {
    try {
      localStorage.setItem('ai_exam_planner_topics', topicsText)
    } catch {
      // ignore
    }
  }, [topicsText])

  // If quiz results exist, auto-fill performance (strength + confidence)
  useEffect(() => {
    try {
      const raw = localStorage.getItem('ai_exam_planner_quiz_results')
      if (!raw) return
      const parsed = JSON.parse(raw)
      const topic_strengths: Record<string, string> = parsed?.topic_strengths || {}
      const topic_confidence: Record<string, number> = parsed?.topic_confidence || {}

      setPerformance((prev) => {
        const next = { ...prev }
        Object.keys(topic_strengths).forEach((topic) => {
          const strength = topic_strengths[topic] as TopicPerformance['strength']
          const confidence = Number(topic_confidence?.[topic] ?? 50)
          next[topic] = {
            strength: strength === 'weak' || strength === 'medium' || strength === 'strong' ? strength : 'medium',
            confidence: Number.isFinite(confidence) ? Math.max(0, Math.min(100, confidence)) : 50,
          }
        })
        return next
      })
    } catch {
      // ignore
    }
  }, [])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const topics: TopicInput[] = topicNames.map((name) => ({ name, estimated_hours: 2 }))

    // Build performance payload with strength + confidence if provided
    const perfPayload: Record<string, { strength: string; confidence: number }> = {}
    topicNames.forEach((name) => {
      const p = performance[name]
      if (p) {
        perfPayload[name] = {
          strength: p.strength,
          confidence: p.confidence,
        }
      }
    })

    try {
      const resp = await fetch('https://flask1-backend.onrender.com/api/plan/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ days, topics, performance: perfPayload }),
      })

      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}))
        throw new Error(data.error || 'Failed to generate plan')
      }

      const data = await resp.json()
      try {
        localStorage.setItem('ai_exam_planner_last_plan', JSON.stringify(data))
      } catch {
        // ignore
      }
      navigate('/plan', { state: { planResponse: data } })
    } catch (err: any) {
      setError(err.message || 'Unexpected error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>Create your study plan</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <label>
          Days until exam:
          <input
            type="number"
            min={1}
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
          />
        </label>

        <label>
          Subjects / topics (one per line):
          <textarea
            rows={5}
            value={topicsText}
            onChange={(e) => setTopicsText(e.target.value)}
          />
        </label>

        {topicNames.length > 0 && (
          <div>
            <p style={{ fontSize: '0.9rem', marginBottom: '0.25rem' }}>
              Optional: mark your strength and confidence for each topic.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {topicNames.map((name) => {
                const current = performance[name] ?? { strength: 'medium', confidence: 50 }
                return (
                  <div key={name} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ minWidth: '120px' }}>{name}</span>
                    <select
                      value={current.strength}
                      onChange={(e) =>
                        setPerformance((prev) => ({
                          ...prev,
                          [name]: {
                            strength: e.target.value as TopicPerformance['strength'],
                            confidence: current.confidence,
                          },
                        }))
                      }
                    >
                      <option value="weak">Weak</option>
                      <option value="medium">Medium</option>
                      <option value="strong">Strong</option>
                    </select>
                    <input
                      type="number"
                      min={0}
                      max={100}
                      value={current.confidence}
                      onChange={(e) =>
                        setPerformance((prev) => ({
                          ...prev,
                          [name]: {
                            strength: current.strength,
                            confidence: Number(e.target.value),
                          },
                        }))
                      }
                      style={{ width: '70px' }}
                    />
                    <span style={{ fontSize: '0.8rem' }}>% confidence</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Generating…' : 'Generate plan'}
        </button>

        {error && <p style={{ color: 'red' }}>{error}</p>}
      </form>

      <p style={{ marginTop: '1rem', fontSize: '0.9rem' }}>
        Optional: Use the quiz tab to estimate your strengths and weaknesses, then come back here.
      </p>
    </section>
  )
}
