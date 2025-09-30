# Frontend API Base Configuration

The React UI needs to know how to reach the FastAPI backend.

Preferred options (in order):
1. window.env.API_BASE injected at runtime (e.g., using a script that defines window.env.API_BASE = "https://your-api").
2. Environment variable at build time: REACT_APP_API_BASE.
3. Same-origin relative path (default when neither 1 nor 2 is present). This assumes a reverse proxy is routing / to the backend as needed.
4. Fallback to http://localhost:8000 for local development.

Examples:
- Local dev (separate ports):
  REACT_APP_API_BASE=http://localhost:8000 npm start

- Same-origin proxy:
  Leave REACT_APP_API_BASE unset; the app will use relative URLs.

Troubleshooting "Failed to fetch":
- Ensure the backend is running and reachable at the configured base.
- Check the browser console for CORS errors.
- Verify that proxies or preview environments allow reaching the backend host/port.
