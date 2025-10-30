from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from .routers import profile, prep



from .supabase_client import create_supabase

from .utils.logger import info, error





@asynccontextmanager

async def lifespan(app: FastAPI):

    """Manage the Supabase client's lifecycle."""

    client = await create_supabase()

    app.state.supabase = client

    info("Supabase client initialized and attached to app state.")

    yield

    info("Supabase client closing.")

    # await client.close()





app = FastAPI(lifespan=lifespan)



app.include_router(profile.router, prefix="/api/auth", tags=["Profile"])

app.include_router(prep.router, prefix="/api", tags=["Prep"])


@app.get("/")
async def read_root():
    info("Root endpoint accessed.")
    return {"message": "Hello from Sales Call Prep Assistant Backend"}


@app.get("/health")
async def health_check():
    """Checks the connection to Supabase."""
    supabase = await create_supabase()
    try:
        # Perform a lightweight, read-only operation to check the connection.
        _ = supabase.storage.list_buckets()
        info("Supabase connection successful.")
        return {"status": "ok", "message": "Supabase connection successful."}
    except Exception as e:
        error(f"Supabase connection failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Supabase connection failed: {e}",
        )
