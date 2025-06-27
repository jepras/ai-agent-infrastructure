from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Numeric,
    Text,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Date,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    image = Column(String)
    email_verified = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    accounts = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    credentials = relationship(
        "UserCredential", back_populates="user", cascade="all, delete-orphan"
    )
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    email_logs = relationship(
        "EmailAnalysisLog", back_populates="user", cascade="all, delete-orphan"
    )
    deals = relationship(
        "DealCreated", back_populates="user", cascade="all, delete-orphan"
    )
    usage_tracking = relationship(
        "UsageTracking", back_populates="user", cascade="all, delete-orphan"
    )
    webhook_subscriptions = relationship(
        "WebhookSubscription", back_populates="user", cascade="all, delete-orphan"
    )


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    provider_account_id = Column(String, nullable=False)
    refresh_token = Column(Text)
    access_token = Column(Text)
    expires_at = Column(Integer)
    token_type = Column(String)
    scope = Column(String)
    id_token = Column(Text)
    session_state = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="accounts")

    # Constraints
    __table_args__ = (
        UniqueConstraint("provider", "provider_account_id", name="uq_provider_account"),
    )


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    session_token = Column(String, unique=True, nullable=False)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expires = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")


class UserCredential(Base):
    __tablename__ = "user_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    credential_type = Column(
        String, nullable=False
    )  # 'outlook_oauth', 'pipedrive_oauth', 'openai_api_key', 'anthropic_api_key'
    encrypted_data = Column(Text, nullable=False)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    meta = Column(JSONB)  # Store scopes, refresh tokens, etc.
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="credentials")

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "credential_type", name="uq_user_credential_type"),
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    monitoring_enabled = Column(Boolean, default=False)
    ai_model_preference = Column(String, default="gpt-4o-mini")
    pipedrive_domain = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="profile")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "ai_model_preference IN ('gpt-4o-mini', 'claude-sonnet-4')",
            name="ck_ai_model_preference",
        ),
    )


class EmailAnalysisLog(Base):
    __tablename__ = "email_analysis_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    processed_at = Column(DateTime, default=func.now())

    # Safe metadata (no PII)
    sender_domain = Column(String)  # e.g., "gmail.com"
    subject_hash = Column(String)  # SHA-256 hash of subject
    subject_length = Column(Integer)
    body_word_count = Column(Integer)

    # AI analysis results
    is_sales_opportunity = Column(Boolean)
    confidence_score = Column(Numeric(3, 2))  # 0.00 to 1.00
    keywords_detected = Column(ARRAY(String))
    ai_reasoning = Column(Text)  # Safe summary, not original content
    ai_model_used = Column(String)
    estimated_deal_value = Column(Numeric(10, 2))

    # Processing results
    deal_created = Column(Boolean, default=False)
    deal_skipped_reason = Column(String)
    processing_duration_ms = Column(Integer)
    tokens_used = Column(Integer)
    cost_incurred = Column(Numeric(10, 4))

    # Error handling
    error_occurred = Column(Boolean, default=False)
    error_message = Column(Text)

    # Relationships
    user = relationship("User", back_populates="email_logs")
    deals = relationship("DealCreated", back_populates="email_analysis")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="ck_confidence_score",
        ),
    )


class DealCreated(Base):
    __tablename__ = "deals_created"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    email_analysis_id = Column(UUID(as_uuid=True), ForeignKey("email_analysis_logs.id"))
    pipedrive_deal_id = Column(String, nullable=False)
    deal_title = Column(String)
    deal_value = Column(Numeric(10, 2))
    pipeline_stage = Column(String)
    deal_owner_id = Column(String)  # Pipedrive user ID
    ai_created = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="deals")
    email_analysis = relationship("EmailAnalysisLog", back_populates="deals")


class UsageLimit(Base):
    __tablename__ = "usage_limits"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    daily_email_limit = Column(Integer, default=100)
    monthly_token_limit = Column(Integer, default=50000)
    daily_spend_limit = Column(Numeric(10, 2), default=5.00)
    monthly_spend_limit = Column(Numeric(10, 2), default=50.00)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UsageTracking(Base):
    __tablename__ = "usage_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    date = Column(Date, default=func.current_date())
    emails_processed = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    cost_incurred = Column(Numeric(10, 4), default=0)

    # Relationships
    user = relationship("User", back_populates="usage_tracking")

    # Constraints
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date"),)


class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    provider = Column(String, nullable=False)  # 'outlook'
    subscription_id = Column(String)  # External webhook ID
    webhook_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="webhook_subscriptions")

    # Constraints
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_user_provider"),)


class OAuthState(Base):
    __tablename__ = "oauth_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    state = Column(String, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    service = Column(String, nullable=False)  # 'outlook', 'pipedrive'
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    state_metadata = Column(JSONB)  # Additional state data
