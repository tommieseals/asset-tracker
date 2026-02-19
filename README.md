# Asset Inventory Tracker

A production-ready internal portal for tracking company assets with AI-powered natural language search, role-based access control, and full audit logging.

![CI](https://github.com/tommieseals/asset-tracker/workflows/CI/badge.svg)

## Features

- **📦 Asset Management**: Track laptops, monitors, software licenses, keys, and more
- **👥 User Management**: Role-based access (Admin, User, Auditor)
- **🔄 Check-in/Check-out**: Full workflow with history tracking
- **🔍 AI-Powered Search**: Natural language queries ("show me all laptops assigned to engineering")
- **📊 Audit Logging**: Complete history of who changed what, when
- **📱 QR Code Generation**: Scan to quickly look up assets
- **📤 Export**: CSV/Excel export for reporting
- **🔐 JWT Authentication**: Secure API with refresh tokens

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy 2.0** - Async ORM with SQLite/PostgreSQL
- **Pydantic** - Data validation
- **JWT** - Authentication with python-jose
- **Alembic** - Database migrations

### Frontend
- **Next.js 14** - React framework with App Router
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **TanStack Query** - Data fetching

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/tommieseals/asset-tracker.git
cd asset-tracker

# Start services
docker-compose up -d

# Access the app
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/login` | Login and get JWT token |
| GET | `/api/assets/` | List all assets |
| POST | `/api/assets/` | Create new asset |
| POST | `/api/assets/{id}/checkout` | Check out asset to user |
| POST | `/api/assets/{id}/checkin` | Check in asset |
| POST | `/api/search/ai` | AI-powered search |
| GET | `/api/qr/{asset_id}` | Generate QR code |
| GET | `/api/audit/` | View audit logs |

## Default Credentials

After seeding the database:

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | password123 |
| User | jsmith | password123 |
| Auditor | auditor | password123 |

⚠️ **Change these in production!**

## AI Search Examples

The AI search understands natural language queries:

- "show me all laptops assigned to engineering"
- "available monitors"
- "what does John Smith have?"
- "Dell laptops in maintenance"
- "unassigned headsets"

## Project Structure

```
asset-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # JWT authentication
│   │   ├── database.py      # Database configuration
│   │   ├── config.py        # Settings
│   │   └── routers/
│   │       ├── assets.py    # Asset CRUD + checkout
│   │       ├── users.py     # User management
│   │       ├── audit.py     # Audit log access
│   │       ├── search.py    # AI-powered search
│   │       └── qr.py        # QR code generation
│   ├── alembic/             # Database migrations
│   ├── tests/               # Pytest tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   └── lib/             # Utilities
│   └── package.json
├── seed/
│   └── sample_data.sql      # Sample data
├── docs/
│   ├── api.md               # API documentation
│   └── deployment.md        # Deployment guide
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./assets.db` |
| `SECRET_KEY` | JWT signing key | (required in production) |
| `AI_API_URL` | OpenAI-compatible API URL | `http://localhost:11434/v1` |
| `AI_MODEL` | AI model for search | `qwen2.5:3b` |

## Deployment

See [docs/deployment.md](docs/deployment.md) for production deployment guides:
- Docker Compose
- Kubernetes
- Cloud Run / App Engine

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest backend/tests/`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.
