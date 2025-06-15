"""Story state management for the folktale generator."""

import random
from datetime import datetime
from typing import Dict, List, Optional

from utils.language import Language
from narrative.arc import StoryArc

class StoryState:
    """Tracks the state of a story throughout its generation process."""
    
    def __init__(self, language=Language.ENGLISH):
        """Initialize a new story state.
        
        Args:
            language: The language to use for this story (CHINESE, ENGLISH, or BILINGUAL).
        """
        self.current_turn = 0
        self.max_turns = random.randint(5, 8)
        self.active_elements = []
        self.cosmic_position = "wood"  # Starting position
        self.previous_sentence = ""
        self.previous_sentence_zh = ""  # Chinese version
        self.narrative_thread = []
        self.story_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.language = language
        
        # Initialize story arc
        self.story_arc = StoryArc(max_turns=self.max_turns)
    
    def to_dict(self) -> Dict:
        """Convert the state to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the story state.
        """
        return {
            "current_turn": self.current_turn,
            "max_turns": self.max_turns,
            "active_elements": self.active_elements,
            "cosmic_position": self.cosmic_position,
            "previous_sentence": self.previous_sentence,
            "previous_sentence_zh": self.previous_sentence_zh,
            "narrative_thread": self.narrative_thread,
            "story_id": self.story_id,
            "language": self.language,
            "story_arc": self.story_arc.to_dict() if self.story_arc else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create a StoryState from a dictionary.
        
        Args:
            data: Dictionary containing story state data.
            
        Returns:
            A new StoryState instance with the provided data.
        """
        state = cls()
        # Handle story arc separately
        arc_data = data.pop("story_arc", None)
        state.__dict__.update(data)
        if arc_data:
            state.story_arc = StoryArc.from_dict(arc_data)
        return state
    
    def add_narrative(self, narrative: str, narrative_zh: str = None, 
                     turn_data: Dict = None) -> None:
        """Add a narrative segment to the story thread.
        
        Args:
            narrative: The narrative text in English.
            narrative_zh: Optional narrative text in Chinese.
            turn_data: Additional data for this turn such as roll, action_type, elements.
        """
        if turn_data is None:
            turn_data = {}
        
        # Create a new turn entry
        turn_entry = {
            "turn": self.current_turn,
            "narrative": narrative,
            **turn_data
        }
        
        # Add Chinese narrative if provided
        if narrative_zh:
            turn_entry["narrative_zh"] = narrative_zh
        
        # Add to narrative thread
        self.narrative_thread.append(turn_entry)
        
        # Update previous sentence(s)
        self.previous_sentence = narrative
        if narrative_zh:
            self.previous_sentence_zh = narrative_zh