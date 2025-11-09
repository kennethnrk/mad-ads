# Snowflake Connection Setup

## Environment Variables Updated

The following Snowflake credentials have been configured:

```env
SNOWFLAKE_ACCOUNT=ZGXJKBZ-LH19094
SNOWFLAKE_USER=PURUJIT
SNOWFLAKE_AUTHENTICATOR=externalbrowser
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HACKATHON
SNOWFLAKE_SCHEMA=PRODUCTS
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_CORTEX_SERVICE_NAME=product_search
```

## Connection Test Results

The connection test encountered authentication issues. This is expected with `externalbrowser` authenticator as it requires:

1. **Browser-based authentication**: The `externalbrowser` authenticator opens a browser window for SSO/login
2. **Account format**: May need adjustment based on your Snowflake account setup

## Troubleshooting

### Error: "SAML Identity Provider account parameter"

This error typically means:
- The account identifier format may need adjustment
- The authenticator method might need to be changed
- Browser authentication may be required

### Solutions to Try

1. **Use password authentication instead** (if available):
   ```env
   SNOWFLAKE_AUTHENTICATOR=
   SNOWFLAKE_PASSWORD=<your_password>
   ```

2. **Try different account formats**:
   - Full: `ZGXJKBZ-LH19094`
   - Account only: `ZGXJKBZ`
   - Account.locator: `ZGXJKBZ.LH19094`

3. **Use Snowpark instead** (as your teammate is using):
   ```python
   from snowflake.snowpark import Session
   
   session = Session.builder.configs({
       "account": "ZGXJKBZ-LH19094",
       "user": "PURUJIT",
       "authenticator": "externalbrowser",
       "role": "ACCOUNTADMIN",
       "warehouse": "COMPUTE_WH",
       "database": "HACKATHON",
       "schema": "PRODUCTS",
   }).create()
   ```

## Testing the Connection

Run the test script:
```bash
source venv/bin/activate
python test_snowflake_connection.py
```

## Next Steps

1. **If using externalbrowser**: Ensure you can authenticate via browser when the script runs
2. **If using password**: Add `SNOWFLAKE_PASSWORD` to `.env` file
3. **Consider Snowpark**: Install `snowflake-snowpark-python` if you prefer that approach

## Integration with MCP Tools

Once connection is working, update `app/mcp/tools.py`:
- `snowflake_query()` - Use real Snowflake connection
- `snowflake_vector_search()` - Use Cortex Search API

The connection logic is ready in `app/config.py` - just need to verify authentication method works.

