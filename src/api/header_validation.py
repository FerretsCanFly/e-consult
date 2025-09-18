"""Header validation for infrastructure requirements."""

import logging
import os
from typing import Optional

from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param

from ..exceptions.base import HeaderValidationError

logger = logging.getLogger("header_validation")

# Header constants matching the Java infrastructure
PP_IDENTITY_HEADER_NAME = "pp-identity"
PP_CLUSTER_HEADER_NAME = "pp-cluster"


class HeaderValidationContext:
    """Context object containing validated header information."""
    
    def __init__(self, user_identity: str, cluster_id: Optional[str] = None):
        self.user_identity = user_identity
        self.cluster_id = cluster_id
    
    def __str__(self) -> str:
        return f"HeaderValidationContext(user_identity={self.user_identity}, cluster_id={self.cluster_id})"


def validate_required_headers(request: Request) -> HeaderValidationContext:
    """
    Validate required headers from Java infrastructure.
    
    This function validates the headers that are set by the Java application
    that acts as a proxy to maintain standard infrastructure operations.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        HeaderValidationContext: Context containing validated header information
        
    Raises:
        HTTPException: When required headers are missing or invalid in production mode
    """
    # Check for required pp-identity header
    user_identity = request.headers.get(PP_IDENTITY_HEADER_NAME)
    
    # In development mode (when DEVELOPMENT=true), use a default identity if header is missing
    is_development = os.getenv('DEVELOPMENT', 'false').lower() == 'true'
    
    if not user_identity:
        if is_development:
            user_identity = "dev-user"
            logger.info("Development mode: Using default user identity: %s", user_identity)
        else:
            logger.warning("Missing required header: %s", PP_IDENTITY_HEADER_NAME)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The user identity should be present on the header!",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Optional cluster header
    cluster_id = request.headers.get(PP_CLUSTER_HEADER_NAME)
    
    # Log successful validation
    logger.debug(
        "Header validation successful - user: %s, cluster: %s", 
        user_identity, 
        cluster_id or "not provided"
    )
    
    return HeaderValidationContext(
        user_identity=user_identity,
        cluster_id=cluster_id
    )


# FastAPI dependency function
def get_validated_headers(request: Request) -> HeaderValidationContext:
    """
    FastAPI dependency for header validation.
    
    Use this as a dependency in endpoints that require header validation:
    
    @app.get("/api/endpoint")
    async def endpoint(headers: HeaderValidationContext = Depends(get_validated_headers)):
        # headers.user_identity and headers.cluster_id are now available
        pass
    """
    return validate_required_headers(request)
