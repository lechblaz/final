# Personal Finance Manager

A containerized personal finance management system with intelligent transaction tagging and analytics.

## Features

- **CSV Import**: Import mBank bank statements (Polish format)
- **Transaction Management**: View, filter, and manage financial transactions
- **Flat Tag System**: Flexible, non-hierarchical transaction tagging (Phase 3)
- **Auto-Tagging**: Intelligent tag suggestions using merchant patterns and NLP (Phase 4-5)
- **Tag Synonyms**: Automatic detection of duplicate tags (e.g., "pet" vs "pets") (Phase 5)
- **Analytics**: Spending insights by tags and tag combinations (Phase 6)
- **Multi-User Ready**: Schema designed for future multi-user support

## Current Status: Phase 1 Complete ✅

**What's implemented:**
- ✅ CSV import for mBank statements (Polish format)
- ✅ Duplicate detection (file and transaction level)
- ✅ Transaction viewing with pagination
- ✅ Date range filtering
- ✅ Database schema with flat tag system
- ✅ Docker containerized setup

**Coming next:** Phase 2 - Merchant normalization

## Tech Stack

- **Backend**: Python 3.11 + FastAPI + SQLAlchemy
- **Frontend**: React 18 + TypeScript + Vite + TanStack Query
- **Database**: PostgreSQL 16
- **NLP**: spaCy (Polish language model) - for Phase 5
- **Containers**: Docker + Docker Compose

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Git

### Quick Start

```bash
# Navigate to project directory
cd ~/src/local/final

# Start all services (this will build images on first run)
docker-compose up -d

# Check logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs (Swagger): http://localhost:8000/docs
# API Docs (ReDoc): http://localhost:8000/redoc
```

### First Time Setup

1. **Verify services are running:**
```bash
docker-compose ps
```

All three services (db, backend, frontend) should show as "Up"

2. **Check database initialization:**
```bash
docker-compose exec db psql -U finance_user -d finance_db -c "\dt"
```

You should see all tables (users, transactions, tags, merchants, etc.)

3. **Open the frontend:**
Navigate to http://localhost:5173 in your browser

### Importing Your First CSV

1. Go to http://localhost:5173/import
2. Click "Choose File" and select your mBank CSV export
3. Click "Upload & Import"
4. You'll be redirected to the transactions page automatically

**Sample CSV location:** `data/31593830_250801_251031.csv`

## Project Structure

```
finance-manager/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/      # API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── core/        # Utilities
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # React frontend
│   ├── src/
│   │   ├── api/         # API clients
│   │   ├── pages/       # React pages
│   │   ├── types/       # TypeScript types
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── database/             # SQL schemas
│   ├── init.sql         # Database schema
│   └── seed/            # Seed data (future)
├── data/                 # Sample CSV files
├── docker-compose.yml    # Development setup
└── README.md
```

## API Endpoints

### Imports
- `POST /api/v1/imports/upload` - Upload CSV file
- `GET /api/v1/imports` - List import batches
- `GET /api/v1/imports/{id}` - Get import details

### Transactions
- `GET /api/v1/transactions` - List transactions (with filters)
- `GET /api/v1/transactions/{id}` - Get single transaction
- `PATCH /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Soft delete transaction

### Health
- `GET /` - API info
- `GET /health` - Health check

**Full API documentation:** http://localhost:8000/docs

## Development

### Stop Services
```bash
docker-compose down
```

### Rebuild After Code Changes
```bash
# Rebuild specific service
docker-compose up -d --build backend

# Or rebuild all
docker-compose up -d --build
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Access Database
```bash
# PostgreSQL CLI
docker-compose exec db psql -U finance_user -d finance_db

# Example queries
SELECT COUNT(*) FROM transactions;
SELECT * FROM import_batches ORDER BY created_at DESC LIMIT 5;
```

### Run Backend Tests (when implemented)
```bash
docker-compose exec backend pytest
```

## CSV Format Support

Currently supports **mBank** CSV exports with the following characteristics:
- **Encoding**: Windows-1250 (Polish characters)
- **Delimiter**: Semicolon (`;`)
- **Structure**: Multi-section file with metadata, summary, and transactions
- **Date formats**: `YYYY-MM-DD` or `DD.MM.YYYY`
- **Amount format**: Comma decimal separator (`16,43 PLN`)

## Troubleshooting

### Services won't start
```bash
# Check if ports are already in use
lsof -i :5173  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Clean up and restart
docker-compose down -v
docker-compose up -d --build
```

### Database errors
```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### CSV import fails
- Ensure file is mBank format CSV
- Check file encoding is Windows-1250
- Verify file size is under 10MB
- Check backend logs: `docker-compose logs backend`

## Implementation Phases

- ✅ **Phase 1**: CSV import + transaction viewing (COMPLETE)
- 🔄 **Phase 2**: Merchant normalization (Next)
- ⏳ **Phase 3**: Manual tagging system
- ⏳ **Phase 4**: Auto-tagging
- ⏳ **Phase 5**: NLP tag synonym detection
- ⏳ **Phase 6**: Analytics & insights

See the detailed [implementation plan](/.claude/plans/mighty-dreaming-harp.md).

## Git History

Regular commits track implementation progress:
```bash
git log --oneline
```

Each commit represents a logical development step.

## Contributing

This is a personal project. For suggestions or issues, please create a GitHub issue.

## License

MIT
