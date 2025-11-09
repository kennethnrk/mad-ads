# Dummy Data for Testing

## Snowflake Query Test Examples

### 1. Basic Product Query
```sql
SELECT * FROM MVP_PRODUCTS LIMIT 5
```

### 2. Products by Category
```sql
SELECT id, name, category, price FROM MVP_PRODUCTS WHERE category = 'Gear' LIMIT 10
```

### 3. Product Count by Category
```sql
SELECT category, COUNT(*) as count FROM MVP_PRODUCTS GROUP BY category ORDER BY count DESC
```

### 4. Products with Price Range
```sql
SELECT id, name, price, category FROM MVP_PRODUCTS WHERE price::INTEGER BETWEEN 100 AND 500 ORDER BY price
```

## Snowflake Vector Search Test Examples

### 1. Gear for Wrist Pain
- **Search Text**: `wrist hurts on bench press, need support`
- **k**: `5`
- **Filter**: `{"@eq": {"category": "Gear"}}`
- **Columns**: `["id", "name", "category", "price", "image_url"]`

### 2. Low Sugar Post Workout Snack
- **Search Text**: `low sugar post workout snack high protein`
- **k**: `5`
- **Filter**: `{"@eq": {"category": "Snacks"}}`
- **Columns**: `["id", "name", "category", "price", "image_url"]`

### 3. Protein Supplements
- **Search Text**: `protein powder for muscle building`
- **k**: `10`
- **Filter**: `{"@eq": {"category": "Supplements"}}`
- **Columns**: `["id", "name", "category", "price"]`

### 4. Workout Equipment
- **Search Text**: `home gym equipment for small space`
- **k**: `5`
- **Filter**: `{"@eq": {"category": "Gear"}}`
- **Columns**: `["id", "name", "category", "price", "image_url"]`

## Match Content Test Examples

### Example 1: Fitness Content
```json
{
  "content_id": "content_fitness_001",
  "brief": "target fitness enthusiasts looking for sustainable workout gear",
  "limit": 5
}
```

### Example 2: Nutrition Content
```json
{
  "content_id": "content_nutrition_001",
  "brief": "healthy snacks for active lifestyle",
  "limit": 3
}
```

### Example 3: Workout Content
```json
{
  "content_id": "content_workout_001",
  "ad_pool_id": "pool_fitness",
  "brief": "post-workout recovery products",
  "limit": 5
}
```

## Quick Test Workflow

1. **Test Health Check** - Verify backend is running
2. **Test Snowflake Query** - Use: `SELECT * FROM MVP_PRODUCTS LIMIT 5`
3. **Test Vector Search** - Use the "gear for wrist pain" example above
4. **Test Match Content** - Use the fitness content example
5. **Test Generate Variants** - Use any content_id and ad_id
6. **Test TTS** - Use any ad script text
7. **Test Optimize** - Use default values or customize

## Expected Results

- **Snowflake Query**: Should return product data from MVP_PRODUCTS table
- **Vector Search**: Should return products with similarity scores (@scores field)
- **Match Content**: Should return matched ads with scores and reasons
- **Generate/TTS/Optimize**: Currently return mock data (stubs)

