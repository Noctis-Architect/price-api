from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader, APIKeyQuery
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

async def verify_api_key(
    request: Request,
    header_key: str = Security(api_key_header),
    query_key: str = Security(api_key_query)
) -> str:
    """
    Validates API key from X-API-Key header, Authorization Bearer header, or api_key query param.
    """
    if not settings.REQUIRE_API_KEY:
        return "public"
    
    # Check X-API-Key header or query param
    key = header_key or query_key
    
    # Check Authorization: Bearer <token>
    if not key:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            key = auth_header.split(" ", 1)[1].strip()
            
    if not key or key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": "error",
                "message": "Invalid or missing API key. Provide via 'X-API-Key' header, 'Authorization: Bearer <key>', or '?api_key=<key>' parameter."
            }
        )
        
    return key
