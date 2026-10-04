import { useState } from 'react'
import './App.css'
import DependencyGraph from './components/DependencyGraph'

type Commit = {
  sha: string
  message: string
  author?: string | null
  date?: string | null
}

type Repository = {
  repository_url: string
  repository_path?: string
  status: string
  message: string
  name?: string
  owner?: string
  description?: string
  language?: string
  stars?: number
  forks?: number
  open_issues?: number
  default_branch?: string
  commits?: Commit[]
}

function App() {
  const [repositoryUrl, setRepositoryUrl] = useState('')
  const [repository, setRepository] = useState<Repository | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const analyzeRepository = async () => {
    if (!repositoryUrl.trim()) {
      setError('Please enter a GitHub repository URL.')
      return
    }

    setLoading(true)
    setError('')
    setRepository(null)

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/api/repositories/analyze',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            repository_url: repositoryUrl,
          }),
        },
      )

      if (!response.ok) {
        throw new Error(
          'Something went wrong while analyzing the repository.',
        )
      }

      const data: Repository = await response.json()

      if (data.status !== 'valid') {
        setError(data.message)
        return
      }

      setRepository(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to connect to the backend.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">SA</div>

          <div>
            <h1>Software Archaeologist</h1>
            <span>Understand how your codebase evolved.</span>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          System Ready
        </div>
      </header>

      <main className="dashboard">
        {/* HERO SECTION */}

        <section className="hero-section">
          <div className="hero-content">
            <p className="eyebrow">CODEBASE FORENSICS</p>

            <h2>
              Discover the
              <span> story behind your code.</span>
            </h2>

            <p className="hero-description">
              Analyze Git history, source code, dependencies, and documentation
              to understand how your software evolved and why it looks the way
              it does today.
            </p>

            <div className="repository-input">
              <input
                type="text"
                value={repositoryUrl}
                onChange={(event) => setRepositoryUrl(event.target.value)}
                placeholder="https://github.com/username/repository"
              />

              <button
                type="button"
                onClick={analyzeRepository}
                disabled={loading}
              >
                {loading ? 'Analyzing...' : 'Analyze Repository'}
              </button>
            </div>

            <p className="input-hint">
              Connect a GitHub repository to begin your investigation.
            </p>

            {error && <p className="error-message">{error}</p>}
          </div>
        </section>

        {/* REPOSITORY RESULT */}

        {repository && (
          <section className="repository-result">
            <div className="section-heading">
              <div>
                <p className="eyebrow">REPOSITORY FOUND</p>

                <h3>
                  {repository.owner}/{repository.name}
                </h3>
              </div>

              <span className="repository-language">
                {repository.language ?? 'Unknown'}
              </span>
            </div>

            <p className="repository-description">
              {repository.description ?? 'No description available.'}
            </p>

            <div className="repository-stats">
              <div>
                <strong>{repository.stars ?? 0}</strong>
                <span>Stars</span>
              </div>

              <div>
                <strong>{repository.forks ?? 0}</strong>
                <span>Forks</span>
              </div>

              <div>
                <strong>{repository.open_issues ?? 0}</strong>
                <span>Open Issues</span>
              </div>

              <div>
                <strong>{repository.default_branch ?? '-'}</strong>
                <span>Default Branch</span>
              </div>
            </div>
          </section>
        )}

        {/* EVOLUTION TIMELINE */}

        {repository &&
          repository.commits &&
          repository.commits.length > 0 && (
            <section className="timeline-section">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">EVOLUTION TIMELINE</p>

                  <h3>Recent changes</h3>
                </div>

                <span className="timeline-count">
                  {repository.commits.length} commits
                </span>
              </div>

              <div className="timeline">
                {repository.commits.map((commit) => (
                  <div className="timeline-item" key={commit.sha}>
                    <div className="timeline-dot"></div>

                    <div className="timeline-content">
                      <h4>
                    {commit.message.split('\n')[0].replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')}
</h4>
                      <div className="timeline-meta">
                        <span>
                          {commit.author ?? 'Unknown author'}
                        </span>

                        {commit.date && (
                          <span>
                            {new Date(commit.date).toLocaleDateString()}
                          </span>
                        )}
                      </div>

                      <span className="commit-sha">
                        {commit.sha.slice(0, 7)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

        {/* INVESTIGATION OVERVIEW */}

        <section className="overview-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">INVESTIGATION OVERVIEW</p>

              <h3>What we will uncover</h3>
            </div>

            <span className="coming-soon">Coming soon</span>
          </div>

          <div className="overview-grid">
            <div className="overview-card">
              <div className="card-number">01</div>

              <h4>Evolution Timeline</h4>

              <p>
                Trace important changes and understand how the codebase
                evolved over time.
              </p>
            </div>

            <div className="overview-card">
              <div className="card-number">02</div>

              <h4>Dependency Graph</h4>

              <p>
                Explore relationships between modules, files, functions, and
                components.
              </p>
            </div>

            <div className="overview-card">
              <div className="card-number">03</div>

              <h4>Change Hotspots</h4>

              <p>
                Identify areas of the codebase that change frequently and may
                require investigation.
              </p>
            </div>

            <div className="overview-card">
              <div className="card-number">04</div>

              <h4>Documentation Drift</h4>

              <p>
                Detect situations where documentation no longer matches the
                actual implementation.
              </p>
            </div>
          </div>
        </section>

        {/* DEPENDENCY GRAPH */}

        <section className="graph-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">CODEBASE MAP</p>

              <h3>Dependency Graph</h3>
            </div>
          </div>

          <DependencyGraph repositoryPath={repository?.repository_path} />
        </section>
      </main>
    </div>
  )
}

export default App