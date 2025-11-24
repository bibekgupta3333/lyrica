"""
Generation schemas for API requests and responses.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


# Generation Request Schema
class GenerationRequest(BaseModel):
    """Request schema for lyrics generation."""
    prompt: str = Field(..., min_length=1, max_length=1000, description="User prompt for lyrics generation")
    genre: Optional[str] = Field(None, max_length=100, description="Music genre")
    mood: Optional[str] = Field(None, max_length=100, description="Mood/emotion")
    theme: Optional[str] = Field(None, max_length=255, description="Main theme")
    custom_structure: Optional[Dict[str, Any]] = Field(None, description="Custom song structure")
    max_iterations: Optional[int] = Field(default=3, ge=1, le=5, description="Max refinement iterations")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")


# Agent Log Schema
class AgentLogBase(BaseModel):
    """Base agent log schema."""
    agent_name: str
    step_number: int
    execution_time_seconds: Optional[float] = None
    status: str
    error_message: Optional[str] = None


class AgentLog(AgentLogBase):
    """Agent log response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    generation_history_id: uuid.UUID
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    created_at: datetime


# Generation History Schema
class GenerationHistoryBase(BaseModel):
    """Base generation history schema."""
    input_prompt: str
    genre: Optional[str] = None
    mood: Optional[str] = None
    theme: Optional[str] = None
    status: str


class GenerationHistory(GenerationHistoryBase):
    """Generation history response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    user_id: uuid.UUID
    lyrics_id: Optional[uuid.UUID] = None
    custom_structure: Optional[Dict[str, Any]] = None
    agent_steps: List[str]
    iterations: int
    error_message: Optional[str] = None
    total_time_seconds: Optional[float] = None
    llm_time_seconds: Optional[float] = None
    retrieval_time_seconds: Optional[float] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class GenerationHistoryWithLogs(GenerationHistory):
    """Generation history with agent logs."""
    agent_logs: List[AgentLog] = []


# Generation Response Schema
class GenerationResponse(BaseModel):
    """Response schema for lyrics generation."""
    generation_id: uuid.UUID
    lyrics_id: Optional[uuid.UUID] = None
    status: str
    message: str
    lyrics: Optional[Dict[str, Any]] = None
    generation_time_seconds: Optional[float] = None

