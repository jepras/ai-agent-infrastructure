# AI Email-to-Deal Processor - Technical Specification (Railway Edition)

## Project Overview

A GDPR-compliant AI system that monitors outgoing Outlook emails, identifies sales opportunities, and automatically creates deals in Pipedrive. Built entirely on Railway infrastructure with unified authentication management and process-and-discard email handling.

## Architecture Overview

### Technology Stack
- **Platform**: Railway (full-stack deployment)
- **Backend**: Python FastAPI + PostgreSQL
- **Frontend**: Next.js 13+ with NextAuth.js
- **Authentication**: Unified AuthManager (user auth + service OAuth)
- **AI Processing**: User-provided OpenAI/Anthropic API keys
- **CRM Integration**: Pipedrive API with integrated MCP client
- **Email Integration**: Outlook API via OAuth

### Core Components
1. **Unified Authentication System** (user login + service OAuth)
2. **Email Monitoring Service** (Outlook webhooks)
3. **AI Content Analysis Engine** (process-and-discard pattern)
4. **Pipedrive Integration** (MCP client embedded)
5. **Real-time Dashboard** (WebSocket updates)
6. **Usage Protection System** (billing limits)

## Database Schema

```sql
-- Users table (NextAuth.js compatible)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR,
  image VARCHAR,
  email_verified TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- NextAuth.js required tables
CREATE TABLE accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR NOT NULL,
  provider VARCHAR NOT NULL,
  provider_account_id VARCHAR NOT NULL,
  refresh_token TEXT,
  access_token TEXT,
  expires_at INTEGER,
  token_type VARCHAR,
  scope VARCHAR,
  id_token TEXT,
  session_state VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(provider, provider_account_id)
);

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_token VARCHAR UNIQUE NOT NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Unified credentials storage (all service tokens/keys)
CREATE TABLE user_credentials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  credential_type VARCHAR NOT NULL, -- 'outlook_oauth', 'pipedrive_oauth', 'openai_api_key', 'anthropic_api_key'
  encrypted_data TEXT NOT NULL,
  expires_at TIMESTAMP,
  is_active BOOLEAN DEFAULT true,
  metadata JSONB, -- Store scopes, refresh tokens, etc.
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, credential_type)
);

-- User configuration
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES users(id),
  monitoring_enabled BOOLEAN DEFAULT false,
  ai_model_preference VARCHAR DEFAULT 'gpt-4o-mini' CHECK (ai_model_preference IN ('gpt-4o-mini', 'claude-sonnet-4')),
  pipedrive_domain VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Email processing logs (GDPR-compliant metadata only)
CREATE TABLE email_analysis_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  processed_at TIMESTAMP DEFAULT NOW(),
  
  -- Safe metadata (no PII)
  sender_domain VARCHAR, -- e.g., "gmail.com"
  subject_hash VARCHAR, -- SHA-256 hash of subject
  subject_length INTEGER,
  body_word_count INTEGER,
  
  -- AI analysis results
  is_sales_opportunity BOOLEAN,
  confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
  keywords_detected TEXT[],
  ai_reasoning TEXT, -- Safe summary, not original content
  ai_model_used VARCHAR,
  estimated_deal_value NUMERIC,
  
  -- Processing results
  deal_created BOOLEAN DEFAULT false,
  deal_skipped_reason VARCHAR,
  processing_duration_ms INTEGER,
  tokens_used INTEGER,
  cost_incurred NUMERIC,
  
  -- Error handling
  error_occurred BOOLEAN DEFAULT false,
  error_message TEXT
);

-- Created deals tracking
CREATE TABLE deals_created (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  email_analysis_id UUID REFERENCES email_analysis_logs,
  pipedrive_deal_id VARCHAR NOT NULL,
  deal_title VARCHAR,
  deal_value NUMERIC,
  pipeline_stage VARCHAR,
  deal_owner_id VARCHAR, -- Pipedrive user ID
  ai_created BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Usage tracking and billing protection
CREATE TABLE usage_limits (
  user_id UUID PRIMARY KEY REFERENCES users(id),
  daily_email_limit INTEGER DEFAULT 100,
  monthly_token_limit INTEGER DEFAULT 50000,
  daily_spend_limit NUMERIC DEFAULT 5.00,
  monthly_spend_limit NUMERIC DEFAULT 50.00,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE usage_tracking (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  date DATE DEFAULT CURRENT_DATE,
  emails_processed INTEGER DEFAULT 0,
  tokens_used INTEGER DEFAULT 0,
  cost_incurred NUMERIC DEFAULT 0,
  UNIQUE(user_id, date)
);

-- Webhook subscriptions
CREATE TABLE webhook_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  provider VARCHAR NOT NULL, -- 'outlook'
  subscription_id VARCHAR, -- External webhook ID
  webhook_url VARCHAR,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, provider)
);
```

## API Endpoints

### Authentication Endpoints
- `POST /auth/signin` - User login (NextAuth.js)
- `POST /auth/signout` - User logout (NextAuth.js)
- `GET /auth/session` - Get current session (NextAuth.js)

### Service Connection Endpoints
- `GET /api/auth/connect/{service}` - Initiate OAuth flow (outlook/pipedrive)
- `GET /api/auth/callback/{service}` - Handle OAuth callback
- `POST /api/auth/api-key` - Store AI API key
- `DELETE /api/auth/disconnect/{service}` - Remove service connection

### Processing Endpoints
- `POST /api/webhooks/outlook` - Outlook email webhook
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/logs` - Email processing logs
- `GET /api/dashboard/deals` - Created deals list
- `WebSocket /ws` - Real-time updates

### Configuration Endpoints
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user preferences
- `GET /api/user/usage` - Get usage statistics
- `PUT /api/user/limits` - Update usage limits

## Email Processing Flow

```
1. Email sent by user
2. Outlook webhook triggered
3. FastAPI receives webhook
4. Authenticate user from webhook data
5. Fetch email content via Outlook API (temporary)
6. Check usage limits before AI processing
7. AI analysis of content (user's API key)
8. Search existing Pipedrive deals via MCP client
9. Create deal if it doesn't exist in pipeline
10. Log analysis results (metadata only)
11. Discard email content from memory
12. Send real-time update via WebSocket
```

## Implementation Plan

### Phase 1: Foundation & Authentication (Week 1-2)

**Railway Setup**
- [ ] Create Railway project with PostgreSQL
- [ ] Set up environment variables
- [ ] Configure custom domain

**Backend Foundation**
- [ ] Initialize FastAPI project structure
- [ ] Set up database models with SQLAlchemy
- [ ] Implement database migrations
- [ ] Create unified AuthManager class

**Frontend Foundation**
- [ ] Initialize Next.js project with NextAuth.js
- [ ] Configure NextAuth.js with database adapter
- [ ] Set up basic dashboard layout
- [ ] Implement user registration/login flow

### Phase 2: Service OAuth Integration (Week 3-4)

**Unified Authentication System**
- [ ] Implement OAuth flow for Outlook
- [ ] Implement OAuth flow for Pipedrive
- [ ] Create encrypted credential storage
- [ ] Build service connection management
- [ ] Add token refresh automation

**Service Integration**
- [ ] Build Outlook API client with auto-refresh
- [ ] Build Pipedrive API client with MCP integration
- [ ] Implement webhook subscription management
- [ ] Create service health monitoring

### Phase 3: Email Processing Core (Week 5-6)

**Email Monitoring**
- [ ] Implement Outlook webhook handler
- [ ] Create email content fetcher (temporary processing)
- [ ] Build process-and-discard email system
- [ ] Add comprehensive error handling

**AI Integration**
- [ ] Implement AI analysis with user API keys
- [ ] Create email content analysis prompts
- [ ] Add confidence scoring and keyword extraction
- [ ] Implement usage tracking and cost calculation

### Phase 4: Deal Processing (Week 7-8)

**Pipedrive Integration**
- [ ] Embed MCP client for deal operations
- [ ] Implement deal search and duplicate detection
- [ ] Create deal creation with AI attribution
- [ ] Add pipeline stage mapping

**Usage Protection**
- [ ] Implement daily/monthly spending limits
- [ ] Add usage monitoring and alerts
- [ ] Create cost estimation before processing
- [ ] Build automatic cutoff mechanisms

### Phase 5: Dashboard & Real-time Features (Week 9-10)

**Frontend Dashboard**
- [ ] Create real-time email processing logs
- [ ] Build deal creation tracking with filters
- [ ] Add usage monitoring and billing dashboard
- [ ] Implement service connection status

**Real-time System**
- [ ] Set up WebSocket connections
- [ ] Implement real-time log updates
- [ ] Add system health monitoring
- [ ] Create notification system

### Phase 6: Testing & Deployment (Week 11-12)

**Testing**
- [ ] Unit tests for AuthManager and core services
- [ ] Integration tests for OAuth flows
- [ ] End-to-end tests with real Outlook/Pipedrive accounts
- [ ] Load testing for webhook processing

**Production Deployment**
- [ ] Railway production environment setup
- [ ] Domain configuration and SSL
- [ ] Monitoring and alerting setup
- [ ] Documentation and user guides

## Technical Specifications

### Unified AuthManager Interface
```python
class AuthManager:
    # User Authentication (NextAuth.js integration)
    async def get_current_user(self, session_token: str) -> User | None
    async def create_user_session(self, user_id: str) -> str
    
    # Service Authentication
    async def connect_outlook(self, user_id: str, oauth_code: str) -> bool
    async def connect_pipedrive(self, user_id: str, oauth_code: str) -> bool
    async def store_ai_api_key(self, user_id: str, provider: str, api_key: str) -> bool
    
    # Service Clients (auto-refresh tokens)
    async def get_outlook_client(self, user_id: str) -> OutlookClient
    async def get_pipedrive_client(self, user_id: str) -> PipedriveClient
    async def get_ai_client(self, user_id: str) -> AIClient
    
    # Credential Management
    async def refresh_service_tokens(self, user_id: str, service: str) -> bool
    async def revoke_service_access(self, user_id: str, service: str) -> bool
    async def get_service_status(self, user_id: str) -> dict
```

### AI Analysis Response Format
```python
class EmailAnalysisResult:
    is_sales_opportunity: bool
    confidence_score: float  # 0.0 to 1.0
    keywords: list[str]
    estimated_deal_value: float | None
    reasoning: str
    urgency_level: str  # 'low', 'medium', 'high'
    next_steps: list[str]
    contact_info: dict | None
```

### MCP Client Integration
```python
class PipedriveService:
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
    
    async def search_existing_deals(self, user_id: str, keywords: list[str]) -> list[Deal]
    async def create_deal(self, user_id: str, analysis: EmailAnalysisResult) -> Deal
    async def get_pipelines(self, user_id: str) -> list[Pipeline]
```

### WebSocket Real-time Updates
```python
class WebSocketManager:
    async def send_email_processed(self, user_id: str, log: EmailAnalysisLog)
    async def send_deal_created(self, user_id: str, deal: Deal)
    async def send_usage_alert(self, user_id: str, usage: UsageStats)
    async def send_system_status(self, user_id: str, status: SystemStatus)
```

## Railway Deployment Configuration

### Environment Variables
```bash
# Database (Railway auto-provides)
DATABASE_URL=postgresql://...

# NextAuth.js
NEXTAUTH_URL=https://your-app.railway.app
NEXTAUTH_SECRET=your-nextauth-secret

# OAuth Applications (your app credentials)
OUTLOOK_CLIENT_ID=your-outlook-app-id
OUTLOOK_CLIENT_SECRET=your-outlook-secret
PIPEDRIVE_CLIENT_ID=your-pipedrive-app-id
PIPEDRIVE_CLIENT_SECRET=your-pipedrive-secret

# System Security
CREDENTIAL_ENCRYPTION_KEY=your-encryption-key
JWT_SECRET=your-jwt-secret

# Application Configuration
BASE_URL=https://your-app.railway.app
ENVIRONMENT=production
```

### Cost Estimates

**Railway Hosting**: $5/month
- Full-stack deployment
- PostgreSQL database included
- Custom domain included

**AI Processing Costs** (50 emails/day):
- **GPT-4o Mini**: ~$0.30/month per user
- **Claude Sonnet 4**: ~$4.50/month per user

**Total Operating Cost**: $5-10/month for single user

## Security & Compliance

### GDPR Compliance Measures
- **No email content storage**: All processing in-memory only
- **Minimal metadata collection**: Only non-PII analysis results
- **User control**: Complete data export and deletion
- **Audit logging**: All credential access tracked
- **Data retention**: 90-day automatic cleanup

### Security Features
- **Credential encryption**: All tokens encrypted at rest
- **Token auto-refresh**: Automatic renewal without user intervention
- **Usage limits**: Prevent unexpected billing
- **Rate limiting**: Protect against abuse
- **Webhook validation**: Verify all incoming requests

## Success Metrics
- **Processing Accuracy**: >90% correct sales opportunity detection
- **Response Time**: <30 seconds from email to deal creation
- **Uptime**: 99.9% availability
- **Cost Control**: Zero unexpected billing incidents
- **User Satisfaction**: Measured via dashboard feedback

---

*This specification provides a complete roadmap for building a production-ready AI email processor with unified authentication and Railway deployment.*