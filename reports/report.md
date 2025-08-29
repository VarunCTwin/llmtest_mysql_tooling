# LLM Test Report

Generated: 2025-08-29 16:10:11

## Database: test_db

✅ **activationDate filter** → Only include clients with activationDate >= 2025-01-01

- Runner: sql
- Message: Validated inclusion rule on 2 rows (define stricter rule if needed).

✅ **pending disenrollment visibility** → Only active members should appear in search results

- Runner: sql
- Message: Found 2 active members (excluding pending disenrollment)

✅ **user authentication** → Only recently active users should be able to authenticate

- Runner: sql
- Message: Found 2 recently active users (within 30 days)

✅ **search performance optimization** → Search index should be updated daily

- Runner: sql
- Message: Search index has 2 records updated today

✅ **user authentication** → Only recently active users should be able to authenticate

- Runner: sql
- Message: Found 2 recently active users (within 30 days)

