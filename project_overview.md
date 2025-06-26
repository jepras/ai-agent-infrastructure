# AI Development Rules for Railway Email Processor

## Project Context & Architecture

You are building an AI-powered email processor that automatically creates Pipedrive deals from Outlook emails. The system uses:

- **Platform**: Railway (full-stack deployment)
- **Backend**: Python FastAPI + PostgreSQL + SQLAlchemy
- **Frontend**: Next.js 13+ with NextAuth.js integration
- **Authentication**: Unified AuthManager (user login + service OAuth tokens)
- **AI Integration**: User-provided OpenAI/Anthropic API keys with usage limits
- **Email**: Outlook API via OAuth webhooks
- **CRM**: Pipedrive API with embedded MCP client
- **Privacy**: GDPR-compliant (process-and-discard email content)
- **Real-time**: WebSocket updates for dashboard

ai-email-processor/
├── README.md
├── .gitignore
├── .env.example
├── railway.toml                    # Railway deployment config
├── requirements.txt                # Python dependencies
├── package.json                   # Node.js dependencies (for frontend)
├── Dockerfile                     # Railway deployment
├── alembic.ini                    # Database migrations config
├── frontend/                      # Next.js application
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── .env.local.example
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── logo.svg
│   │   └── manifest.json
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── globals.css
│   │   │   ├── api/
│   │   │   │   └── auth/
│   │   │   │       └── [...nextauth]/
│   │   │   │           └── route.ts
│   │   │   ├── auth/
│   │   │   │   ├── signin/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── signup/
│   │   │   │       └── page.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── emails/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── deals/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── usage/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── settings/
│   │   │   │       └── page.tsx
│   │   │   └── setup/
│   │   │       ├── page.tsx
│   │   │       ├── outlook/
│   │   │       │   └── page.tsx
│   │   │       ├── pipedrive/
│   │   │       │   └── page.tsx
│   │   │       └── ai-config/
│   │   │           └── page.tsx
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── alert.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   ├── loading.tsx
│   │   │   │   └── progress.tsx
│   │   │   ├── auth/
│   │   │   │   ├── signin-form.tsx
│   │   │   │   ├── signup-form.tsx
│   │   │   │   └── auth-guard.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── email-log-table.tsx
│   │   │   │   ├── deals-list.tsx
│   │   │   │   ├── usage-chart.tsx
│   │   │   │   ├── real-time-status.tsx
│   │   │   │   ├── stats-cards.tsx
│   │   │   │   └── activity-feed.tsx
│   │   │   ├── setup/
│   │   │   │   ├── oauth-connector.tsx
│   │   │   │   ├── api-key-form.tsx
│   │   │   │   ├── usage-limits-form.tsx
│   │   │   │   ├── setup-wizard.tsx
│   │   │   │   └── service-status.tsx
│   │   │   └── layout/
│   │   │       ├── header.tsx
│   │   │       ├── sidebar.tsx
│   │   │       ├── footer.tsx
│   │   │       └── navigation.tsx
│   │   ├── lib/
│   │   │   ├── auth/
│   │   │   │   ├── config.ts
│   │   │   │   ├── options.ts
│   │   │   │   └── adapter.ts
│   │   │   ├── api/
│   │   │   │   ├── client.ts
│   │   │   │   ├── auth.ts
│   │   │   │   ├── dashboard.ts
│   │   │   │   └── setup.ts
│   │   │   ├── hooks/
│   │   │   │   ├── use-auth.ts
│   │   │   │   ├── use-websocket.ts
│   │   │   │   ├── use-email-logs.ts
│   │   │   │   ├── use-deals.ts
│   │   │   │   └── use-usage-stats.ts
│   │   │   ├── types/
│   │   │   │   ├── auth.ts
│   │   │   │   ├── api.ts
│   │   │   │   ├── dashboard.ts
│   │   │   │   └── database.ts
│   │   │   └── utils/
│   │   │       ├── formatting.ts
│   │   │       ├── validation.ts
│   │   │       ├── constants.ts
│   │   │       └── websocket.ts
│   │   └── styles/
│   │       └── globals.css
├── backend/                       # Python FastAPI application
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Application configuration
│   ├── dependencies.py            # FastAPI dependencies
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py         # Unified AuthManager
│   │   │   ├── models.py          # Auth-related models
│   │   │   ├── oauth/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── outlook.py     # Outlook OAuth implementation
│   │   │   │   ├── pipedrive.py   # Pipedrive OAuth implementation
│   │   │   │   └── base.py        # Base OAuth class
│   │   │   └── utils.py           # Auth utilities
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Auth endpoints
│   │   │   ├── dashboard.py       # Dashboard endpoints
│   │   │   ├── webhooks.py        # Webhook handlers
│   │   │   ├── setup.py           # Setup/configuration endpoints
│   │   │   └── websocket.py       # WebSocket endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── email_processor.py # Core email processing
│   │   │   ├── ai_analyzer.py     # AI content analysis
│   │   │   ├── pipedrive_service.py # Pipedrive integration (MCP)
│   │   │   ├── outlook_service.py # Outlook API client
│   │   │   ├── usage_monitor.py   # Usage tracking & limits
│   │   │   └── webhook_manager.py # Webhook subscription management
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── database.py        # SQLAlchemy models
│   │   │   ├── schemas.py         # Pydantic schemas
│   │   │   ├── auth.py            # Auth-related models
│   │   │   └── types.py           # Custom types
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── database.py        # Database connection
│   │   │   ├── encryption.py      # Credential encryption
│   │   │   ├── websocket.py       # WebSocket manager
│   │   │   ├── mcp_client.py      # MCP client integration
│   │   │   └── exceptions.py      # Custom exceptions
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validation.py      # Input validation
│   │       ├── formatting.py      # Data formatting
│   │       ├── constants.py       # Application constants
│   │       ├── logging.py         # Logging configuration
│   │       └── helpers.py         # General utilities
├── migrations/                    # Alembic database migrations
│   ├── versions/
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_nextauth_tables.py
│   │   ├── 003_add_credentials_table.py
│   │   ├── 004_add_usage_tracking.py
│   │   └── 005_add_webhook_subscriptions.py
│   ├── script.py.mako
│   └── env.py
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── test_auth/
│   │   ├── __init__.py
│   │   ├── test_manager.py       # AuthManager tests
│   │   ├── test_oauth.py         # OAuth flow tests
│   │   └── test_encryption.py    # Encryption tests
│   ├── test_services/
│   │   ├── __init__.py
│   │   ├── test_email_processor.py
│   │   ├── test_ai_analyzer.py
│   │   ├── test_pipedrive_service.py
│   │   └── test_usage_monitor.py
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_auth_endpoints.py
│   │   ├── test_webhooks.py
│   │   └── test_dashboard.py
│   ├── fixtures/
│   │   ├── sample_emails.json
│   │   ├── test_users.json
│   │   ├── mock_responses.json
│   │   └── test_credentials.json
│   └── integration/
│       ├── __init__.py
│       ├── test_oauth_flow.py
│       ├── test_email_to_deal.py
│       └── test_websocket.py
├── scripts/                       # Development and deployment scripts
│   ├── setup_dev.py              # Development environment setup
│   ├── migrate.py                # Database migration runner
│   ├── seed_db.py                # Database seeding
│   ├── generate_encryption_key.py # Generate encryption keys
│   └── deploy.sh                 # Deployment script
├── docs/                         # Documentation
│   ├── setup-guide.md
│   ├── api-reference.md
│   ├── authentication.md
│   ├── deployment.md
│   ├── troubleshooting.md
│   └── architecture.md
├── monitoring/                   # Monitoring and logging
│   ├── health_check.py
│   ├── metrics.py
│   └── alerts.py
└── .github/                      # GitHub Actions
    └── workflows/
        ├── ci.yml
        ├── deploy.yml
        └── test.yml

## Core Development Rules

### 1. Security & Privacy First
- **NEVER store email content** - only process in memory and immediately discard
- **Always encrypt sensitive credentials** using `backend/core/encryption.py`
- **Use user-provided API keys** stored encrypted, never system-wide keys
- **Implement usage limits** to prevent unexpected AI billing
- **Validate all inputs** before processing
- **Follow GDPR compliance** - log only non-PII metadata

### 2. Railway-Specific Guidelines

**Environment Variables:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")  # Railway auto-provides
NEXTAUTH_SECRET = os.getenv("NEXTAUTH_SECRET")
CREDENTIAL_ENCRYPTION_KEY = os.getenv("CREDENTIAL_ENCRYPTION_KEY")
```

**Database Connection:**
```python
# Use Railway's auto-provided DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Handle Railway connection issues
    pool_recycle=300     # Recycle connections
)
SessionLocal = sessionmaker(bind=engine)
```

**Deployment Configuration:**
```python
# Railway automatically detects and runs:
# 1. Frontend: npm run build && npm start (from frontend/)
# 2. Backend: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3. Unified Authentication Pattern

**Always use the AuthManager for all authentication needs:**

```python
# backend/app/auth/manager.py - Core pattern
from app.auth.manager import AuthManager

# Initialize once, use everywhere
auth_manager = AuthManager()

# User authentication (NextAuth.js integration)
user = await auth_manager.get_current_user(session_token)

# Service authentication (auto-refresh tokens)
outlook_client = await auth_manager.get_outlook_client(user.id)
pipedrive_client = await auth_manager.get_pipedrive_client(user.id)
ai_client = await auth_manager.get_ai_client(user.id)
```

**FastAPI Dependency Pattern:**
```python
# backend/dependencies.py
from fastapi import Depends, HTTPException
from app.auth.manager import AuthManager

auth_manager = AuthManager()

async def get_current_user(session_token: str = Depends(get_session_token)):
    user = await auth_manager.get_current_user(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

async def get_outlook_client(user: User = Depends(get_current_user)):
    return await auth_manager.get_outlook_client(user.id)
```

### 4. Database Operations with SQLAlchemy

**Model Definition Pattern:**
```python
# backend/app/models/database.py
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    credentials = relationship("UserCredential", back_populates="user")
    email_logs = relationship("EmailAnalysisLog", back_populates="user")
```

**Database Session Pattern:**
```python
# backend/app/core/database.py
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Usage in services
async def create_user(user_data: dict) -> User:
    async with get_db_session() as db:
        user = User(**user_data)
        db.add(user)
        db.flush()  # Get ID without committing
        return user
```

### 5. Email Processing Pattern (GDPR-Compliant)

**Always follow the process-and-discard pattern:**

```python
# backend/app/services/email_processor.py
async def process_email_webhook(webhook_data: dict, user_id: str):
    email_content = None  # Initialize to None
    
    try:
        # 1. Check usage limits FIRST
        await usage_monitor.check_limits(user_id)
        
        # 2. Fetch email content (temporary, in-memory only)
        outlook_client = await auth_manager.get_outlook_client(user_id)
        email_content = await outlook_client.get_email_content(webhook_data['message_id'])
        
        # 3. AI analysis (never store content)
        ai_client = await auth_manager.get_ai_client(user_id)
        analysis = await ai_client.analyze_email(email_content)
        
        # 4. Search existing deals
        pipedrive_client = await auth_manager.get_pipedrive_client(user_id)
        existing_deals = await pipedrive_client.search_deals(analysis.keywords)
        
        # 5. Create deal if needed
        deal_created = False
        if analysis.is_sales_opportunity and not existing_deals:
            deal = await pipedrive_client.create_deal(analysis)
            deal_created = True
        
        # 6. Log metadata only (NO email content)
        await log_email_analysis(user_id, analysis, deal_created, email_content=None)
        
        # 7. Track usage and costs
        await usage_monitor.track_usage(user_id, analysis.tokens_used, analysis.cost)
        
        # 8. Send real-time update
        await websocket_manager.send_update(user_id, {
            'type': 'email_processed',
            'analysis': analysis.to_dict(),
            'deal_created': deal_created
        })
        
    except Exception as e:
        logger.error(f"Email processing failed for user {user_id}: {e}")
        raise
    finally:
        # 9. ALWAYS discard email content
        email_content = None
        
async def log_email_analysis(user_id: str, analysis: EmailAnalysis, deal_created: bool, email_content=None):
    """Log analysis results WITHOUT storing email content"""
    if email_content is not None:
        raise ValueError("Email content must never be stored")
    
    # Only store safe metadata
    log_data = {
        'user_id': user_id,
        'sender_domain': analysis.sender_domain,
        'subject_hash': hash_subject(analysis.subject),  # Hash, not plaintext
        'subject_length': len(analysis.subject),
        'body_word_count': analysis.word_count,
        'is_sales_opportunity': analysis.is_sales_opportunity,
        'confidence_score': analysis.confidence,
        'keywords_detected': analysis.keywords,
        'ai_reasoning': analysis.safe_summary,  # AI-generated summary, not original
        'deal_created': deal_created,
        'tokens_used': analysis.tokens_used,
        'cost_incurred': analysis.cost
    }
    
    async with get_db_session() as db:
        log = EmailAnalysisLog(**log_data)
        db.add(log)
```

### 6. AI Integration with User Keys

**Always use user-provided API keys with usage protection:**

```python
# backend/app/services/ai_analyzer.py
class AIAnalyzer:
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
    
    async def analyze_email(self, user_id: str, email_content: str) -> EmailAnalysis:
        # Get user's AI client (with their API key)
        ai_client = await self.auth_manager.get_ai_client(user_id)
        
        # Estimate cost before processing
        estimated_tokens = self.estimate_tokens(email_content)
        estimated_cost = self.estimate_cost(estimated_tokens, ai_client.model)
        
        # Check if user can afford this request
        await usage_monitor.check_spend_limit(user_id, estimated_cost)
        
        # Make AI request
        response = await ai_client.analyze_content(
            content=email_content,
            prompt=self.get_analysis_prompt(),
            max_tokens=500
        )
        
        return EmailAnalysis.from_ai_response(response)
    
    def get_analysis_prompt(self) -> str:
        return """
        Analyze this email for sales opportunities. Return JSON with:
        {
            "is_sales_opportunity": boolean,
            "confidence": float (0-1),
            "keywords": ["product", "service", "terms"],
            "estimated_value": number or null,
            "reasoning": "brief explanation",
            "urgency": "low|medium|high",
            "next_steps": ["action1", "action2"]
        }
        
        Email content: {content}
        """
```

### 7. MCP Client Integration

**Embed MCP client into Pipedrive service:**

```python
# backend/app/services/pipedrive_service.py
from app.core.mcp_client import MCPClient

class PipedriveService:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.mcp_client = MCPClient(
            base_url="https://api.pipedrive.com/v1",
            auth_token=access_token
        )
    
    async def search_deals(self, keywords: list[str]) -> list[Deal]:
        """Search for existing deals using MCP tools"""
        search_params = {
            'term': ' '.join(keywords),
            'fields': 'title,person,org',
            'limit': 50
        }
        
        result = await self.mcp_client.call_tool('search_deals', search_params)
        return [Deal.from_pipedrive_data(item) for item in result.get('data', [])]
    
    async def create_deal(self, analysis: EmailAnalysis) -> Deal:
        """Create deal with AI attribution"""
        deal_data = {
            'title': f"{' '.join(analysis.keywords[:3])} - AI Generated",
            'value': analysis.estimated_value,
            'currency': 'USD',
            'status': 'open',
            'add_time': datetime.now().isoformat(),
            # AI Attribution
            'source': 'AI Email Processor',
            'visible_to': '3',  # Owner only
            'custom_fields': {
                'ai_created': True,
                'ai_confidence': analysis.confidence,
                'ai_keywords': analysis.keywords,
                'email_processed_at': datetime.now().isoformat()
            }
        }
        
        result = await self.mcp_client.call_tool('create_deal', deal_data)
        return Deal.from_pipedrive_data(result['data'])
```

### 8. WebSocket Real-time Updates

**Implement WebSocket for real-time dashboard updates:**

```python
# backend/app/api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_update(self, user_id: str, data: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(data))
            except:
                # Connection broken, remove it
                await self.disconnect(user_id)

websocket_manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Authenticate WebSocket connection
    user = await auth_manager.get_current_user(token)
    if not user:
        await websocket.close(code=4001)
        return
    
    await websocket_manager.connect(websocket, user.id)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.disconnect(user.id)
```

### 9. Next.js Frontend Integration

**NextAuth.js configuration:**

```typescript
// frontend/src/lib/auth/config.ts
import NextAuth from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async session({ session, user }) {
      session.user.id = user.id
      return session
    },
    async jwt({ token, user }) {
      if (user) {
        token.userId = user.id
      }
      return token
    },
  },
  pages: {
    signIn: '/auth/signin',
    signUp: '/auth/signup',
  },
})
```

**API Client Pattern:**

```typescript
// frontend/src/lib/api/client.ts
import { getSession } from 'next-auth/react'

class APIClient {
  private baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  
  private async getAuthHeaders() {
    const session = await getSession()
    return {
      'Authorization': `Bearer ${session?.accessToken}`,
      'Content-Type': 'application/json'
    }
  }
  
  async connectOutlook(): Promise<{ auth_url: string }> {
    const headers = await this.getAuthHeaders()
    const response = await fetch(`${this.baseURL}/api/auth/connect/outlook`, {
      method: 'GET',
      headers
    })
    return response.json()
  }
  
  async getEmailLogs(): Promise<EmailLog[]> {
    const headers = await this.getAuthHeaders()
    const response = await fetch(`${this.baseURL}/api/dashboard/logs`, {
      method: 'GET',
      headers
    })
    return response.json()
  }
}

export const apiClient = new APIClient()
```

**Real-time Hook:**

```typescript
// frontend/src/lib/hooks/use-websocket.ts
import { useEffect, useState } from 'react'
import { useSession } from 'next-auth/react'

export function useWebSocket() {
  const { data: session } = useSession()
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [data, setData] = useState<any[]>([])
  
  useEffect(() => {
    if (!session?.accessToken) return
    
    const ws = new WebSocket(`ws://localhost:8000/ws?token=${session.accessToken}`)
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)
      setData(prev => [update, ...prev])
    }
    
    ws.onopen = () => setSocket(ws)
    ws.onclose = () => setSocket(null)
    
    return () => ws.close()
  }, [session])
  
  return { socket, data }
}
```

### 10. Error Handling & Logging

**Structured logging pattern:**

```python
# backend/app/utils/logging.py
import logging
import json
from datetime import datetime

def log_event(user_id: str, event_type: str, data: dict, level: str = 'info'):
    """Structured logging for all events"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'event_type': event_type,
        'level': level,
        'data': data
    }
    
    # Never log sensitive data
    sanitized_data = sanitize_log_data(data)
    log_entry['data'] = sanitized_data
    
    logger = logging.getLogger(__name__)
    getattr(logger, level)(json.dumps(log_entry))

def sanitize_log_data(data: dict) -> dict:
    """Remove sensitive data from logs"""
    sensitive_keys = ['access_token', 'api_key', 'email_content', 'password']
    
    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys:
            sanitized[key] = '[REDACTED]'
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        else:
            sanitized[key] = value
    
    return sanitized
```

### 11. Testing Patterns

**Service Testing:**

```python
# tests/test_services/test_email_processor.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.email_processor import EmailProcessor

@pytest.fixture
async def email_processor():
    with patch('app.auth.manager.AuthManager') as mock_auth:
        mock_auth.return_value.get_outlook_client = AsyncMock()
        mock_auth.return_value.get_ai_client = AsyncMock()
        mock_auth.return_value.get_pipedrive_client = AsyncMock()
        yield EmailProcessor(mock_auth.return_value)

@pytest.mark.asyncio
async def test_process_email_creates_deal(email_processor):
    # Mock email content (never stored)
    mock_email = "Hi, I'm interested in your software solution..."
    
    # Mock AI analysis
    mock_analysis = EmailAnalysis(
        is_sales_opportunity=True,
        confidence=0.85,
        keywords=['software', 'solution'],
        estimated_value=5000
    )
    
    # Mock no existing deals
    email_processor.auth_manager.get_pipedrive_client.return_value.search_deals.return_value = []
    email_processor.auth_manager.get_ai_client.return_value.analyze_email.return_value = mock_analysis
    
    # Process email
    result = await email_processor.process_email_webhook(
        {'message_id': 'test123'}, 
        'user123'
    )
    
    # Verify deal was created
    assert result.deal_created == True
    assert result.analysis.confidence == 0.85
```

### 12. Deployment & Environment

**Railway-specific patterns:**

```python
# main.py - Entry point for Railway
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="AI Email Processor")

# Railway-friendly CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://*.railway.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api import auth, dashboard, webhooks, websocket
app.include_router(auth.router, prefix="/api/auth")
app.include_router(dashboard.router, prefix="/api/dashboard")
app.include_router(webhooks.router, prefix="/api/webhooks")
app.include_router(websocket.router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

**Environment configuration:**

```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    nextauth_secret: str
    credential_encryption_key: str
    outlook_client_id: str
    outlook_client_secret: str
    pipedrive_client_id: str
    pipedrive_client_secret: str
    base_url: str = "https://your-app.railway.app"
    environment: str = "production"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Common Patterns to Follow

### 1. Service Initialization
```python
# Always inject AuthManager
class SomeService:
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
    
    async def do_something(self, user_id: str):
        client = await self.auth_manager.get_some_client(user_id)
        return await client.perform_action()
```

### 2. Error Handling
```python
# Consistent error responses
try:
    result = await some_operation()
    return {"success": True, "data": result}
except ServiceException as e:
    log_event(user_id, 'service_error', {'error': str(e)}, 'error')
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    log_event(user_id, 'unexpected_error', {'error': str(e)}, 'error')
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 3. Usage Tracking
```python
# Always track AI usage
async def process_with_ai(user_id: str, content: str):
    # Check limits first
    await usage_monitor.check_limits(user_id)
    
    # Process
    result = await ai_client.process(content)
    
    # Track usage
    await usage_monitor.track_usage(
        user_id, 
        tokens_used=result.tokens,
        cost=result.cost
    )
    
    return result
```

## Critical Reminders

1. **Never store email content** - always process and discard
2. **Use the unified AuthManager** for all authentication needs
3. **Encrypt all credentials** before database storage
4. **Check usage limits** before AI processing
5. **Use Railway environment variables** properly
6. **Implement proper error handling** with structured logging
7. **Follow NextAuth.js patterns** for frontend authentication
8. **Use WebSockets** for real-time dashboard updates
9. **Test with real OAuth flows** during development
10. **Monitor costs and usage** continuously

## Architecture Principles

- **Security by Design**: Encrypt everything, validate all inputs
- **Privacy by Default**: GDPR compliance, minimal data collection
- **Unified Authentication**: One AuthManager for all auth needs
- **Cost Protection**: Usage limits and monitoring
- **Real-time Updates**: WebSocket for immediate feedback
- **Railway Optimization**: Leverage platform features
- **Testable Code**: Mock external services, test core logic
- **Scalable Design**: Easy to add new services and features

Follow these rules consistently to build a secure, scalable, and maintainable AI email processing system on Railway.