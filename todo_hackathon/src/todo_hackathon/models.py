"""Todo model definitions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Todo:
    """Represents a single todo item."""
    
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate todo after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Todo title cannot be empty")
        
        # Ensure updated_at is at least as recent as created_at
        if self.updated_at < self.created_at:
            self.updated_at = self.created_at

