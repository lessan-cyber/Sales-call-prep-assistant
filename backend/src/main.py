from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .routers import profile, prep, dashboard
from .supabase_client import create_supabase
from .services.supabase_service import init_supabase_service
from .utils.logger import info, error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the Supabase client's lifecycle."""
    client = await create_supabase()
    app.state.supabase = client
    await init_supabase_service(client)
    info("Supabase client and service initialized.")
    yield
    info("Supabase client closing.")
    await client.close()


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router, prefix="/api/auth", tags=["Profile"])
app.include_router(prep.router, prefix="/api", tags=["Prep"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])


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
