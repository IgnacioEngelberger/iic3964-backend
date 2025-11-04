from supabase import Client, create_client

from app.core.config import settings

if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    raise EnvironmentError("SUPABASE_URL y SUPABASE_KEY deben estar en el .env")

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
