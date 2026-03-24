from fastapi import Header, HTTPException
from app.core.config import settings


def verify_admin_key(x_admin_key: str = Header(None)):
    if not x_admin_key or x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key not in settings.api_keys:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    return x_api_key