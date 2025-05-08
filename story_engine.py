import random
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pickle
import os

class StoryState:
    def __init__(self):
        self.current_turn = 0
        self.max_turns = random.randint(7, 12)
        self.active_elements = []
        self.cosmic_position = "wood"  # Starting position
        self.previous_sentence = ""
        self.narrative_thread = []
        self.story_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def to_dict(self):
        return {
            "current_turn": self.current_turn,
            "max_turns": self.max_turns,
            "active_elements": self.active_elements,
            "cosmic_position": self.cosmic_position,
            "previous_sentence": self.previous_sentence,
            "narrative_thread": self.narrative_thread,
            "story_id": self.story_id
        }
    
    @classmethod
    def from_dict(cls, data):
        state = cls()
        state.__dict__.update(data)
        return state

class D18StoryDie:
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
    
    def roll(self) -> Tuple[int, str]:
        """Returns (roll_number, action_type)"""
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

class StoryEngine:
    def __init__(self, data_path="./data"):
        self.data_path = data_path
        self.die = D18StoryDie()
        self.elements = {
            "wood": {"season": "spring", "direction": "east", "color": "green", "virtue": "benevolence", "animal": "azure dragon"},
            "fire": {"season": "summer", "direction": "south", "color": "red", "virtue": "propriety", "animal": "vermilion bird"},
            "earth": {"season": "late_summer", "direction": "center", "color": "yellow", "virtue": "trustworthiness", "animal": "yellow dragon"},
            "metal": {"season": "autumn", "direction": "west", "color": "white", "virtue": "righteousness", "animal": "white tiger"},
            "water": {"season": "winter", "direction": "north", "color": "black", "virtue": "wisdom", "animal": "black turtle"}
        }
        
        # Load data files
        self.load_data()
    
    def load_data(self):
        """Load all CSV data files into memory"""
        try:
            self.places = self._load_csv("places.csv")
            self.characters = self._load_csv("characters.csv")
            self.objects = self._load_csv("objects.csv")
            self.events = self._load_csv("events.csv")
            self.interventions = self._load_csv("interventions.csv")
            self.story_seeds = self._load_csv("story_seeds.csv")
            self.endings = self._load_csv("endings.csv")
        except FileNotFoundError as e:
            print(f"Warning: {e}")
            # Initialize empty lists for missing files
            self.places = []
            self.characters = []
            self.objects = []
            self.events = []
            self.interventions = []
            self.story_seeds = []
            self.endings = []
    
    def _load_csv(self, filename):
        """Load CSV file and return list of values"""
        import csv
        data = []
        filepath = os.path.join(self.data_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:  # Skip empty rows
                        data.append(row[0].strip('"'))  # Remove quotes if present
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            raise
        return data
    
    def get_cosmic_position(self, state: StoryState) -> str:
        """Calculate current cosmic position based on story state"""
        elements_cycle = ["wood", "fire", "earth", "metal", "water"]
        base_index = elements_cycle.index(state.cosmic_position)
        new_index = (base_index + state.current_turn) % len(elements_cycle)
        return elements_cycle[new_index]
    
    def select_elements(self, action_type: str, current_element: str) -> Dict:
        """Select appropriate elements based on action type and cosmic position"""
        element_data = self.elements[current_element]
        
        # Base selection logic - you'll customize this based on your needs
        selected = {"cosmic_element": current_element}
        
        if action_type == "character_action":
            selected["character"] = random.choice(self.characters) if self.characters else "a wandering scholar"
        elif action_type == "environmental_event":
            selected["event"] = random.choice(self.events) if self.events else "a sudden storm"
            selected["place"] = random.choice(self.places) if self.places else "a misty mountain"
        elif action_type == "object_appearance":
            selected["object"] = random.choice(self.objects) if self.objects else "an ancient bronze mirror"
        elif action_type == "cosmic_intervention":
            selected["intervention"] = random.choice(self.interventions) if self.interventions else "the heavens rumble"
        elif action_type == "wildcard":
            # Combine multiple elements for wildcard
            selected["character"] = random.choice(self.characters) if self.characters else "a mysterious figure"
            selected["object"] = random.choice(self.objects) if self.objects else "a glowing artifact"
            selected["place"] = random.choice(self.places) if self.places else "a forgotten temple"
        
        return selected
    
    def create_prompt(self, state: StoryState, elements: Dict, action_type: str) -> str:
        """Build the prompt for the LLM based on current state and elements"""
        
        prompt_base = f"""You are a storyteller of ancient Chinese folktales in the style of Han dynasty stories. 
Continue the following story with a single paragraph.

Current cosmic element: {elements['cosmic_element']} ({self.elements[elements['cosmic_element']]['season']})
Action type: {action_type}
Current turn: {state.current_turn + 1}/{state.max_turns}

Previous narrative: {state.previous_sentence}

Include these elements in your continuation:
"""
        
        for key, value in elements.items():
            if key != "cosmic_element":
                prompt_base += f"\n- {key}: {value}"
        
        prompt_base += "\n\nWrite in a style reminiscent of ancient Chinese folktales, with references to the cosmic element and its associated qualities. Keep the narrative flowing naturally from the previous sentence."
        
        return prompt_base
    
    def save_story(self, state: StoryState):
        """Save completed story to archive"""
        story_data = {
            "id": state.story_id,
            "completed_at": datetime.now().isoformat(),
            "final_narrative": state.narrative_thread,
            "cosmic_position": state.cosmic_position,
            "total_turns": state.current_turn,
            "max_turns": state.max_turns
        }
        
        # Ensure stories directory exists
        os.makedirs("./stories", exist_ok=True)
        
        filepath = f"./stories/{state.story_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(story_data, f, ensure_ascii=False, indent=2)
    
    def get_story_seed_from_previous(self, previous_story_id: str = None) -> Dict:
        """Get seed elements from the most recent story for exquisite corpse"""
        if previous_story_id is None:
            # Find most recent story
            story_files = [f for f in os.listdir("./stories") if f.endswith('.json')]
            if not story_files:
                return {"seed": random.choice(self.story_seeds) if self.story_seeds else "In ancient times..."}
            
            story_files.sort()
            previous_story_id = story_files[-1].replace('.json', '')
        
        try:
            with open(f"./stories/{previous_story_id}.json", 'r', encoding='utf-8') as f:
                previous_story = json.load(f)
            
            # Extract the last sentence and cosmic position
            if previous_story['final_narrative']:
                last_turn = previous_story['final_narrative'][-1]
                return {
                    "seed": last_turn['narrative'],
                    "cosmic_position": previous_story['cosmic_position']
                }
        except Exception as e:
            print(f"Error loading previous story: {e}")
        
        # Fallback to random seed
        return {"seed": random.choice(self.story_seeds) if self.story_seeds else "Long ago..."}