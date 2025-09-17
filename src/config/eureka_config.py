"""Eureka client configuration for service registry."""

import logging
import os
from typing import Optional

import py_eureka_client.eureka_client as eureka_client


logger = logging.getLogger("eureka")


class EurekaConfig:
    """Eureka client configuration and management."""
    
    def __init__(
        self, 
        eureka_server: str = "http://localhost:8761/eureka/",
        app_name: str = "python-ai-service",
        instance_port: int = 8000,
        instance_host: str = "localhost",
        username: str = None,
        password: str = None,
        enabled: bool = False
    ):
        self.eureka_server = eureka_server
        self.app_name = app_name
        self.instance_port = instance_port
        self.instance_host = instance_host
        self.username = username
        self.password = password
        self.enabled = enabled
        self._is_registered = False

    async def register_with_eureka(self) -> None:
        """Register the application with Eureka server."""
        if not self.enabled:
            logger.info("Eureka registration is disabled")
            return
            
        if self._is_registered:
            logger.warning("Application is already registered with Eureka")
            return

        try:
            logger.info(f"🚀 Registering {self.app_name} with Eureka server at {self.eureka_server}")
            logger.info(f"📡 Port: {self.instance_port}, Host: {self.instance_host}")
            
            # Error callback for debugging
            def on_error(error_type: str, error: Exception):
                logger.error(f"💥 Eureka error - Type: {error_type}, Error: {error}")
            
            # Base configuration
            config = {
                "eureka_server": self.eureka_server,
                "app_name": self.app_name,
                "instance_port": self.instance_port,
                "instance_host": self.instance_host,
                "on_error": on_error,
                "health_check_url": "/actuator/health",
                "status_page_url": "/actuator/info",
                "home_page_url": "/"
            }
            
            # Add authentication using CORRECT py-eureka-client parameters
            if self.username and self.password:
                config["eureka_basic_auth_user"] = self.username
                config["eureka_basic_auth_password"] = self.password
                logger.info(f"🔐 Using authentication with user: {self.username}")
            else:
                logger.info(f"🔓 No authentication configured - Username: {self.username}, Password: {self.password}")
            
            # Use the async init method
            await eureka_client.init_async(**config)
            
            self._is_registered = True
            logger.info(f"✅ Successfully registered {self.app_name} with Eureka")
            
        except Exception as e:
            logger.error(f"❌ Failed to register with Eureka: {e}")
            raise

    async def unregister_from_eureka(self) -> None:
        """Unregister the application from Eureka server."""
        if not self._is_registered:
            logger.info("Application is not registered with Eureka")
            return

        try:
            await eureka_client.stop_async()
            self._is_registered = False
            logger.info(f"✅ Successfully unregistered {self.app_name} from Eureka")
            
        except Exception as e:
            logger.error(f"❌ Failed to unregister from Eureka: {e}")
            # Don't re-raise during shutdown

    @property
    def is_registered(self) -> bool:
        """Check if the application is registered with Eureka."""
        return self._is_registered


# Global Eureka configuration instance
eureka_config: Optional[EurekaConfig] = None


def get_eureka_config() -> EurekaConfig:
    """Get the global Eureka configuration instance."""
    global eureka_config
    if eureka_config is None:
        logger.info("📋 Creating default Eureka config")
        eureka_config = EurekaConfig()
    return eureka_config


def init_eureka_client(port: int = 8000, username: str = None, password: str = None, enabled: bool = False) -> EurekaConfig:
    """Initialize the Eureka client with the specified port and optional credentials.
    
    Credentials can be provided via:
    1. Direct parameters: init_eureka_client(port=8000, username="dev", password="dev")
    2. Environment variables: EUREKA_USERNAME and EUREKA_PASSWORD
    """
    global eureka_config
    
    logger.info(f"🔧 Initializing Eureka client - Port: {port}")
    
    # Use environment variables as fallback
    if username is None:
        username = os.getenv('EUREKA_USERNAME')
    if password is None:
        password = os.getenv('EUREKA_PASSWORD')
    
    if username and password:
        logger.info(f"🔐 Credentials found - User: {username}")
    else:
        logger.info("🔓 No credentials provided")
    
    eureka_config = EurekaConfig(
        instance_port=port,
        username=username,
        password=password,
        enabled=enabled
    )
    return eureka_config