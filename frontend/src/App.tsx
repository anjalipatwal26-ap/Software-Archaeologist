import './App.css'

function App() {
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
                placeholder="https://github.com/username/repository"
              />

              <button type="button">
                Analyze Repository
              </button>
            </div>

            <p className="input-hint">
              Connect a GitHub repository to begin your investigation.
            </p>
          </div>
        </section>

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
      </main>
    </div>
  )
}

export default App