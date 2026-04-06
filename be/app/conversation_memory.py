"""
Conversation Memory for FitVoice
Maintains per-session conversation history for context-aware LLM responses.
"""

from collections import defaultdict
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading


@dataclass
class Turn:
    """A single conversation turn (user question + assistant answer)."""
    user: str
    assistant: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ConversationMemory:
    """Thread-safe per-session conversation memory.
    
    Stores recent conversation turns per session_id and formats them
    for injection into the LLM prompt.
    """
    
    def __init__(self, max_turns: int = 5):
        """
        Args:
            max_turns: Maximum number of recent turns to keep per session.
                       Older turns are discarded (sliding window).
        """
        self.max_turns = max_turns
        self._sessions: Dict[str, List[Turn]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def add_turn(self, session_id: str, user_msg: str, assistant_msg: str) -> None:
        """Record a conversation turn for a session."""
        with self._lock:
            turns = self._sessions[session_id]
            turns.append(Turn(user=user_msg, assistant=assistant_msg))
            # Keep only the most recent max_turns
            if len(turns) > self.max_turns:
                self._sessions[session_id] = turns[-self.max_turns:]
    
    def get_history(self, session_id: str) -> List[Turn]:
        """Get conversation history for a session."""
        with self._lock:
            return list(self._sessions.get(session_id, []))
    
    def format_for_prompt(self, session_id: str) -> str:
        """Format conversation history as a string for LLM prompt injection.
        
        Returns an empty string if no history exists.
        """
        turns = self.get_history(session_id)
        if not turns:
            return ""
        
        lines = ["Previous conversation:"]
        for turn in turns:
            lines.append(f"User: {turn.user}")
            lines.append(f"Assistant: {turn.assistant}")
        
        return "\n".join(lines)
    
    def clear_session(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        with self._lock:
            self._sessions.pop(session_id, None)
    
    def get_session_count(self) -> int:
        """Get number of active sessions."""
        with self._lock:
            return len(self._sessions)
    
    def get_turn_count(self, session_id: str) -> int:
        """Get number of turns in a session."""
        with self._lock:
            return len(self._sessions.get(session_id, []))
