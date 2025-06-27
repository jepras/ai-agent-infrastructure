# AI Email-to-Deal Processor.

A GDPR-compliant AI system that monitors outgoing Outlook emails, identifies sales opportunities, and automatically creates deals in Pipedrive. Built on Railway infrastructure with unified authentication management.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and Python 3.11+
- Railway account
- Microsoft 365 Developer account (for Outlook API)
- Pipedrive account
- OpenAI or Anthropic API key

### Local Development Setup

1. **Clone and setup project structure:**
```bash
git clone <your-repo>
cd ai-agent-infrastructure
```

2. **Install dependencies:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

3. **Environment setup:**
```bash
# Copy environment files
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
```

4. **Database setup:**
```bash
# Run migrations
cd backend
alembic upgrade head
```

5. **Start development servers:**
```bash
# Backend (Terminal 1)
cd backend
uvicorn main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev
```

## 🏗️ Architecture

- **Platform**: Railway (full-stack deployment)
- **Backend**: Python FastAPI + PostgreSQL + SQLAlchemy
- **Frontend**: Next.js 13+ with NextAuth.js
- **Authentication**: Unified AuthManager (user login + service OAuth)
- **AI Integration**: User-provided OpenAI/Anthropic API keys
- **Email**: Outlook API via OAuth webhooks
- **CRM**: Pipedrive API with embedded MCP client

## 📋 Development Phases

1. **Foundation & Authentication** (Week 1-2)
2. **Service OAuth Integration** (Week 3-4)
3. **Email Processing Core** (Week 5-6)
4. **Deal Processing** (Week 7-8)
5. **Dashboard & Real-time Features** (Week 9-10)
6. **Testing & Deployment** (Week 11-12)

## 🔐 Security Features

- GDPR-compliant (process-and-discard email content)
- Encrypted credential storage
- Usage limits and cost protection
- Unified authentication management
- Real-time WebSocket updates

## 📚 Documentation

- [Project Overview](project_overview.md) - Detailed architecture and patterns
- [Technical Specification](specification_doc.md) - Complete technical requirements
- [Setup Guide](docs/setup-guide.md) - Step-by-step setup instructions
- [API Reference](docs/api-reference.md) - Backend API documentation
