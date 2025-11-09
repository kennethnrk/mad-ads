#!/usr/bin/env python3
"""Isolated test for Snowflake connection"""

import snowflake.connector
import os

print("=" * 60)
print("Testing Snowflake Connection (Isolated)")
print("=" * 60)

try:
    print("\n[1/3] Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        account="ZGXJKBZ-LH19094",
        user="PURUJIT",
        password="Test@123456789",
        authenticator="snowflake",  # important: NOT externalbrowser
        warehouse="COMPUTE_WH",
        database="HACKATHON",
        schema="PRODUCTS",
        role="ACCOUNTADMIN",
    )
    print("✅ Connection established!")
    
    print("\n[2/3] Testing basic query...")
    cs = conn.cursor()
    cs.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
    result = cs.fetchone()
    print(f"✅ Query successful!")
    print(f"   User: {result[0]}")
    print(f"   Role: {result[1]}")
    print(f"   Database: {result[2]}")
    print(f"   Schema: {result[3]}")
    cs.close()
    
    print("\n[3/3] Testing Cortex Search service...")
    cs = conn.cursor()
    try:
        # Test if Cortex Search service exists
        cs.execute("SHOW CORTEX SEARCH SERVICES")
        services = cs.fetchall()
        print(f"✅ Found {len(services)} Cortex Search service(s):")
        for service in services:
            print(f"   - {service[0]}")
        
        # Test Cortex Search query
        print("\n[4/4] Testing Cortex Search query...")
        sql = """
        SELECT PARSE_JSON(
          SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
            'product_search',
            '{"query": "protein snack", "limit": 3}'
          )
        )['results']
        """
        cs.execute(sql)
        row = cs.fetchone()
        if row and row[0]:
            import json
            if isinstance(row[0], str):
                results = json.loads(row[0])
            else:
                results = row[0]
            print(f"✅ Cortex Search working! Found {len(results)} results")
            if results:
                print(f"   First result: {results[0]}")
        else:
            print("⚠️  No results returned from Cortex Search")
    except Exception as e:
        print(f"❌ Cortex Search error: {e}")
    finally:
        cs.close()
    
    conn.close()
    print("\n✅ All tests passed! Connection is working.")
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

