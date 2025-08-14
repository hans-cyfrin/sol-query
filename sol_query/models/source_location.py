"""Source location models for tracking code positions."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class SourceLocation(BaseModel):
    """
    Represents a location in source code with detailed position information.
    
    This model tracks both line/column positions (1-indexed for human readability)
    and byte positions (0-indexed for programmatic use).
    """
    
    file_path: Optional[Path] = Field(
        default=None,
        description="Path to the source file, if known"
    )
    
    start_line: int = Field(
        ge=1,
        description="Starting line number (1-indexed)"
    )
    
    start_column: int = Field(
        ge=1,
        description="Starting column number (1-indexed)"
    )
    
    end_line: int = Field(
        ge=1,
        description="Ending line number (1-indexed)"
    )
    
    end_column: int = Field(
        ge=1,
        description="Ending column number (1-indexed)"
    )
    
    start_byte: int = Field(
        ge=0,
        description="Starting byte offset (0-indexed)"
    )
    
    end_byte: int = Field(
        ge=0,
        description="Ending byte offset (0-indexed)"
    )
    
    source_text: str = Field(
        description="The actual source code text at this location"
    )
    
    model_config = {"arbitrary_types_allowed": True}
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        location = f"line {self.start_line}, column {self.start_column}"
        if self.file_path:
            return f"{self.file_path}:{location}"
        return location
    
    def spans_multiple_lines(self) -> bool:
        """Check if this location spans multiple lines."""
        return self.start_line != self.end_line
    
    def get_length(self) -> int:
        """Get the length in bytes of this location."""
        return self.end_byte - self.start_byte
    
    def contains_position(self, line: int, column: int) -> bool:
        """
        Check if a given line/column position is within this location.
        
        Args:
            line: Line number (1-indexed)
            column: Column number (1-indexed)
            
        Returns:
            True if the position is within this location
        """
        if line < self.start_line or line > self.end_line:
            return False
        
        if line == self.start_line and column < self.start_column:
            return False
        
        if line == self.end_line and column > self.end_column:
            return False
        
        return True
    
    def overlaps_with(self, other: "SourceLocation") -> bool:
        """
        Check if this location overlaps with another location.
        
        Args:
            other: Another SourceLocation to check against
            
        Returns:
            True if the locations overlap
        """
        # Check if they're in different files
        if self.file_path and other.file_path and self.file_path != other.file_path:
            return False
        
        # Use byte positions for precise overlap detection
        return not (self.end_byte <= other.start_byte or other.end_byte <= self.start_byte)
    
    def to_dict(self) -> dict:
        """Convert to a dictionary suitable for JSON serialization."""
        return {
            "file_path": str(self.file_path) if self.file_path else None,
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line,
            "end_column": self.end_column,
            "start_byte": self.start_byte,
            "end_byte": self.end_byte,
            "source_text": self.source_text
        }