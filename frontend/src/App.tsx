import { Routes, Route, Link } from 'react-router-dom'
import { PlannerForm } from './components/PlannerForm'
import { PlanView } from './components/PlanView'
import { QuizPage } from './components/QuizPage'

export default function App() {
  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '1rem' }}>
      <header style={{ marginBottom: '1rem' }}>
        <h1>AI Exam Preparation Planner</h1>
        <nav style={{ display: 'flex', gap: '1rem' }}>
          <Link to="/">Planner</Link>
          <Link to="/quiz">Quiz</Link>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<PlannerForm />} />
        <Route path="/plan" element={<PlanView />} />
        <Route path="/quiz" element={<QuizPage />} />
      </Routes>
    </div>
  )
}
