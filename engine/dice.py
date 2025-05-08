"""18-sided die for the folktale generator."""

import random
from typing import Dict, Tuple

from utils.language import Language

class D18StoryDie:
    """An 18-sided die for story progression, based on the ancient Han dynasty die."""
    
    def __init__(self):
        self.die_faces = {
            (1, 6): "character_action",
            (7, 9): "environmental_event",
            (10, 12): "object_appearance",
            (13, 15): "cosmic_intervention",
            16: "plot_twist",
            17: "wildcard",
            18: "story_ending"
        }
        
        # Bilingual action types
        self.action_types_bilingual = {
            "character_action": "角色行动",
            "environmental_event": "环境事件",
            "object_appearance": "物品出现",
            "cosmic_intervention": "天命干预",
            "plot_twist": "剧情转折",
            "wildcard": "随机组合",
            "story_ending": "故事结局"
        }
    
    def roll(self) -> Tuple[int, str]:
        """Roll the die and return (roll_number, action_type).
        
        Returns:
            A tuple containing the roll number (1-18) and the corresponding action type.
        """
        roll = random.randint(1, 18)
        
        # Check each die face range
        for face_key, action_type in self.die_faces.items():
            if isinstance(face_key, tuple):
                start, end = face_key
                if start <= roll <= end:
                    return roll, action_type
            elif roll == face_key:
                return roll, action_type
        
        # Fallback (should never reach here)
        return roll, "error"
    
    def get_action_type_bilingual(self, action_type: str, language=Language.ENGLISH) -> str:
        """Get action type in selected language.
        
        Args:
            action_type: The action type in English.
            language: The target language (CHINESE, ENGLISH, or BILINGUAL).
            
        Returns:
            The action type in the selected language format.
        """
        if language == Language.CHINESE:
            return self.action_types_bilingual.get(action_type, action_type)
        elif language == Language.BILINGUAL:
            return f"{action_type} ({self.action_types_bilingual.get(action_type, '')})"
        return action_type