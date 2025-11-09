"""Snowflake connection management"""

import snowflake.connector
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def get_snowflake_connection():
    """Get a Snowflake connection using settings"""
    conn_params = {
        "account": settings.snowflake_account,
        "user": settings.snowflake_user,
        "warehouse": settings.snowflake_warehouse,
        "database": settings.snowflake_database,
        "schema": settings.snowflake_schema,
        "role": settings.snowflake_role,
    }
    
    # Add authentication method - prefer password with snowflake authenticator
    if settings.snowflake_password:
        conn_params["password"] = settings.snowflake_password
        # Use specified authenticator or default to "snowflake" for password auth
        if settings.snowflake_authenticator:
            conn_params["authenticator"] = settings.snowflake_authenticator
        else:
            conn_params["authenticator"] = "snowflake"
    elif settings.snowflake_authenticator:
        conn_params["authenticator"] = settings.snowflake_authenticator
    else:
        raise ValueError("No authentication method configured (password or authenticator required)")
    
    return snowflake.connector.connect(**conn_params)

