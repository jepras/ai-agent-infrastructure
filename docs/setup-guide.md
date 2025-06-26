# Setup Guide - AI Email Processor

This guide will walk you through setting up the AI Email Processor project for development and production deployment.

## Prerequisites

Before starting, ensure you have:

- **Node.js 18+** and **npm**
- **Python 3.11+** and **pip**
- **Git** for version control
- **Railway account** for deployment
- **Microsoft 365 Developer account** (for Outlook API)
- **Pipedrive account** (for CRM integration)
- **OpenAI or Anthropic API key** (for AI processing)

## Quick Start (Automated Setup)

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd ai-agent-infrastructure
```

2. **Run the automated setup script:**
```bash
python3 scripts/setup_dev.py
```

3. **Follow the manual steps below for OAuth configuration**

## Manual Setup Steps

### 1. Railway Project Setup

**In Railway Dashboard:**
1. Go to [Railway.app](https://railway.app) and create a new project
2. Add a PostgreSQL database service
3. Note the `DATABASE_URL` - you'll need this for your `.env` file
4. Set up a custom domain (optional but recommended)

**Environment Variables to Add:**
```bash
DATABASE_URL=postgresql://... # Railway auto-provides
NEXTAUTH_URL=https://your-app.railway.app
NEXTAUTH_SECRET=your-generated-secret
CREDENTIAL_ENCRYPTION_KEY=your-32-char-key
JWT_SECRET=your-jwt-secret
```

### 2. Microsoft 365 Developer Setup

**In Microsoft 365 Developer Portal:**
1. Go to [Microsoft 365 Developer Portal](https://developer.microsoft.com/en-us/microsoft-365)
2. Create a new app registration
3. Add redirect URI: `https://your-app.railway.app/api/auth/callback/outlook`
4. Note the Client ID and Client Secret
5. Add required permissions:
   - `Mail.Read`
   - `Mail.Send`
   - `User.Read`

**Add to your `.env`:**
```bash
OUTLOOK_CLIENT_ID=your-outlook-client-id
OUTLOOK_CLIENT_SECRET=your-outlook-client-secret
```

### 3. Pipedrive App Setup

**In Pipedrive Developer Portal:**
1. Go to [Pipedrive Developer Portal](https://developers.pipedrive.com/)
2. Create a new app
3. Add redirect URI: `https://your-app.railway.app/api/auth/callback/pipedrive`
4. Note the Client ID and Client Secret
5. Add required scopes:
   - `deals:read`
   - `deals:write`
   - `persons:read`
   - `organizations:read`

**Add to your `.env`:**
```bash
PIPEDRIVE_CLIENT_ID=your-pipedrive-client-id
PIPEDRIVE_CLIENT_SECRET=your-pipedrive-client-secret
```

### 4. Local Development Setup

**Backend Setup:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env with your credentials

# Run database migrations
cd backend
alembic upgrade head

# Start backend server
uvicorn main:app --reload --port 8000
```

**Frontend Setup:**
```bash
# Install dependencies
cd frontend
npm install

# Set up environment
cp .env.local.example .env.local
# Edit .env.local with your API URL

# Start frontend server
npm run dev
```

### 5. Database Schema Setup

The project uses Alembic for database migrations. The initial schema includes:

- **Users table** (NextAuth.js compatible)
- **Accounts and Sessions** (NextAuth.js required)
- **User Credentials** (encrypted OAuth tokens)
- **Email Analysis Logs** (GDPR-compliant metadata)
- **Deals Created** (tracking created deals)
- **Usage Tracking** (billing protection)

**Run migrations:**
```bash
cd backend
alembic upgrade head
```

### 6. Testing the Setup

**Backend Health Check:**
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", "service": "ai-email-processor"}
```

**Frontend Access:**
- Open http://localhost:3000
- You should see the landing page

**API Documentation:**
- Open http://localhost:8000/docs
- FastAPI automatic documentation

## Development Workflow

### 1. Backend Development

**Project Structure:**
```
backend/
├── main.py              # FastAPI app entry point
├── config.py            # Application configuration
├── app/
│   ├── auth/           # Authentication & OAuth
│   ├── api/            # API endpoints
│   ├── services/       # Business logic
│   ├── models/         # Database models
│   ├── core/           # Core utilities
│   └── utils/          # Helper functions
└── migrations/         # Database migrations
```

**Key Development Patterns:**
- Always use the unified `AuthManager` for authentication
- Follow GDPR compliance (process-and-discard email content)
- Implement usage limits before AI processing
- Use encrypted storage for all credentials

### 2. Frontend Development

**Project Structure:**
```
frontend/
├── src/
│   ├── app/            # Next.js 13+ app directory
│   ├── components/     # Reusable UI components
│   ├── lib/            # Utilities and configurations
│   └── styles/         # Global styles
├── public/             # Static assets
└── package.json        # Dependencies
```

**Key Development Patterns:**
- Use NextAuth.js for authentication
- Implement real-time updates with WebSocket
- Follow responsive design principles
- Use TypeScript for type safety

### 3. Database Development

**Creating New Migrations:**
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

**Database Models Pattern:**
```python
# Always include audit fields
class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Deployment

### Railway Deployment

**Automatic Deployment:**
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Python/Node.js setup
3. Set environment variables in Railway dashboard
4. Deploy with `git push`

**Manual Deployment:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

### Environment Variables for Production

**Required Variables:**
```bash
DATABASE_URL=postgresql://... # Railway auto-provides
NEXTAUTH_URL=https://your-app.railway.app
NEXTAUTH_SECRET=your-secure-secret
CREDENTIAL_ENCRYPTION_KEY=your-32-char-key
JWT_SECRET=your-jwt-secret
OUTLOOK_CLIENT_ID=your-outlook-client-id
OUTLOOK_CLIENT_SECRET=your-outlook-client-secret
PIPEDRIVE_CLIENT_ID=your-pipedrive-client-id
PIPEDRIVE_CLIENT_SECRET=your-pipedrive-client-secret
BASE_URL=https://your-app.railway.app
ENVIRONMENT=production
```

## Troubleshooting

### Common Issues

**1. Database Connection Errors:**
- Verify `DATABASE_URL` is correct
- Ensure PostgreSQL service is running in Railway
- Check if migrations have been applied

**2. OAuth Authentication Issues:**
- Verify redirect URIs match exactly
- Check client IDs and secrets
- Ensure required permissions are granted

**3. Frontend Build Errors:**
- Clear Next.js cache: `rm -rf .next`
- Reinstall dependencies: `npm install`
- Check TypeScript errors: `npm run type-check`

**4. AI Processing Errors:**
- Verify API keys are valid
- Check usage limits and billing
- Ensure email content is being processed correctly

### Getting Help

- Check the [API Documentation](http://localhost:8000/docs) for endpoint details
- Review the [Project Overview](project_overview.md) for architecture details
- See the [Technical Specification](specification_doc.md) for complete requirements
- Open an issue in the repository for bugs or feature requests

## Next Steps

After completing the setup:

1. **Implement the AuthManager** - Start with unified authentication
2. **Build OAuth flows** - Connect Outlook and Pipedrive
3. **Create email processing** - Implement the core AI analysis
4. **Add real-time features** - WebSocket updates for dashboard
5. **Deploy to production** - Railway deployment with monitoring

The project is designed to be built incrementally, with each phase building on the previous one. Follow the development phases outlined in the specification document for the best approach. 