import React, { useState, useEffect, useMemo } from 'react';
import './App.css';

/**
 * Resolve backend base URL from environment or default appropriately.
 * Priority:
 * 1) window.env.API_BASE (runtime injected)
 * 2) process.env.REACT_APP_API_BASE (build-time)
 * 3) If on dev server (port 3000) and no base set -> http://localhost:8000
 * 4) Otherwise same-origin relative path (assumes reverse proxy)
 * 5) Final fallback: http://localhost:8000
 */
// PUBLIC_INTERFACE
function useApiBase() {
  const base = useMemo(() => {
    const w = typeof window !== 'undefined' ? window : {};
    const injected = (w.env && w.env.API_BASE) || process.env.REACT_APP_API_BASE;
    if (injected) return String(injected).replace(/\/+$/, '');

    // If in browser, check current origin/port
    if (typeof window !== 'undefined' && window.location) {
      const { origin, port } = window.location;
      // Common dev case: React runs on :3000 while FastAPI on :8000
      if (port === '3000') {
        return 'http://localhost:8000';
      }
      // In preview/proxy deployments, prefer same-origin relative path
      if (origin) {
        return ''; // use relative URLs (same-origin/proxy)
      }
    }

    // Fallback to localhost during local dev
    return 'http://localhost:8000';
  }, []);
  return base;
}

// PUBLIC_INTERFACE
function App() {
  const [theme, setTheme] = useState('light');
  const [sessionId, setSessionId] = useState(() => Math.random().toString(36).slice(2, 10));
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]); // {role, content}[]
  const [notes, setNotes] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recLoading, setRecLoading] = useState(false);
  const [recs, setRecs] = useState([]);
  const [error, setError] = useState('');
  const [health, setHealth] = useState(null);
  const apiBase = useApiBase();

  // Apply theme to document element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // PUBLIC_INTERFACE
  const toggleTheme = () => setTheme(prev => (prev === 'light' ? 'dark' : 'light'));

  function formatNetworkError(e, endpoint) {
    // Improve error message for fetch network/CORS failures
    if (e && e.name === 'TypeError' && /fetch/i.test(String(e))) {
      return `Network error calling ${endpoint}. Possible causes: CORS, wrong API base (${apiBase || 'same-origin'}), or backend not running.
Tip: If you see "Cannot POST ${endpoint}", the request likely hit the React dev server. Ensure API_BASE points to FastAPI (e.g., http://localhost:8000).`;
    }
    return e?.message || `Request failed for ${endpoint}`;
  }

  async function callChat() {
    setError('');
    const content = input.trim();
    if (!content) return;
    setLoading(true);
    try {
      const url = `${apiBase}/chat`.replace(/\/\//g, '/').replace(/^http(s)?:\//, 'http$1://');
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: { role: 'patient', content }
        })
      });
      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(`Chat error ${resp.status}: ${txt}`);
      }
      const data = await resp.json();
      // Append user message and agent reply
      setMessages(prev => [
        ...prev,
        { role: 'patient', content },
        { role: 'agent', content: data.reply }
      ]);
      setNotes(data.notes || null);
      setInput('');
    } catch (e) {
      setError(formatNetworkError(e, '/chat'));
    } finally {
      setLoading(false);
    }
  }

  async function callRecommend() {
    setError('');
    setRecLoading(true);
    try {
      const url = `${apiBase}/recommend`.replace(/\/\//g, '/').replace(/^http(s)?:\//, 'http$1://');
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(`Recommend error ${resp.status}: ${txt}`);
      }
      const data = await resp.json();
      setRecs(data.recommendations || []);
    } catch (e) {
      setError(formatNetworkError(e, '/recommend'));
    } finally {
      setRecLoading(false);
    }
  }

  async function checkHealth() {
    setError('');
    setHealth('Checking...');
    try {
      const url = `${apiBase}/`.replace(/\/\//g, '/').replace(/^http(s)?:\//, 'http$1://');
      const resp = await fetch(url, { method: 'GET' });
      if (!resp.ok) {
        const txt = await resp.text();
        setHealth(`Health check error ${resp.status}: ${txt}`);
        return;
      }
      const data = await resp.json();
      setHealth(`OK: ${data?.status || 'ok'} (${data?.service || 'api'})`);
    } catch (e) {
      setHealth(formatNetworkError(e, '/'));
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!loading) callChat();
    }
  }

  return (
    <div className="App">
      <header className="App-header" style={{ minHeight: 'auto', paddingTop: 32, paddingBottom: 32 }}>
        <button
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
        </button>

        <h1 style={{ marginTop: 16, color: 'var(--text-primary)' }}>Medical Decision Support Chat</h1>
        <p style={{ margin: 0, opacity: 0.8 }}>Session: <code>{sessionId}</code></p>
        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.8 }}>
          API base: <code>{apiBase || '(same-origin)'}</code>
          <button
            onClick={checkHealth}
            style={{ marginLeft: 8, background: '#e5e7eb', border: '1px solid #d1d5db', padding: '2px 6px', borderRadius: 6, cursor: 'pointer' }}
          >
            Check API
          </button>
          {health ? <span style={{ marginLeft: 8 }}>{health}</span> : null}
        </div>
      </header>

      <main style={{ maxWidth: 900, margin: '0 auto', padding: 16 }}>
        {error ? (
          <div style={{
            background: '#FEF2F2',
            color: '#991B1B',
            border: '1px solid #FCA5A5',
            padding: '10px 12px',
            borderRadius: 8,
            marginBottom: 12
          }}>
            {error}
          </div>
        ) : null}

        {/* Chat window */}
        <div style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          borderRadius: 12,
          padding: 16,
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
        }}>
          <div style={{ maxHeight: 300, overflowY: 'auto', paddingRight: 8 }}>
            {messages.length === 0 ? (
              <p style={{ opacity: 0.75, margin: 0 }}>Start by sending a message describing your symptoms.</p>
            ) : (
              messages.map((m, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    justifyContent: m.role === 'patient' ? 'flex-end' : 'flex-start',
                    marginBottom: 10
                  }}
                >
                  <div
                    style={{
                      background: m.role === 'patient' ? '#2563EB' : '#ffffff',
                      color: m.role === 'patient' ? '#ffffff' : 'var(--text-primary)',
                      border: '1px solid var(--border-color)',
                      padding: '8px 12px',
                      borderRadius: 10,
                      maxWidth: '75%',
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    <strong style={{ opacity: 0.8 }}>
                      {m.role === 'patient' ? 'You' : 'Assistant'}
                    </strong>
                    <div>{m.content}</div>
                  </div>
                </div>
              ))
            )}
          </div>

          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            <input
              type="text"
              placeholder="Type your message..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              style={{
                flex: 1,
                padding: '10px 12px',
                borderRadius: 8,
                border: '1px solid var(--border-color)',
                outline: 'none'
              }}
              aria-label="Message input"
            />
            <button
              onClick={callChat}
              disabled={loading || !input.trim()}
              style={{
                background: '#2563EB',
                color: '#ffffff',
                border: 'none',
                borderRadius: 8,
                padding: '10px 16px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
              aria-label="Send message"
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>

        {/* Notes panel */}
        <section style={{ marginTop: 16, display: 'grid', gridTemplateColumns: '1fr', gap: 12 }}>
          <div style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderRadius: 12,
            padding: 16
          }}>
            <h3 style={{ marginTop: 0 }}>Structured Notes</h3>
            {notes ? (
              <pre style={{
                background: 'var(--surface, #fff)',
                padding: 12,
                borderRadius: 8,
                overflowX: 'auto',
                border: '1px solid var(--border-color)'
              }}>{JSON.stringify(notes, null, 2)}</pre>
            ) : (
              <p style={{ opacity: 0.75, margin: 0 }}>No notes yet. Send a message to populate notes.</p>
            )}
          </div>

          <div style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderRadius: 12,
            padding: 16
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <h3 style={{ margin: 0, flex: 1 }}>Recommendations</h3>
              <button
                onClick={callRecommend}
                disabled={recLoading}
                style={{
                  background: '#F59E0B',
                  color: '#111827',
                  border: 'none',
                  borderRadius: 8,
                  padding: '8px 12px',
                  cursor: recLoading ? 'not-allowed' : 'pointer'
                }}
                aria-label="Get recommendations"
              >
                {recLoading ? 'Loading…' : 'Get Recommendations'}
              </button>
            </div>

            {recs && recs.length > 0 ? (
              <ul style={{ marginTop: 12 }}>
                {recs.map((r, i) => (
                  <li key={i} style={{ marginBottom: 8 }}>
                    <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>{r.type}:</span> {r.details}
                    {r.rationale ? <em style={{ opacity: 0.8 }}> — {r.rationale}</em> : null}
                  </li>
                ))}
              </ul>
            ) : (
              <p style={{ opacity: 0.75, marginTop: 12 }}>No recommendations yet.</p>
            )}
          </div>
        </section>

        <footer style={{ marginTop: 16, opacity: 0.8, fontSize: 12 }}>
          <p style={{ margin: 0 }}>
            Disclaimer: This system provides information for educational purposes only and is not a substitute for professional medical advice.
          </p>
        </footer>
      </main>
    </div>
  );
}

export default App;
