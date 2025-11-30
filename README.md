# Personal Finance Manager

A containerized personal finance management system with intelligent transaction tagging and analytics.

## Features

- **CSV Import**: Import mBank bank statements (Polish format)
- **Flat Tag System**: Flexible, non-hierarchical transaction tagging
- **Auto-Tagging**: Intelligent tag suggestions using merchant patterns and NLP
- **Tag Synonyms**: Automatic detection of duplicate tags (e.g., "pet" vs "pets")
- **Analytics**: Spending insights by tags and tag combinations
- **Multi-User Ready**: Schema designed for future multi-user support

## Tech Stack

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: React 18 + TypeScript + Vite
- **Database**: PostgreSQL 16
- **NLP**: spaCy (Polish language model)
- **Containers**: Docker + Docker Compose

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Git

### Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd final

# Start all services
docker-compose up

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Project Structure

```
finance-manager/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── database/         # SQL schemas and seeds
├── scripts/          # Utility scripts
└── docs/            # Documentation
```

## Development

See the [implementation plan](/.claude/plans/mighty-dreaming-harp.md) for detailed development phases.

## License

MIT
