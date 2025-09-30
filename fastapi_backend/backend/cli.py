import uvicorn

if __name__ == "__main__":
    # Run on 0.0.0.0:3000 by default for Kavia cloud preview compatibility.
    # Use env vars UVICORN_HOST/UVICORN_PORT if provided to override.
    import os
    host = os.getenv("UVICORN_HOST", "0.0.0.0")
    try:
        port = int(os.getenv("UVICORN_PORT", "3000"))
    except ValueError:
        port = 3000
    uvicorn.run("main:app", host=host, port=port, reload=True)
