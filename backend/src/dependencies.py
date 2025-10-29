from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from gotrue.errors import AuthApiError
from gotrue import User
from supabase import AsyncClient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def get_supabase_client(request: Request) -> AsyncClient:
    """Dependency to get the Supabase client from the app state."""
    return request.app.state.supabase


def get_current_user(
    token: str = Depends(oauth2_scheme),
    supabase: AsyncClient = Depends(get_supabase_client),
) -> User:
    """Dependency to get the current user from a JWT token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user = supabase.auth.get_user(token)
        return user
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
