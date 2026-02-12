# Seed Data Directory

This directory contains seed data for development and testing purposes.

## Files

- `seed_companies.json`: 100 sample companies with complete data
- `seed_users.json`: 50 sample users with authentication data
- `seed_partnerships.json`: 30 sample partnerships with compatibility scores

## Usage

To load seed data into the database:

```bash
# For auth-service
docker compose exec auth-service python -m scripts.seed_data --users 50

# For company-service  
docker compose exec company-service python -m scripts.seed_data --companies 100

# For partner-service
docker compose exec partner-service python -m scripts.seed_data --partnerships 30
```

Note: The seed_data.py script is located in `/platform/scripts/`.