from fastapi import FastAPI, HTTPException
from .supabase_client import supabase

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Hello from Sales Call Prep Assistant Backend"}


@app.get("/health")
async def health_check():
    """Checks the connection to Supabase."""
    try:
        # Perform a lightweight, read-only operation to check the connection.
        _ = supabase.storage.list_buckets()
        return {"status": "ok", "message": "Supabase connection successful."}
    except Exception as e:
        # If the connection fails, return a 503 Service Unavailable error.
        raise HTTPException(
            status_code=503,
            detail=f"Supabase connection failed: {e}",
        )
