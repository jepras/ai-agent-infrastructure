from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid


# Base schemas
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    image: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: str
    email_verified: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @validator("id", pre=True)
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


# Profile schemas
class UserProfileBase(BaseModel):
    monitoring_enabled: bool = False
    ai_model_preference: str = "gpt-4o-mini"
    pipedrive_domain: Optional[str] = None

    @validator("ai_model_preference")
    def validate_ai_model(cls, v):
        if v not in ["gpt-4o-mini", "claude-sonnet-4"]:
            raise ValueError("AI model must be either gpt-4o-mini or claude-sonnet-4")
        return v


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(UserProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime

    @validator("id", pre=True)
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


# Credential schemas
class CredentialBase(BaseModel):
    credential_type: str
    expires_at: Optional[datetime] = None
    meta: Optional[Dict[str, Any]] = None


class CredentialCreate(CredentialBase):
    data: str  # This will be encrypted before storage


class CredentialResponse(CredentialBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @validator("id", pre=True)
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


# Usage schemas
class UsageLimitBase(BaseModel):
    daily_email_limit: int = Field(default=100, ge=1, le=10000)
    monthly_token_limit: int = Field(default=50000, ge=1000, le=1000000)
    daily_spend_limit: Decimal = Field(
        default=Decimal("5.00"), ge=Decimal("0.01"), le=Decimal("1000.00")
    )
    monthly_spend_limit: Decimal = Field(
        default=Decimal("50.00"), ge=Decimal("0.01"), le=Decimal("10000.00")
    )


class UsageLimitUpdate(UsageLimitBase):
    pass


class UsageLimitResponse(UsageLimitBase):
    user_id: str
    updated_at: datetime

    class Config:
        from_attributes = True


class UsageTrackingResponse(BaseModel):
    id: str
    user_id: str
    date: datetime
    emails_processed: int
    tokens_used: int
    cost_incurred: Decimal

    @validator("id", "user_id", pre=True)
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


# Service status schemas
class ServiceStatusResponse(BaseModel):
    outlook: bool
    pipedrive: bool
    openai: bool
    anthropic: bool


# Email analysis schemas
class EmailAnalysisBase(BaseModel):
    sender_domain: Optional[str] = None
    subject_hash: Optional[str] = None
    subject_length: Optional[int] = None
    body_word_count: Optional[int] = None
    is_sales_opportunity: Optional[bool] = None
    confidence_score: Optional[Decimal] = Field(None, ge=Decimal("0"), le=Decimal("1"))
    keywords_detected: Optional[List[str]] = None
    ai_reasoning: Optional[str] = None
    ai_model_used: Optional[str] = None
    estimated_deal_value: Optional[Decimal] = None
    deal_created: bool = False
    deal_skipped_reason: Optional[str] = None
    processing_duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    cost_incurred: Optional[Decimal] = None
    error_occurred: bool = False
    error_message: Optional[str] = None


class EmailAnalysisCreate(EmailAnalysisBase):
    user_id: str


class EmailAnalysisResponse(EmailAnalysisBase):
    id: str
    user_id: str
    processed_at: datetime

    @validator("id", "user_id", pre=True)
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


# Deal schemas
class DealCreatedBase(BaseModel):
    pipedrive_deal_id: str
    deal_title: Optional[str] = None
    deal_value: Optional[Decimal] = None
    pipeline_stage: Optional[str] = None
    deal_owner_id: Optional[str] = None
    ai_created: bool = True


class DealCreatedCreate(DealCreatedBase):
    user_id: str
    email_analysis_id: str


class DealCreatedResponse(DealCreatedBase):
    id: str
    user_id: str
    email_analysis_id: str
    created_at: datetime

    @validator("id", "user_id", "email_analysis_id", pre=True)
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


# Webhook subscription schemas
class WebhookSubscriptionBase(BaseModel):
    provider: str
    subscription_id: Optional[str] = None
    webhook_url: Optional[str] = None
    is_active: bool = True


class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    user_id: str


class WebhookSubscriptionResponse(WebhookSubscriptionBase):
    id: str
    user_id: str
    created_at: datetime

    @validator("id", "user_id", pre=True)
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


# Dashboard schemas
class DashboardStatsResponse(BaseModel):
    total_emails_processed: int
    total_deals_created: int
    total_cost_incurred: Decimal
    emails_processed_today: int
    deals_created_today: int
    cost_incurred_today: Decimal
    service_status: ServiceStatusResponse


class DashboardLogsResponse(BaseModel):
    logs: List[EmailAnalysisResponse]
    total: int
    page: int
    per_page: int
    has_more: bool


class DashboardDealsResponse(BaseModel):
    deals: List[DealCreatedResponse]
    total: int
    page: int
    per_page: int
    has_more: bool


# API Key schemas
class ApiKeyCreate(BaseModel):
    api_key: str
    provider: str = Field(..., pattern="^(openai|anthropic)$")

    @validator("provider")
    def validate_provider(cls, v):
        if v not in ["openai", "anthropic"]:
            raise ValueError("Provider must be either openai or anthropic")
        return v


# OAuth schemas
class OAuthInitiateResponse(BaseModel):
    auth_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    error: Optional[str] = None


# Health check schema
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    database: bool
    services: Dict[str, bool]
