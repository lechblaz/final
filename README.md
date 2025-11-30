# Personal Finance Manager

A full-stack containerized personal finance management system with intelligent transaction tagging, merchant normalization, and visual analytics.

## Features

- **Dashboard**: Visual overview with Sankey diagram showing money flow from income sources to expense categories
- **CSV Import**: Import mBank bank statements (Polish format) with duplicate detection
- **Merchant Normalization**: Automatic extraction and normalization of merchant names and store locations
- **Smart Auto-Tagging**: Intelligent transaction categorization based on merchants, amounts, operation types, and keywords
- **Manual Tag Management**: Create, edit, and apply custom tags to transactions
- **Advanced Filtering**: Filter transactions by date range and multiple tags (AND logic)
- **Transaction Management**: View, search, and manage financial transactions with pagination
- **Analytics**: Spending insights with visual diagrams and top expense categories

## Screenshots & Features

### Dashboard
- Summary cards: Total transactions, income, expenses, balance
- Sankey diagram visualizing money flow through categories
- Top 5 expense categories with color-coded rankings

### Transactions Page
- Tag display as colored badges
- Tag filtering with transaction counts
- Inline tag editing modal
- Merchant and store information display

### Tags Page
- Create custom tags with colors and descriptions
- View all tags with usage statistics
- Sorted by transaction count

### Merchants Page
- Normalized merchant names with store counts
- Transaction totals and spending by merchant
- Automatic merchant discovery from transaction titles

## Implementation Status

- ✅ **Phase 1**: CSV import + transaction viewing (COMPLETE)
- ✅ **Phase 2**: Merchant normalization (COMPLETE)
- ✅ **Phase 3**: Auto-tagging + manual tag management (COMPLETE)
- ✅ **Dashboard**: Sankey diagram with financial flow visualization (COMPLETE)

## Tech Stack

- **Backend**: Python 3.11 + FastAPI + SQLAlchemy
- **Frontend**: React 18 + TypeScript + Vite + TanStack Query
- **Database**: PostgreSQL 16
- **Visualization**: Recharts (Sankey diagrams)
- **Containers**: Docker + Docker Compose

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/lechblaz/final.git
cd final

# Start all services (builds images on first run)
docker compose up -d

# Check logs
docker compose logs -f

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs (Swagger): http://localhost:8000/docs
```

### First Time Setup

1. **Verify services are running:**
```bash
docker compose ps
```

All three services (db, backend, frontend) should show as "Up"

2. **Check database initialization:**
```bash
docker compose exec db psql -U finance_user -d finance_db -c "\dt"
```

You should see all tables (users, transactions, tags, merchants, stores, etc.)

3. **Open the frontend:**
Navigate to http://localhost:5173 in your browser - you'll see the Dashboard

### Importing Your First CSV

1. Go to http://localhost:5173/import
2. Click "Choose File" and select your mBank CSV export
3. Click "Upload & Import"
4. View imported transactions at http://localhost:5173/transactions

**Note:** Place your CSV files in the `data/` directory (excluded from git)

## Project Structure

```
final/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/      # API endpoints
│   │   │   ├── dashboard.py    # Dashboard statistics
│   │   │   ├── imports.py      # CSV import
│   │   │   ├── merchants.py    # Merchant management
│   │   │   ├── tags.py         # Tag management
│   │   │   └── transactions.py # Transaction CRUD
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   │   ├── auto_tagger.py       # Auto-tagging engine
│   │   │   ├── csv_processor.py     # CSV parsing
│   │   │   └── merchant_extractor.py # Merchant normalization
│   │   └── config.py    # Configuration
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # React frontend
│   ├── src/
│   │   ├── api/         # API clients
│   │   │   ├── dashboard.ts
│   │   │   ├── merchants.ts
│   │   │   ├── tags.ts
│   │   │   └── transactions.ts
│   │   ├── pages/       # React pages
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ImportPage.tsx
│   │   │   ├── MerchantsPage.tsx
│   │   │   ├── TagsPage.tsx
│   │   │   └── TransactionsPage.tsx
│   │   ├── types/       # TypeScript types
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── database/             # SQL schemas
│   └── init.sql         # Database schema
├── data/                 # CSV files (gitignored)
├── docker-compose.yml    # Development setup
└── README.md
```

## API Endpoints

### Dashboard
- `GET /api/v1/dashboard/summary` - Dashboard statistics (income, expenses, balance, top categories)
- `GET /api/v1/dashboard/sankey` - Sankey diagram data (nodes and links for money flow)

### Imports
- `POST /api/v1/imports/upload` - Upload CSV file
- `GET /api/v1/imports` - List import batches
- `GET /api/v1/imports/{id}` - Get import details

### Transactions
- `GET /api/v1/transactions` - List transactions (with date and tag filters)
- `GET /api/v1/transactions/{id}` - Get single transaction
- `PATCH /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Soft delete transaction

### Tags
- `GET /api/v1/tags` - List all tags with usage statistics
- `POST /api/v1/tags` - Create new tag
- `GET /api/v1/tags/{id}` - Get tag details
- `PATCH /api/v1/tags/{id}` - Update tag
- `DELETE /api/v1/tags/{id}` - Delete tag
- `POST /api/v1/tags/apply` - Apply tags to transaction
- `GET /api/v1/tags/suggest/{transaction_id}` - Get tag suggestions
- `POST /api/v1/tags/auto-tag-all` - Auto-tag all untagged transactions

### Merchants
- `GET /api/v1/merchants` - List merchants with statistics
- `GET /api/v1/merchants/discover` - Discover new merchants from transactions
- `GET /api/v1/merchants/{id}/stores` - List stores for merchant
- `POST /api/v1/merchants/{id}/stores` - Create store

### Health
- `GET /` - API info
- `GET /health` - Health check

**Full API documentation:** http://localhost:8000/docs

## Auto-Tagging System

The auto-tagger intelligently categorizes transactions based on:

### Merchant-Based Tags
- **Żabka, Carrefour, Biedronka**: `grocery`, `convenience-store`, `shopping`
- **Uber, Bolt**: `transport`, `taxi`
- **Starbucks, Costa Coffee**: `food`, `coffee`, `dining`
- **McDonald's, KFC**: `food`, `fast-food`, `dining`
- **Netflix, Spotify**: `entertainment`, `subscription`
- **Parking lots**: `transport`, `parking`
- **Hotels, Airbnb**: `travel`, `accommodation`

### Operation Type Tags
- Card payments: `card-payment`
- BLIK payments: `blik`, `mobile-payment`
- Transfers: `transfer`
- ATM withdrawals: `atm`, `cash-withdrawal`

### Amount-Based Tags
- Income (amount > 0): `income`
- Expenses (amount < 0): `expense`
- Small purchases (< 20 PLN): `small-purchase`
- Major expenses (> 500 PLN): `major-expense`

### Location Tags
- Warsaw: `warsaw`

### Keyword Detection
Searches transaction titles for keywords like:
- `parking`, `fuel`, `medicine`, `pharmacy`, `gym`, `fitness`, etc.

## CSV Format Support

Currently supports **mBank** CSV exports with:
- **Encoding**: Windows-1250 (Polish characters)
- **Delimiter**: Semicolon (`;`)
- **Structure**: Multi-section file with metadata, summary, and transactions
- **Date formats**: `YYYY-MM-DD` or `DD.MM.YYYY`
- **Amount format**: Comma decimal separator (`16,43 PLN`)

## Development

### Stop Services
```bash
docker compose down
```

### Rebuild After Code Changes
```bash
# Rebuild specific service
docker compose up -d --build backend

# Or rebuild all
docker compose up -d --build
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

### Access Database
```bash
# PostgreSQL CLI
docker compose exec db psql -U finance_user -d finance_db

# Example queries
SELECT COUNT(*) FROM transactions;
SELECT * FROM tags ORDER BY usage_count DESC LIMIT 10;
SELECT name, display_name, transaction_count FROM tags;
```

### Install Frontend Dependencies
```bash
# Install new npm packages
docker compose exec frontend npm install <package-name>
```

## Troubleshooting

### Services won't start
```bash
# Check if ports are already in use
lsof -i :5173  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Clean up and restart
docker compose down -v
docker compose up -d --build
```

### Database errors
```bash
# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d
```

### CSV import fails
- Ensure file is mBank format CSV
- Check file encoding is Windows-1250
- Verify file size is under 10MB
- Check backend logs: `docker compose logs backend`

### Frontend not updating
```bash
# Clear Vite cache and rebuild
docker compose exec frontend rm -rf node_modules/.vite
docker compose restart frontend
```

## Data Privacy

**Important:** This repository does NOT include:
- Transaction CSV files (excluded via `.gitignore`)
- Database contents (excluded via `.gitignore`)
- Environment variables with secrets (`.env`)

Your financial data stays local on your machine.

## License

MIT

## Acknowledgments

Built with Claude Code (Anthropic)
