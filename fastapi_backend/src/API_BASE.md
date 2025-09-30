# Frontend API Base Configuration

The React UI needs to know how to reach the FastAPI backend.

Preferred options (in order):
1. window.env.API_BASE injected at runtime (e.g., using a script that defines window.env.API_BASE = "https://your-api").
2. Environment variable at build time: REACT_APP_API_BASE.
3. If the app is running on port 3000 (React dev server) and no base is set, the UI will default to http://localhost:8000 to reach FastAPI.
4. Same-origin relative path (when not on port 3000). This assumes a reverse proxy is routing API requests to the backend.
5. Fallback to http://localhost:8000 for local development.

URL building:
- The app uses a robust joinUrl helper to combine the base and path (e.g., /chat). It supports absolute bases like http://localhost:8000 and same-origin relative base ("").
- This avoids malformed URLs and ensures requests hit FastAPI instead of the React dev server.

Examples:
- Local dev (separate ports):
  REACT_APP_API_BASE=http://localhost:8000 npm start
  (If not set, the UI will automatically use http://localhost:8000 when running on port 3000.)

- Same-origin proxy:
  Leave REACT_APP_API_BASE unset; the app will use relative URLs when not on port 3000.

Troubleshooting "Failed to fetch" or 404 "Cannot POST /chat":
- "Cannot POST /chat" usually means the request was sent to the React dev/preview server instead of FastAPI. Ensure API_BASE points to FastAPI (e.g., http://localhost:8000) or a valid reverse proxy.
- Confirm backend is running: uvicorn main:app --reload (in fastapi_backend/backend).
- Check the header in the app: it shows the resolved API base. It should be http://localhost:8000 for local dev.
- Check for CORS errors in the browser console.
- Verify that proxies or preview environments allow reaching the backend host/port.
