"""Test Snowflake connection using password authentication"""

import sys
import os
import json
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.logging_config import configure_logging, get_logger
import snowflake.connector

# Configure logging
configure_logging(settings.log_level)
logger = get_logger(__name__)


def cortex_search_preview(conn, service_name: str, query: str, columns=None, filter_obj=None, limit: int = 5):
    """
    Calls SNOWFLAKE.CORTEX.SEARCH_PREVIEW on your Cortex Search service.
    Returns a list of result dicts (already parsed from JSON).
    """
    payload = {
        "query": query,
        "limit": limit
    }
    if columns:
        payload["columns"] = columns
    if filter_obj:
        payload["filter"] = filter_obj

    sql = """
    SELECT PARSE_JSON(
      SNOWFLAKE.CORTEX.SEARCH_PREVIEW(%(svc)s, %(payload)s)
    )['results']
    """
    
    cs = conn.cursor()
    try:
        cs.execute(sql, {"svc": service_name, "payload": json.dumps(payload)})
        row = cs.fetchone()
        if row and row[0]:
            # Parse JSON if it's a string, otherwise use as-is
            if isinstance(row[0], str):
                try:
                    results = json.loads(row[0])
                except json.JSONDecodeError:
                    results = row[0]
            else:
                results = row[0]
            # Ensure it's a list
            if not isinstance(results, list):
                results = [results] if results else []
        else:
            results = []
        return results
    finally:
        cs.close()


def test_snowflake_connection():
    """Test Snowflake connection with password authentication"""
    
    logger.info("testing_snowflake_connection", account=settings.snowflake_account)
    
    # Check if required config is set
    required_vars = [
        "snowflake_account",
        "snowflake_user",
        "snowflake_warehouse",
        "snowflake_database",
        "snowflake_schema",
        "snowflake_role"
    ]
    
    missing = []
    for var in required_vars:
        if not getattr(settings, var):
            missing.append(var)
    
    if missing:
        logger.error("missing_snowflake_config", missing_vars=missing)
        print(f"❌ Missing required Snowflake configuration: {', '.join(missing)}")
        print("\nPlease set these in your .env file:")
        for var in missing:
            env_var = var.upper()
            print(f"  {env_var}=<value>")
        return False
    
    # Check for password
    if not settings.snowflake_password:
        print("⚠️  Warning: SNOWFLAKE_PASSWORD not set")
        print("   Using password authentication requires SNOWFLAKE_PASSWORD in .env")
        print("   If you want to use externalbrowser, set SNOWFLAKE_AUTHENTICATOR=externalbrowser")
        return False
    
    try:
        logger.info("connecting_to_snowflake", account=settings.snowflake_account, user=settings.snowflake_user)
        
        # Connect using password authentication (matching the provided pattern)
        conn = snowflake.connector.connect(
            account=settings.snowflake_account,
            user=settings.snowflake_user,
            password=settings.snowflake_password,
            warehouse=settings.snowflake_warehouse,
            database=settings.snowflake_database,
            schema=settings.snowflake_schema,
            role=settings.snowflake_role,
        )
        
        logger.info("snowflake_connected_successfully")
        print("✅ Successfully connected to Snowflake!")
        
        # Test query
        cs = conn.cursor()
        try:
            cs.execute("SELECT CURRENT_VERSION(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
            row = cs.fetchone()
            
            print("\n📊 Connection Details:")
            print(f"   Version: {row[0]}")
            print(f"   Database: {row[1]}")
            print(f"   Schema: {row[2]}")
            print(f"   Role: {row[3]}")
            print(f"   Warehouse: {row[4]}")
            
            # Test Cortex Search if service exists
            print("\n🔍 Testing Cortex Search...")
            try:
                # Test 1: gear for wrist pain
                print("\n1) Testing: gear for wrist pain")
                res1 = cortex_search_preview(
                    conn=conn,
                    service_name=settings.snowflake_cortex_service_name,
                    query="wrist hurts on bench press, need support",
                    columns=["id", "name", "category", "price", "image_url"],
                    filter_obj={"@eq": {"category": "Gear"}},
                    limit=5
                )
                print(f"   Found {len(res1)} results")
                if res1:
                    print("   Sample result (first 3):")
                    for i, result in enumerate(res1[:3], 1):
                        print(f"   {i}. {json.dumps(result, indent=6)}")
                
                # Test 2: low sugar snack for post workout
                print("\n2) Testing: low sugar post workout snack")
                res2 = cortex_search_preview(
                    conn=conn,
                    service_name=settings.snowflake_cortex_service_name,
                    query="low sugar post workout snack high protein",
                    columns=["id", "name", "category", "price", "image_url"],
                    filter_obj={"@eq": {"category": "Snacks"}},
                    limit=5
                )
                print(f"   Found {len(res2)} results")
                if res2:
                    print("   Sample result (first 3):")
                    for i, result in enumerate(res2[:3], 1):
                        print(f"   {i}. {json.dumps(result, indent=6)}")
                
                print("\n✅ Cortex Search is working!")
                
            except Exception as e:
                logger.warning("cortex_search_test_failed", error=str(e))
                print(f"⚠️  Cortex Search test failed: {e}")
                print("   This might be expected if the service isn't set up yet")
            
            # Try to list tables
            try:
                cs.execute(f"SHOW TABLES IN SCHEMA {settings.snowflake_database}.{settings.snowflake_schema}")
                tables = cs.fetchall()
                if tables:
                    print(f"\n📋 Tables in schema '{settings.snowflake_schema}': {len(tables)}")
                    print("   Available tables:")
                    for table in tables[:10]:  # Show first 10
                        print(f"     - {table[1]}")
                    if len(tables) > 10:
                        print(f"     ... and {len(tables) - 10} more")
            except Exception as e:
                logger.warning("could_not_list_tables", error=str(e))
                print(f"\n⚠️  Could not list tables: {e}")
            
        finally:
            cs.close()
        
        conn.close()
        logger.info("snowflake_connection_closed")
        print("\n✅ Connection test completed successfully!")
        return True
        
    except snowflake.connector.errors.ProgrammingError as e:
        logger.error("snowflake_programming_error", error=str(e), error_code=e.errno)
        print(f"❌ Snowflake Programming Error: {e}")
        print(f"   Error Code: {e.errno}")
        return False
    except snowflake.connector.errors.OperationalError as e:
        logger.error("snowflake_operational_error", error=str(e), error_code=e.errno)
        print(f"❌ Snowflake Operational Error: {e}")
        print(f"   Error Code: {e.errno}")
        print("\n💡 Common issues:")
        print("   - Check your account identifier format")
        print("   - Verify network connectivity")
        print("   - Check username and password")
        return False
    except Exception as e:
        logger.error("snowflake_connection_error", error=str(e), error_type=type(e).__name__)
        print(f"❌ Connection Error: {e}")
        print(f"   Error Type: {type(e).__name__}")
        return False


if __name__ == "__main__":
    print("🔍 Testing Snowflake Connection (Password Authentication)...\n")
    success = test_snowflake_connection()
    sys.exit(0 if success else 1)
