"""Main story engine for the folktale generator."""

import random
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from utils.language import Language
from engine.dice import D18StoryDie
from engine.state import StoryState
from engine.prompt import create_prompt
from cosmology.wuxing import WuXing, Element
from data.loader import load_all_data_files
from narrative.arc import StoryArc

class StoryEngine:
    """Main engine for generating Han dynasty folktales."""
    
    def __init__(self, data_path="./data"):
        """Initialize the story engine.
        
        Args:
            data_path: Path to data files directory.
        """
        self.data_path = data_path
        self.die = D18StoryDie()
        self.wuxing = WuXing()
        
        # Load data files
        self.data = load_all_data_files(data_path)
        
        # Extract data collections for easy access
        self.places = self.data.get("places", [])
        self.characters = self.data.get("characters", [])
        self.objects = self.data.get("objects", [])
        self.events = self.data.get("events", [])
        self.interventions = self.data.get("interventions", [])
        self.story_seeds = self.data.get("story_seeds", [])
        self.endings = self.data.get("endings", [])
    
    def get_cosmic_position(self, state: StoryState) -> str:
        """Calculate current cosmic position based on story state.
        
        Args:
            state: Current story state.
            
        Returns:
            Current cosmic element name.
        """
        return self.wuxing.calculate_next_position(state.cosmic_position, state.current_turn)
    
    def select_random_element(self, collection, lang=Language.ENGLISH):
        """Select a random element from collection in specified language.
        
        Args:
            collection: Collection of bilingual elements.
            lang: Language to return the element in.
            
        Returns:
            Selected element in the specified language.
        """
        if not collection:
            return None
        
        item = random.choice(collection)
        if lang == Language.CHINESE:
            return item.get("zh", "")
        elif lang == Language.ENGLISH:
            return item.get("en", "")
        else:  # BILINGUAL
            return {"zh": item.get("zh", ""), "en": item.get("en", "")}
    
    # def select_elements(self, action_type: str, current_element: str, lang=Language.ENGLISH) -> Dict:
    #     """Select appropriate elements based on action type and cosmic position in specified language.
        
    #     Args:
    #         action_type: The type of action for this turn.
    #         current_element: The current cosmic element.
    #         lang: Language to return elements in.
            
    #     Returns:
    #         Dictionary of selected story elements.
    #     """
    #     selected = {"cosmic_element": current_element}
        
    #     if action_type == "character_action":
    #         character = self.select_random_element(self.characters, lang)
    #         selected["character"] = character or "a wandering scholar"
    #     elif action_type == "environmental_event":
    #         event = self.select_random_element(self.events, lang)
    #         place = self.select_random_element(self.places, lang)
    #         selected["event"] = event or "a sudden storm"
    #         selected["place"] = place or "a misty mountain"
    #     elif action_type == "object_appearance":
    #         object_item = self.select_random_element(self.objects, lang)
    #         selected["object"] = object_item or "an ancient bronze mirror"
    #     elif action_type == "cosmic_intervention":
    #         intervention = self.select_random_element(self.interventions, lang)
    #         selected["intervention"] = intervention or "the heavens rumble"
    #     elif action_type == "wildcard":
    #         # Combine multiple elements for wildcard
    #         character = self.select_random_element(self.characters, lang)
    #         object_item = self.select_random_element(self.objects, lang)
    #         place = self.select_random_element(self.places, lang)
    #         selected["character"] = character or "a mysterious figure"
    #         selected["object"] = object_item or "a glowing artifact"
    #         selected["place"] = place or "a forgotten temple"
        
    #     return selected


    def select_elements(self, action_type: str, current_element: str, lang=Language.ENGLISH) -> Dict:
        """Select appropriate elements with special handling for central objects."""
        selected = {"cosmic_element": current_element}
        
        if action_type == "character_action":
            character = self.select_random_element(self.characters, lang)
            selected["character"] = character or "a curious child"
        elif action_type == "environmental_event":
            event = self.select_random_element(self.events, lang)
            place = self.select_random_element(self.places, lang)
            selected["event"] = event or "a gentle breeze"
            selected["place"] = place or "a beautiful garden"
        elif action_type == "object_appearance":
            # For object appearance, always use the Han dynasty artifacts
            object_item = self.select_random_element(self.objects, lang)
            selected["object"] = object_item or "a magical Han dynasty artifact"
            # Add a flag to indicate this object should be central
            selected["object_is_central"] = True
        elif action_type == "cosmic_intervention":
            intervention = self.select_random_element(self.interventions, lang)
            selected["intervention"] = intervention or "a friendly spirit appears"
        elif action_type == "wildcard":
            # In wildcard, if an object appears, make it central too
            character = self.select_random_element(self.characters, lang)
            object_item = self.select_random_element(self.objects, lang)
            place = self.select_random_element(self.places, lang)
            selected["character"] = character or "a helpful friend"
            selected["object"] = object_item or "a magical toy"
            selected["place"] = place or "a peaceful temple"
            selected["object_is_central"] = True  # Objects in wildcard should also be central
        
        return selected
    
    def build_prompt(self, state: StoryState, elements: Dict, action_type: str) -> str:
        """Create a prompt for the story generation."""
        prompt = create_prompt(state, elements, action_type, self.wuxing)
        
        # Add explicit instruction to avoid repetition
        if state.language == Language.CHINESE:
            prompt += "\n\n重要: 不要重复前面的内容，只需继续故事情节。提供全新的叙述，将故事向前推进。"
        elif state.language == Language.ENGLISH:
            prompt += "\n\nIMPORTANT: Do not repeat the previous content. Only continue the story with new narrative that advances the plot."
        else:  # BILINGUAL
            prompt += "\n\nIMPORTANT: Do not repeat the previous content. Only continue the story with new narrative that advances the plot in both languages."
        
        return prompt
    
    def save_story(self, state: StoryState):
        """Save completed story to archive.
        
        Args:
            state: Story state to save.
        """
        story_data = {
            "id": state.story_id,
            "completed_at": datetime.now().isoformat(),
            "final_narrative": state.narrative_thread,
            "cosmic_position": state.cosmic_position,
            "total_turns": state.current_turn,
            "max_turns": state.max_turns,
            "language": state.language,
            "story_arc": {
                "type": state.story_arc.arc_type,
                "stages": state.story_arc.stages,
                "theme_elements": state.story_arc.theme_elements,
                "current_stage": state.story_arc.get_current_stage(Language.ENGLISH)
            }
        }
        
        # Ensure stories directory exists
        os.makedirs("./stories", exist_ok=True)
        
        filepath = f"./stories/{state.story_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(story_data, f, ensure_ascii=False, indent=2)
    
    def get_story_seed_from_previous(self, previous_story_id: str = None) -> Dict:
        """Get seed elements from the most recent story for exquisite corpse.
        
        Args:
            previous_story_id: ID of a previous story to build from.
            
        Returns:
            Dictionary with seed text and cosmic position.
        """
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
    
    def create_opening_prompt(self, state: StoryState) -> str:
        """Create a prompt for story opening.
        
        Args:
            state: Current story state.
            
        Returns:
            Opening prompt for the language model.
        """
        lang = state.language
        
        if lang == Language.CHINESE:
            return f"""为孩子们创作一个温暖的中国古代故事，以这个开头开始: "{state.previous_sentence_zh}"

            故事结构: {state.story_arc.arc_data['description_zh']}
            当前阶段: {state.story_arc.get_current_stage(lang)}
            阶段指导: {state.story_arc.get_stage_guidance(lang)}
            {state.story_arc.get_related_literature(lang)}
            {state.story_arc.get_motifs(lang)}

            这是一个发生在古代中国的儿童故事，应该包含传统文化元素但要适合孩子们理解。
            
            要求:
            - 只写一个温暖的叙述段落(2-3句话)，充满童趣和想象力
            - 直接开始故事情节，让孩子们感受到古代中国的美好
            - 体现{self.wuxing.get_element_text(state.cosmic_position, Language.CHINESE)}元素的美好特质
            - 使用古代中国文化背景，但要让现代儿童也能理解和喜爱
            - 营造温馨、神奇的氛围

            现在请开始这个美好的故事:"""
        elif lang == Language.ENGLISH:
            return f"""Begin a new Han dynasty Chinese folktale based on this opening: "{state.previous_sentence}"

            Story arc: {state.story_arc.arc_data['description']}
            Current stage: {state.story_arc.get_current_stage(lang)}
            Stage guidance: {state.story_arc.get_stage_guidance(lang)}
            {state.story_arc.get_related_literature(lang)}
            {state.story_arc.get_motifs(lang)}

            The story takes place during the Han dynasty and should incorporate elements of traditional Chinese cosmology. 
            Start with the cosmic element of {state.cosmic_position}. 
            Write an engaging opening paragraph that appropriately introduces the first stage of the story."""
        else:  # BILINGUAL
            return f"""Create a new Han dynasty Chinese folktale in BOTH Chinese and English. First write in Chinese, then provide its English translation.

            Chinese opening line: "{state.previous_sentence_zh}"
            English opening line: "{state.previous_sentence}"

            Story arc: {state.story_arc.arc_data['description']} / {state.story_arc.arc_data['description_zh']}
            Current stage: {state.story_arc.get_current_stage(lang)}
            Stage guidance: 
            - Chinese: {state.story_arc.get_stage_guidance(Language.CHINESE)}
            - English: {state.story_arc.get_stage_guidance(Language.ENGLISH)}
            {state.story_arc.get_related_literature(lang)}
            {state.story_arc.get_motifs(lang)}

            The story takes place during the Han dynasty (汉代) and should incorporate elements of traditional Chinese cosmology.
            Start with the cosmic element of {state.cosmic_position} ({self.wuxing.get_element_text(state.cosmic_position, Language.CHINESE)}).
                    
            Write an engaging opening paragraph in Chinese first, followed by its English translation. The opening should appropriately introduce the first stage of the story arc."""

    def create_ending_prompt(self, state: StoryState, current_element: str) -> str:
        """Create a prompt for story ending.
        
        Args:
            state: Current story state.
            current_element: Current cosmic element.
            
        Returns:
            Ending prompt for the language model.
        """
        lang = state.language
        
        if lang == Language.CHINESE:
            return f"""为这个温暖的儿童故事写一个美好的结局。
            故事围绕着{self.wuxing.get_element_text(current_element, Language.CHINESE)}元素展开。
            前一段落: {state.previous_sentence_zh}
            请写一个让孩子们感到快乐和满足的结局，将故事中的美好主题联系起来。
            结局应该充满温暖、智慧和正能量，让小朋友们感受到故事的美好寓意。"""
        elif lang == Language.ENGLISH:
            return f"""Complete this Chinese folktale with a fitting conclusion. 
            The story has taken place in the cosmic element of {current_element}. 
            Previous narrative: {state.previous_sentence}
            Write a satisfying ending that ties together the themes and elements introduced."""
        else:  # BILINGUAL
            return f"""Complete this Chinese folktale with a fitting conclusion in BOTH Chinese and English.
            
            The story has taken place in the cosmic element of {current_element} ({self.wuxing.get_element_text(current_element, Language.CHINESE)}).
            
            Previous Chinese narrative: {state.previous_sentence_zh}
            Previous English narrative: {state.previous_sentence}
            
            Write a satisfying ending that ties together the themes and elements introduced.
            First write the conclusion in Chinese, then provide its English translation."""
    
    def should_end_story(self, state: StoryState, roll: int) -> bool:
        """Determine if the story should end.
        
        Args:
            state: Current story state.
            roll: Current die roll.
            
        Returns:
            True if story should end, False otherwise.
        """
        # End on die roll of 18
        if roll == 18:
            return True
        
        # End when max turns reached
        if state.current_turn >= state.max_turns:
            return True
            
        # End if we've completed all stages of the arc
        if state.story_arc.current_stage_index >= len(state.story_arc.stages) - 1:
            # Only end if we've spent enough time in the final stage
            final_stage_turns = state.current_turn - sum(state.story_arc.stage_turns[:-1])
            if final_stage_turns >= state.story_arc.stage_turns[-1]:
                return True
        
        return False