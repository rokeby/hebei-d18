import random
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pickle
import os

# Language enumeration
class Language:
    CHINESE = "zh"
    ENGLISH = "en"
    BILINGUAL = "both"

class StoryState:
    def __init__(self, language=Language.ENGLISH):
        self.current_turn = 0
        self.max_turns = random.randint(7, 12)
        self.active_elements = []
        self.cosmic_position = "wood"  # Starting position
        self.previous_sentence = ""
        self.previous_sentence_zh = ""  # Chinese version
        self.narrative_thread = []
        self.story_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.language = language
        
    def to_dict(self):
        return {
            "current_turn": self.current_turn,
            "max_turns": self.max_turns,
            "active_elements": self.active_elements,
            "cosmic_position": self.cosmic_position,
            "previous_sentence": self.previous_sentence,
            "previous_sentence_zh": self.previous_sentence_zh,
            "narrative_thread": self.narrative_thread,
            "story_id": self.story_id,
            "language": self.language
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
    
    def get_action_type_bilingual(self, action_type, language=Language.ENGLISH):
        """Get action type in selected language"""
        if language == Language.CHINESE:
            return self.action_types_bilingual.get(action_type, action_type)
        elif language == Language.BILINGUAL:
            return f"{action_type} ({self.action_types_bilingual.get(action_type, '')})"
        return action_type

class StoryEngine:
    def __init__(self, data_path="./data", language=Language.ENGLISH):
        self.data_path = data_path
        self.die = D18StoryDie()
        self.language = language
        
        # Bilingual elements
        self.elements = {
            "wood": {
                "en": {"season": "spring", "direction": "east", "color": "green", "virtue": "benevolence", "animal": "azure dragon"},
                "zh": {"season": "春", "direction": "东", "color": "青", "virtue": "仁", "animal": "青龙"}
            },
            "fire": {
                "en": {"season": "summer", "direction": "south", "color": "red", "virtue": "propriety", "animal": "vermilion bird"},
                "zh": {"season": "夏", "direction": "南", "color": "赤", "virtue": "礼", "animal": "朱雀"}
            },
            "earth": {
                "en": {"season": "late summer", "direction": "center", "color": "yellow", "virtue": "trustworthiness", "animal": "yellow dragon"},
                "zh": {"season": "长夏", "direction": "中", "color": "黄", "virtue": "信", "animal": "黄龙"}
            },
            "metal": {
                "en": {"season": "autumn", "direction": "west", "color": "white", "virtue": "righteousness", "animal": "white tiger"},
                "zh": {"season": "秋", "direction": "西", "color": "白", "virtue": "义", "animal": "白虎"}
            },
            "water": {
                "en": {"season": "winter", "direction": "north", "color": "black", "virtue": "wisdom", "animal": "black turtle"},
                "zh": {"season": "冬", "direction": "北", "color": "黑", "virtue": "智", "animal": "玄武"}
            }
        }
        
        # Element names in Chinese
        self.element_names_zh = {
            "wood": "木",
            "fire": "火",
            "earth": "土",
            "metal": "金",
            "water": "水"
        }
        
        # Load data files
        self.load_data()
    
    def load_data(self):
        """Load all CSV data files into memory as bilingual pairs"""
        try:
            self.places = self._load_bilingual_csv("places.csv")
            self.characters = self._load_bilingual_csv("characters.csv")
            self.objects = self._load_bilingual_csv("objects.csv")
            self.events = self._load_bilingual_csv("events.csv")
            self.interventions = self._load_bilingual_csv("interventions.csv")
            self.story_seeds = self._load_bilingual_csv("story_seeds.csv")
            self.endings = self._load_bilingual_csv("endings.csv")
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
    
    def _load_bilingual_csv(self, filename):
        """Load CSV file and return list of bilingual pairs (zh, en)"""
        import csv
        data = []
        filepath = os.path.join(self.data_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:  # Ensure we have both languages
                        zh = row[0].strip('"')
                        en = row[1].strip('"')
                        data.append({"zh": zh, "en": en})
                    elif len(row) == 1:  # Handle single language entries
                        item = row[0].strip('"')
                        data.append({"zh": item, "en": item})
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            raise
        return data
    
    def get_element_text(self, element: str, lang=Language.ENGLISH):
        """Get element properties in specified language"""
        if lang == Language.CHINESE:
            return self.element_names_zh.get(element, element)
        elif lang == Language.BILINGUAL:
            return f"{element} ({self.element_names_zh.get(element, '')})"
        return element
    
    def get_element_properties(self, element: str, lang=Language.ENGLISH):
        """Get element properties in specified language"""
        lang_key = "zh" if lang == Language.CHINESE else "en"
        if lang == Language.BILINGUAL:
            zh_props = self.elements[element]["zh"]
            en_props = self.elements[element]["en"]
            return {
                "season": f"{en_props['season']} ({zh_props['season']})",
                "direction": f"{en_props['direction']} ({zh_props['direction']})",
                "color": f"{en_props['color']} ({zh_props['color']})",
                "virtue": f"{en_props['virtue']} ({zh_props['virtue']})",
                "animal": f"{en_props['animal']} ({zh_props['animal']})"
            }
        return self.elements[element][lang_key]
    
    def get_cosmic_position(self, state: StoryState) -> str:
        """Calculate current cosmic position based on story state"""
        elements_cycle = ["wood", "fire", "earth", "metal", "water"]
        base_index = elements_cycle.index(state.cosmic_position)
        new_index = (base_index + state.current_turn) % len(elements_cycle)
        return elements_cycle[new_index]
    
    def select_random_element(self, collection, lang=Language.ENGLISH):
        """Select a random element from collection in specified language"""
        if not collection:
            return None
        
        item = random.choice(collection)
        if lang == Language.CHINESE:
            return item.get("zh", "")
        elif lang == Language.ENGLISH:
            return item.get("en", "")
        else:  # BILINGUAL
            return {"zh": item.get("zh", ""), "en": item.get("en", "")}
    
    def select_elements(self, action_type: str, current_element: str, lang=Language.ENGLISH) -> Dict:
        """Select appropriate elements based on action type and cosmic position in specified language"""
        selected = {"cosmic_element": current_element}
        
        if action_type == "character_action":
            character = self.select_random_element(self.characters, lang)
            selected["character"] = character or "a wandering scholar"
        elif action_type == "environmental_event":
            event = self.select_random_element(self.events, lang)
            place = self.select_random_element(self.places, lang)
            selected["event"] = event or "a sudden storm"
            selected["place"] = place or "a misty mountain"
        elif action_type == "object_appearance":
            object_item = self.select_random_element(self.objects, lang)
            selected["object"] = object_item or "an ancient bronze mirror"
        elif action_type == "cosmic_intervention":
            intervention = self.select_random_element(self.interventions, lang)
            selected["intervention"] = intervention or "the heavens rumble"
        elif action_type == "wildcard":
            # Combine multiple elements for wildcard
            character = self.select_random_element(self.characters, lang)
            object_item = self.select_random_element(self.objects, lang)
            place = self.select_random_element(self.places, lang)
            selected["character"] = character or "a mysterious figure"
            selected["object"] = object_item or "a glowing artifact"
            selected["place"] = place or "a forgotten temple"
        
        return selected
    
    def create_prompt(self, state: StoryState, elements: Dict, action_type: str) -> str:
        """Build the prompt for the LLM based on current state and elements"""
        lang = state.language
        cosmic_element = elements["cosmic_element"]
        
        # Get element properties in appropriate language
        element_props = self.get_element_properties(cosmic_element, lang)
        element_name = self.get_element_text(cosmic_element, lang)
        action_type_text = self.die.get_action_type_bilingual(action_type, lang)
        
        # Build base prompt
        if lang == Language.CHINESE:
            prompt_base = f"""

            你是一位讲述汉代民间故事的故事家。
            请继续以下故事，用一个简短的段落。

            当前五行元素: {element_name} (季节: {element_props['season']}, 方向: {element_props['direction']}, 颜色: {element_props['color']})
            动作类型: {action_type_text}
            当前回合: {state.current_turn + 1}/{state.max_turns}

            前一段落: {state.previous_sentence_zh}

            请在你的叙述中包含以下元素:
            """
        elif lang == Language.ENGLISH:
                        prompt_base = f"""You are a storyteller of ancient Chinese folktales from the Han dynasty period.
            Continue the following story with a single paragraph.

            Current cosmic element: {element_name} (season: {element_props['season']}, direction: {element_props['direction']}, color: {element_props['color']})
            Action type: {action_type_text}
            Current turn: {state.current_turn + 1}/{state.max_turns}

            Previous narrative: {state.previous_sentence}

            Include these elements in your continuation:
            """
        else:  # BILINGUAL
            prompt_base = f"""You are a master storyteller of Han dynasty folktales. Your task is to continue a story in BOTH Chinese and English.
                        First write a paragraph in Chinese, then provide its English translation.

                        Current cosmic element: {element_name}
                        Season: {element_props['season']}
                        Direction: {element_props['direction']}
                        Color: {element_props['color']}
                        Virtue: {element_props['virtue']}
                        Celestial animal: {element_props['animal']}

                        Action type: {action_type_text}
                        Current turn: {state.current_turn + 1}/{state.max_turns}

                        Previous Chinese narrative: {state.previous_sentence_zh}
                        Previous English narrative: {state.previous_sentence}

                        Include these elements in your continuation:
                        """
        
        # Add elements based on language
        for key, value in elements.items():
            if key != "cosmic_element":
                if isinstance(value, dict) and "zh" in value and "en" in value:
                    if lang == Language.CHINESE:
                        prompt_base += f"\n- {key}: {value['zh']}"
                    elif lang == Language.ENGLISH:
                        prompt_base += f"\n- {key}: {value['en']}"
                    else:  # BILINGUAL
                        prompt_base += f"\n- {key}: {value['zh']} / {value['en']}"
                else:
                    prompt_base += f"\n- {key}: {value}"
        
        # Add style instructions
        if lang == Language.CHINESE:
            prompt_base += "\n\n请以古代汉代民间故事的风格写作，引用五行元素的特质。文风应富有神秘感和古风韵味。请保持叙事自然流畅。"
        elif lang == Language.ENGLISH:
            prompt_base += "\n\nWrite in a style reminiscent of ancient Chinese folktales, with references to the cosmic element and its associated qualities. Keep the narrative flowing naturally from the previous sentence."
        else:  # BILINGUAL
            prompt_base += "\n\nFormat your response with the Chinese paragraph first, followed by its English translation. Write in a style authentic to Han dynasty folklore, mentioning the cosmic element qualities. Keep the narrative flowing naturally."
            prompt_base += "\n\nVERY IMPORTANT: Your response MUST contain BOTH Chinese and English versions. First write in Chinese, then provide the English translation. Make sure both tell the same story but are culturally appropriate in each language."
        
        return prompt_base
    
    def parse_bilingual_response(self, response: str) -> Dict[str, str]:
        """Parse a bilingual response to extract Chinese and English parts"""
        # Simple parsing strategy - try to detect Chinese vs English
        lines = response.strip().split('\n')
        chinese_text = []
        english_text = []
        current_section = "zh"  # Start with Chinese assumption
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains mostly Chinese characters
            chinese_char_count = sum(1 for char in line if '\u4e00' <= char <= '\u9fff')
            is_chinese = chinese_char_count > len(line) * 0.5
            
            # Detect section change based on character composition
            if current_section == "zh" and not is_chinese:
                current_section = "en"
            
            # Add to appropriate section
            if current_section == "zh":
                chinese_text.append(line)
            else:
                english_text.append(line)
        
        return {
            "zh": "\n".join(chinese_text),
            "en": "\n".join(english_text)
        }
    
    def save_story(self, state: StoryState):
        """Save completed story to archive"""
        story_data = {
            "id": state.story_id,
            "completed_at": datetime.now().isoformat(),
            "final_narrative": state.narrative_thread,
            "cosmic_position": state.cosmic_position,
            "total_turns": state.current_turn,
            "max_turns": state.max_turns,
            "language": state.language
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
                seed = self.select_random_element(self.story_seeds) if self.story_seeds else "In ancient times..."
                return {"seed": seed, "seed_zh": seed.get("zh", seed) if isinstance(seed, dict) else seed}
            
            story_files.sort()
            previous_story_id = story_files[-1].replace('.json', '')
        
        try:
            with open(f"./stories/{previous_story_id}.json", 'r', encoding='utf-8') as f:
                previous_story = json.load(f)
            
            # Extract the last sentence and cosmic position
            if previous_story.get('final_narrative'):
                last_turn = previous_story['final_narrative'][-1]
                return {
                    "seed": last_turn.get('narrative', "Long ago..."),
                    "seed_zh": last_turn.get('narrative_zh', "很久以前..."),
                    "cosmic_position": previous_story.get('cosmic_position', "wood")
                }
        except Exception as e:
            print(f"Error loading previous story: {e}")
        
        # Fallback to random seed
        seed = self.select_random_element(self.story_seeds) if self.story_seeds else "Long ago..."
        return {"seed": seed, "seed_zh": seed.get("zh", seed) if isinstance(seed, dict) else seed}



