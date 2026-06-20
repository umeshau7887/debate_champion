
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class DebateTurn(BaseModel):
    """Represents a single speech or rebuttal by an agent."""
    agent_id: str
    argument: str

class DebateRound(BaseModel):
    """Represents a single round containing turns from opposing sides."""
    round_number: int
    turns: List[DebateTurn] = Field(default_factory=list)

class DebateSession(BaseModel):
    """Tracks the entire state, configuration, and history of the debate."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    motion: str
    total_rounds: int
    current_round: int = 1
    is_completed: bool = False
    
    rounds: List[DebateRound] = Field(default_factory=list)
    winner_id: Optional[str] = None
