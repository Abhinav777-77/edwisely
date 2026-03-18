import { useLocation, useNavigate } from 'react-router-dom'

interface PlanItem {
  topic: string
  focus: string
  notes: string
}

interface DayPlan {
  day: number
  items: PlanItem[]
}

interface LocationState {
  planResponse?: {
    plan?: {
      days?: DayPlan[]
    }
  }
}

export function PlanView() {
  const location = useLocation()
  const navigate = useNavigate()
  const state = (location.state || {}) as LocationState

  const days = state.planResponse?.plan?.days || []

  if (!days.length) {
    return (
      <section>
        <p>No plan data. Please generate a plan first.</p>
        <button onClick={() => navigate('/')}>Go to planner</button>
      </section>
    )
  }

  return (
    <section>
      <h2>Your day-wise study plan</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {days.map((day) => (
          <div key={day.day} style={{ border: '1px solid #ddd', padding: '0.75rem' }}>
            <h3>Day {day.day}</h3>
            <ul>
              {day.items.map((item, idx) => (
                <li key={idx}>
                  <strong>{item.topic}</strong> — <em>{item.focus}</em>
                  <div style={{ fontSize: '0.9rem' }}>{item.notes}</div>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  )
}
