# Frontend API Base Configuration

The React UI needs to know how to reach the FastAPI backend.

Preferred options (in order):
1. window.env.API_BASE injected at runtime (e.g., using a script that defines window.env.API_BASE = "https://your-api").
2. Environment variable at build time: REACT_APP_API_BASE.
3. If the app is running on port 3000 (React dev server) and no base is set, the UI will default to http://localhost:8000 to reach FastAPI.
4. Same-origin relative path (when not on port 3000). This assumes a reverse proxy is routing API requests to the backend.
5. Fallback to http://localhost:8000 for local development.

Examples:
- Local dev (separate ports):
  REACT_APP_API_BASE=http://localhost:8000 npm start
  (If not set, the UI will automatically use http://localhost:8000 when running on port 3000.)

- Same-origin proxy:
  Leave REACT_APP_API_BASE unset; the app will use relative URLs when not on port 3000.

Troubleshooting "Failed to fetch" or 404 "Cannot POST /chat":
- If you see "Cannot POST /chat", you are likely posting to the React dev server (port 3000) instead of FastAPI.
  Fix by setting REACT_APP_API_BASE=http://localhost:8000 or relying on the new automatic default on port 3000.
- Ensure the backend is running and reachable at the configured base.
- Check the browser console for CORS errors.
- Verify that proxies or preview environments allow reaching the backend host/port.
