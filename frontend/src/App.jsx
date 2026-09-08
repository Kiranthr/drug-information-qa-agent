import { useEffect, useState } from 'react'
import {
  AlertTriangle,
  BookOpen,
  ChevronDown,
  FileText,
  Loader2,
  MessageCircle,
  Search,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'

import {
  fetchMedicines,
  askQuestion,
} from './api/client'

import './App.css'

function App() {
  const [medicines, setMedicines] = useState([])
  const [selectedMedicine, setSelectedMedicine] = useState('')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingMedicines, setLoadingMedicines] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadMedicines()
  }, [])

  async function loadMedicines() {
    try {
      setLoadingMedicines(true)
      const data = await fetchMedicines()
      setMedicines(data)

      if (data.length > 0) {
        setSelectedMedicine(data[0].id)
      }
    } catch (err) {
      setError('Unable to load medicines. Please make sure the backend is running.')
    } finally {
      setLoadingMedicines(false)
    }
  }

  async function handleAskQuestion(event) {
    event.preventDefault()

    if (!question.trim()) {
      setError('Please enter a question.')
      return
    }

    setError('')
    setAnswer(null)
    setLoading(true)

    try {
      const sessionId =
        sessionStorage.getItem('drug_qa_session') ||
        crypto.randomUUID()

      sessionStorage.setItem('drug_qa_session', sessionId)

      const result = await askQuestion({
        question: question.trim(),
        medicineId: selectedMedicine || null,
        sessionId,
      })

      setAnswer(result)
    } catch (err) {
      setError(err.message || 'Unable to get an answer.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <ShieldCheck size={25} />
          </div>

          <div>
            <h1>Drug Information Q&A</h1>
            <p>Evidence-grounded medicine information</p>
          </div>
        </div>

        <div className="status-pill">
          <span className="status-dot"></span>
          RAG System Online
        </div>
      </header>

      <main className="main-container">

        <section className="hero-section">
          <div className="hero-badge">
            <Sparkles size={16} />
            AI-Powered • Evidence Grounded
          </div>

          <h2>
            Ask questions about
            <span> medicines with confidence.</span>
          </h2>

          <p>
            Get information grounded in official medicine documents,
            with transparent sources and safety-focused responses.
          </p>
        </section>

        <section className="notice">
          <div className="notice-icon">
            <AlertTriangle size={20} />
          </div>

          <div>
            <strong>Medical information notice</strong>
            <p>
              This assistant provides educational information from
              official regulatory documents. It is not a doctor and
              does not provide diagnosis, prescriptions, or personalized
              medical advice.
            </p>
          </div>
        </section>

        <section className="question-card">
          <div className="section-heading">
            <div className="heading-icon">
              <MessageCircle size={21} />
            </div>

            <div>
              <h3>Ask a medicine question</h3>
              <p>Select a medicine and ask your question.</p>
            </div>
          </div>

          <form onSubmit={handleAskQuestion}>

            <label htmlFor="medicine">
              Medicine
            </label>

            <div className="select-wrapper">
              <select
                id="medicine"
                value={selectedMedicine}
                onChange={(event) =>
                  setSelectedMedicine(event.target.value)
                }
                disabled={loadingMedicines}
              >
                {loadingMedicines ? (
                  <option>Loading medicines...</option>
                ) : (
                  medicines.map((medicine) => (
                    <option key={medicine.id} value={medicine.id}>
                      {medicine.generic_name}
                    </option>
                  ))
                )}
              </select>

              <ChevronDown size={18} />
            </div>

            <label htmlFor="question">
              Your question
            </label>

            <div className="question-input-wrapper">
              <Search size={19} />

              <input
                id="question"
                type="text"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Example: What are the common side effects?"
                disabled={loading}
              />
            </div>

            <button
              className="ask-button"
              type="submit"
              disabled={loading || loadingMedicines}
            >
              {loading ? (
                <>
                  <Loader2 className="spin" size={19} />
                  Searching evidence...
                </>
              ) : (
                <>
                  <Sparkles size={19} />
                  Ask Question
                </>
              )}
            </button>
          </form>

          {error && (
            <div className="error-message">
              <AlertTriangle size={18} />
              {error}
            </div>
          )}
        </section>

        {loading && (
          <section className="loading-card">
            <Loader2 className="spin" size={28} />
            <div>
              <strong>Searching official evidence...</strong>
              <p>
                Retrieving relevant information from the medicine
                knowledge base.
              </p>
            </div>
          </section>
        )}

        {answer && !loading && (
          <section className="answer-card">

            <div className="answer-header">
              <div className="section-heading">
                <div className="heading-icon success">
                  <Sparkles size={21} />
                </div>

                <div>
                  <h3>Evidence-grounded answer</h3>
                  <p>
                    Generated using retrieved medicine information
                  </p>
                </div>
              </div>
            </div>

            <div className="answer-content">
              {answer.answer || answer.response || 'No answer returned.'}
            </div>

            {answer.citations && answer.citations.length > 0 && (
              <div className="sources-section">
                <div className="sources-title">
                  <BookOpen size={19} />
                  Sources
                </div>

                <div className="sources-list">
                  {answer.citations.map((citation, index) => (
                    <div
                      className="source-item"
                      key={citation.id || index}
                    >
                      <FileText size={18} />

                      <div>
                        <strong>
                          {citation.document_name ||
                            citation.title ||
                            `Source ${index + 1}`}
                        </strong>

                        <p>
                          {citation.section ||
                            citation.excerpt ||
                            citation.text ||
                            'Retrieved evidence from the medicine document.'}
                        </p>

                        {citation.page && (
                          <span>Page {citation.page}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {answer.safety && (
              <div className="safety-result">
                <ShieldCheck size={18} />

                <div>
                  <strong>
                    Safety classification:{' '}
                    {answer.safety.classification ||
                      answer.safety.category ||
                      'Informational'}
                  </strong>

                  {answer.safety.disclaimer && (
                    <p>{answer.safety.disclaimer}</p>
                  )}
                </div>
              </div>
            )}
          </section>
        )}

        <section className="feature-grid">

          <div className="feature-card">
            <ShieldCheck size={23} />
            <h3>Safety focused</h3>
            <p>
              Built-in guardrails help keep responses within
              informational boundaries.
            </p>
          </div>

          <div className="feature-card">
            <BookOpen size={23} />
            <h3>Evidence grounded</h3>
            <p>
              Answers are generated using retrieved information
              from the medicine knowledge base.
            </p>
          </div>

          <div className="feature-card">
            <FileText size={23} />
            <h3>Transparent sources</h3>
            <p>
              Retrieved evidence and source information are shown
              alongside answers.
            </p>
          </div>

        </section>

      </main>

      <footer>
        <p>
          Drug Information Q&A Agent • For educational purposes only
        </p>
      </footer>
    </div>
  )
}

export default App