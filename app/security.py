from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader, APIKeyQuery
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

def _extract_key(request: Request, header_key: str = None, query_key: str = None) -> str:
    key = header_key or query_key or request.query_params.get("key")
    if not key:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            key = auth_header.split(" ", 1)[1].strip()
    return key or ""

async def verify_api_key(
    request: Request,
    header_key: str = Security(api_key_header),
    query_key: str = Security(api_key_query)
) -> str:
    """
    Validates API key for read-only rate requests.
    If REQUIRE_API_KEY is False, public access is permitted (any or no key).
    """
    key = _extract_key(request, header_key, query_key)
    
    if not settings.REQUIRE_API_KEY:
        return key or "public"
    
    if not key or key not in settings.ALLOWED_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": "error",
                "message": "Invalid or missing API key. Provide via 'X-API-Key' header, 'Authorization: Bearer <key>', or '?key=<key>' parameter."
            }
        )
        
    return key

async def verify_admin_key(
    request: Request,
    header_key: str = Security(api_key_header),
    query_key: str = Security(api_key_query)
) -> str:
    """
    Validates administrative access for manual refresh.
    """
    key = _extract_key(request, header_key, query_key)
    if not key or key not in settings.ALLOWED_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": "error",
                "message": "Admin API key required for manual refresh."
            }
        )
    return key
