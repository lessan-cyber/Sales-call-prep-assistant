from supabase import acreate_client, AsyncClient
from .config import settings

# Initialize the Supabase client using the service key for backend operations,
# as it will need privileges to bypass RLS for certain tasks like writing to the cache.


async def create_supabase() -> AsyncClient:
    supabase: AsyncClient = await acreate_client(
        settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY
    )
    return supabase
