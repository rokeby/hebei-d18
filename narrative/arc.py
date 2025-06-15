"""Story arc definitions and management for folktale generator."""

import random
from typing import Dict, List, Optional

from utils.language import Language

class StoryArc:
    """Tracks and manages the overall narrative arc of a story with authentic Han dynasty elements."""
    
    # Han dynasty folktale arcs based on traditional Chinese narrative structures
    ARC_TYPES = {
        # "quest": {
        #     "stages": ["departure", "challenge", "revelation", "return", "transformation"],
        #     "zh_stages": ["离开", "挑战", "启示", "归来", "转变"],
        #     "description": "A hero embarks on a journey, faces trials, gains wisdom, and returns transformed",
        #     "description_zh": "主人公踏上旅程，面对考验，获得智慧，最终转变归来",
        #     "related_text": "《穆天子传》《西游记》",
        #     "typical_motifs": ["jade talisman", "guardian spirit", "celestial guidance", "divine test"]
        # },
        # "moral_lesson": {
        #     "stages": ["harmony", "transgression", "consequence", "realization", "atonement"],
        #     "zh_stages": ["和谐", "违背", "后果", "顿悟", "赎罪"],
        #     "description": "An initial state of balance is disrupted by a moral failing, leading to consequences before wisdom is gained",
        #     "description_zh": "初始平衡被道德失误打破，引发后果，最终通过自省赎罪",
        #     "related_text": "《孔子家语》《孟子》《荀子》",
        #     "typical_motifs": ["filial piety", "social hierarchy", "ritual propriety", "moral cultivation"]
        # },
        # "cosmic_balance": {
        #     "stages": ["order", "disruption", "chaos", "intervention", "new_order"],
        #     "zh_stages": ["秩序", "破坏", "混乱", "干预", "新秩序"],
        #     "description": "Cosmic forces become imbalanced, causing chaos until divine intervention establishes a new order",
        #     "description_zh": "宇宙力量失衡，引发混乱，直到神圣干预建立新秩序",
        #     "related_text": "《淮南子》《黄帝内经》《周易》",
        #     "typical_motifs": ["five elements", "yin-yang imbalance", "celestial omens", "natural disasters"]
        # },
        # "transformation": {
        #     "stages": ["ordinary", "encounter", "change", "challenge", "transcendence"],
        #     "zh_stages": ["平凡", "遭遇", "变化", "考验", "超越"],
        #     "description": "An ordinary being encounters supernatural forces and undergoes profound transformation",
        #     "description_zh": "普通存在遇到超自然力量，经历深刻变化",
        #     "related_text": "《搜神记》《山海经》",
        #     "typical_motifs": ["jade artifacts", "immortal peaches", "animal spirits", "cinnabar elixir"]
        # },
        # "origin_myth": {
        #     "stages": ["void", "creation", "conflict", "resolution", "explanation"],
        #     "zh_stages": ["虚空", "创造", "冲突", "解决", "解释"],
        #     "description": "Explains how an important aspect of the world came to be through divine/mythic events",
        #     "description_zh": "通过神话事件解释世界重要方面的起源",
        #     "related_text": "《山海经》《淮南子·天文训》",
        #     "typical_motifs": ["primordial chaos", "divine siblings", "cosmic eggs", "celestial separation"]
        # },
        # "ancestral_vengeance": {
        #     "stages": ["injustice", "suffering", "divine_sign", "retribution", "ancestral_peace"],
        #     "zh_stages": ["冤屈", "苦难", "天兆", "报应", "安灵"],
        #     "description": "The unjustly dead seek justice through supernatural intervention in mortal affairs",
        #     "description_zh": "冤死者通过超自然干预寻求正义，最终得到安息",
        #     "related_text": "《聊斋志异》《子不语》",
        #     "typical_motifs": ["vengeful ghost", "dream warning", "ancestral tablet", "blood oath"]
        # },
        # "bureaucratic_trial": {
        #     "stages": ["mortal_case", "underworld_appeal", "divine_judgment", "cosmic_record", "karmic_resolution"],
        #     "zh_stages": ["阳案", "阴诉", "神判", "天录", "果报"],
        #     "description": "Mortal affairs are reviewed by the celestial and underworld bureaucracy for karmic balance",
        #     "description_zh": "人间事务被冥界和天庭官僚审查，以求业力平衡",
        #     "related_text": "《太平广记》《冥祥记》",
        #     "typical_motifs": ["ledger of life and death", "underworld court", "Judge Bao", "karmic retribution"]
        # }

       "friendship_journey": {
        "stages": ["meeting", "misunderstanding", "adventure", "understanding", "celebration"],
        "zh_stages": ["相遇", "误会", "冒险", "理解", "庆祝"],
        "description": "New friends overcome misunderstandings through shared adventures and learn about each other",
        "description_zh": "新朋友通过共同冒险克服误会，互相了解",
        "related_text": "《论语·学而》《孟子·公孙丑》",
        "typical_motifs": ["magical animal friend", "helping others", "teamwork", "festival celebration"]
        },

        "kind_deed_reward": {
            "stages": ["daily_life", "kind_action", "unexpected_result", "magical_help", "happy_ending"],
            "zh_stages": ["日常生活", "善行", "意外结果", "神奇帮助", "美好结局"],
            "description": "A child's small act of kindness leads to magical rewards and teaches about helping others",
            "description_zh": "孩子的小小善举带来神奇回报，教导帮助他人的道理",
            "related_text": "《二十四孝》《三字经》",
            "typical_motifs": ["talking animals", "magical objects", "helping elders", "nature spirits"]
        },
        "festival_adventure": {
            "stages": ["preparation", "problem", "creative_solution", "community_help", "joyful_festival"],
            "zh_stages": ["准备", "问题", "创意解决", "社区帮助", "欢乐节日"],
            "description": "Children work together to save a festival celebration and bring joy to their village",
            "description_zh": "孩子们齐心协力拯救节日庆典，为村庄带来欢乐",
            "related_text": "《岁时记》《风土记》",
            "typical_motifs": ["lantern festival", "dragon dance", "moon cakes", "spring festival"]
        },
        "learning_wisdom": {
            "stages": ["curiosity", "seeking_teacher", "funny_lessons", "practice", "sharing_knowledge"],
            "zh_stages": ["好奇心", "寻找老师", "有趣课程", "练习", "分享知识"],
            "description": "A curious child learns important life lessons through humorous adventures with a wise teacher",
            "description_zh": "好奇的孩子通过与智慧老师的趣味冒险学习重要的人生道理",
            "related_text": "《千字文》《百家姓》",
            "typical_motifs": ["wise panda", "magic paintbrush", "flying kite", "ancient library"]
        },
        "nature_harmony": {
            "stages": ["discovery", "imbalance", "understanding", "cooperation", "restoration"],
            "zh_stages": ["发现", "失衡", "理解", "合作", "恢复"],
            "description": "Children discover how to live in harmony with nature through magical encounters",
            "description_zh": "孩子们通过神奇邂逅发现如何与自然和谐相处",
            "related_text": "《山海经》童话版",
            "typical_motifs": ["guardian animals", "seasonal changes", "magical plants", "rainbow bridge"]
        },
        "brave_little_hero": {
            "stages": ["ordinary_day", "small_challenge", "finding_courage", "clever_solution", "growing_up"],
            "zh_stages": ["平凡一天", "小挑战", "寻找勇气", "聪明解决", "成长"],
            "description": "A small child finds courage to face everyday challenges and grows more confident",
            "description_zh": "小孩子找到勇气面对日常挑战，变得更加自信",
            "related_text": "《成语故事》《寓言故事》",
            "typical_motifs": ["helpful dragon", "magic jade pendant", "wise grandfather", "bamboo forest"]
        }
    }
    
    def __init__(self, arc_type=None, max_turns=10):
        """Initialize a story arc of a specific type or random if none specified.
        
        Args:
            arc_type: The type of story arc to use (e.g., "quest", "moral_lesson").
            max_turns: Maximum number of turns expected in the story.
        """
        if arc_type is None or arc_type not in self.ARC_TYPES:
            arc_type = random.choice(list(self.ARC_TYPES.keys()))
        
        self.arc_type = arc_type
        self.arc_data = self.ARC_TYPES[arc_type]
        self.stages = self.arc_data["stages"]
        self.zh_stages = self.arc_data["zh_stages"]
        self.current_stage_index = 0
        self.max_turns = max_turns
        self.stage_triggers = {}  # Will store event types that should trigger stage advancement
        self.theme_elements = {}  # Will store recurring elements for thematic unity
        self.motifs = random.sample(self.arc_data.get("typical_motifs", []), min(2, len(self.arc_data.get("typical_motifs", []))))
        
        # Set up each stage to occupy roughly equal portion of the story's max_turns
        self.stage_turns = self._calculate_stage_turns(max_turns, len(self.stages))
        
        # Select theme elements that should recur throughout the story
        self._select_theme_elements()
        
        # Set up appropriate stage triggers based on arc type
        self._setup_stage_triggers()
    
    def _calculate_stage_turns(self, max_turns, num_stages):
        """Calculate how many turns each stage should take.
        
        Args:
            max_turns: Maximum number of turns in the story.
            num_stages: Number of stages in the arc.
            
        Returns:
            A list with the number of turns allocated to each stage.
        """
        base_turns = max_turns // num_stages
        remainder = max_turns % num_stages
        
        # Distribute turns, giving extra turns to middle stages for more development
        stage_turns = [base_turns] * num_stages
        
        # Add remainder turns to middle stages
        middle_start = num_stages // 3
        middle_end = num_stages - middle_start
        for i in range(remainder):
            idx = (middle_start + i) % (middle_end - middle_start) + middle_start
            stage_turns[idx] += 1
            
        return stage_turns
    
    def _select_theme_elements(self):
        """Select recurring elements based on arc type for thematic unity."""
        # Implementation for each arc type's theme elements
        # Each arc type gets specific theme elements selected

        if self.arc_type == "friendship_journey":
            self._select_quest_themes()
        elif self.arc_type == "kind_deed_reward":
            self._select_moral_themes()
        elif self.arc_type == "festival_adventure":
            self._select_cosmic_themes()
        elif self.arc_type == "learning_wisdom":
            self._select_transformation_themes()
        elif self.arc_type == "origin_myth":
            self._select_origin_themes()
        elif self.arc_type == "nature_harmony":
            self._select_vengeance_themes()
        elif self.arc_type == "brave_little_hero":
            self._select_trial_themes()

        # if self.arc_type == "friendship_journey":
        #     self._select_quest_themes()
        # elif self.arc_type == "moral_lesson":
        #     self._select_moral_themes()
        # elif self.arc_type == "festival_adventure":
        #     self._select_cosmic_themes()
        # elif self.arc_type == "learning_wisdom":
        #     self._select_transformation_themes()
        # elif self.arc_type == "origin_myth":
        #     self._select_origin_themes()
        # elif self.arc_type == "nature_harmony":
        #     self._select_vengeance_themes()
        # elif self.arc_type == "brave_little_hero":
        #     self._select_trial_themes()



    def _select_quest_themes(self):
        """Child-friendly themes for friendship journey arcs"""
        self.theme_elements["obstacle_type"] = random.choice([
            "a winding river", "a misty mountain", "a dark forest", "a forgotten path"
        ])
        self.theme_elements["virtue_tested"] = random.choice([
            "cooperation", "kindness", "patience", "trust", "helpfulness"
        ])
        self.theme_elements["quest_object"] = random.choice([
            "a lost lantern", "a special festival drum", "grandmother's recipe", 
            "a phoenix feather", "a mooncake mold"
        ])

    def _select_moral_themes(self):
        """Simplified themes for moral lessons"""
        self.theme_elements["virtue"] = random.choice([
            "kindness (善)", "sharing (分享)", "honesty (诚)", "respect (敬)", "gratitude (谢)"
        ])
        self.theme_elements["transgression"] = random.choice([
            "hurting feelings", "being selfish", "breaking a promise", 
            "littering", "not sharing"
        ])
        self.theme_elements["moral_authority"] = random.choice([
            "wise grandmother", "village teacher", "kind monk", 
            "moon rabbit", "talking panda"
        ])

    def _select_cosmic_themes(self):
        """Festival-themed adventures"""
        self.theme_elements["festival_element"] = random.choice([
            "Lantern Festival", "Moon Festival", "Dragon Boat Race", 
            "Spring Celebration", "Harvest Parade"
        ])
        self.theme_elements["disruption"] = random.choice([
            "missing ingredient", "lost musical instrument", "confused directions",
            "broken decoration", "forgotten tradition"
        ])
        self.theme_elements["festival_helper"] = random.choice([
            "dancing lion", "kind spirit", "talking moon", "helpful river", "wise old tortoise"
        ])

    def _select_transformation_themes(self):
        """Wisdom-focused transformations"""
        self.theme_elements["lesson_learned"] = random.choice([
            "valuing honesty", "sharing with others", "asking for help", 
            "practicing patience", "appreciating nature"
        ])
        self.theme_elements["wisdom_guide"] = random.choice([
            "grandfather's story", "a special book", "a kind teacher", 
            "observing nature", "a helpful animal"
        ])
        self.theme_elements["growth_sign"] = random.choice([
            "a blooming flower", "a singing bird", "a mended toy", 
            "a shared meal", "a new friendship"
        ])

    def _select_origin_themes(self):
        """Child-friendly nature myths"""
        self.theme_elements["explained_phenomenon"] = random.choice([
            "why fireflies glow", "how rivers learned to sing", 
            "why pandas have black patches", "how silk was discovered",
            "why peaches mean longevity"
        ])
        self.theme_elements["mythic_agent"] = random.choice([
            "playful dragon", "kind moon spirit", "curious monkey", 
            "helpful phoenix", "wise river turtle"
        ])
        self.theme_elements["natural_element"] = random.choice([
            "a warm breeze", "a fallen leaf", "a smooth stone", 
            "a raindrop", "a sunbeam"
        ])

    def _select_vengeance_themes(self):
        """Nature harmony themes"""
        self.theme_elements["nature_problem"] = random.choice([
            "withering plants", "scared animals", "dirty river", 
            "sad forest", "hungry earth"
        ])
        self.theme_elements["nature_helper"] = random.choice([
            "talking tree", "singing bird", "wise fish", 
            "gentle wind spirit", "moon's reflection"
        ])
        self.theme_elements["restoration_action"] = random.choice([
            "planting seeds", "cleaning a stream", "building bird nests",
            "singing healing songs", "sharing kindness"
        ])

    def _select_trial_themes(self):
        """Little hero challenges"""
        self.theme_elements["child_challenge"] = random.choice([
            "lost family treasure", "scared animal friend", "broken festival item",
            "confusing riddle", "important message delivery"
        ])
        self.theme_elements["helper_character"] = random.choice([
            "friendly dragon", "wise grandmother", "playful monkey spirit",
            "talking cricket", "kind cloud"
        ])
        self.theme_elements["solution_tool"] = random.choice([
            "courageous deed", "clever idea", "helpful friends", 
            "special song", "shared gift"
        ])

    # def _select_quest_themes(self):
    #     """Select themes specific to quest arcs."""
    #     self.theme_elements["obstacle_type"] = random.choice(["natural", "supernatural", "human", "self-doubt"])
    #     self.theme_elements["virtue_tested"] = random.choice(["courage", "wisdom", "compassion", "loyalty", "perseverance"])
    #     self.theme_elements["quest_object"] = random.choice(["divine text", "celestial herb", "magical artifact", "lost knowledge"])
    
    # def _select_moral_themes(self):
    #     """Select themes specific to moral lesson arcs."""
    #     self.theme_elements["virtue"] = random.choice(["benevolence (仁)", "righteousness (义)", "propriety (礼)", "wisdom (智)", "trustworthiness (信)"])
    #     self.theme_elements["transgression"] = random.choice(["greed", "pride", "dishonesty", "disrespect", "improper ritual", "filial neglect"])
    #     self.theme_elements["moral_authority"] = random.choice(["Confucian scholar", "village elder", "imperial decree", "ancestral spirit"])
    
    # def _select_cosmic_themes(self):
    #     """Select themes specific to cosmic balance arcs."""
    #     self.theme_elements["cosmic_force"] = random.choice(["yin-yang", "five elements", "heavenly mandate", "fate", "celestial alignment"])
    #     self.theme_elements["imbalance_cause"] = random.choice(["human excess", "ritual neglect", "supernatural being", "cosmic shift", "divine conflict"])
    #     self.theme_elements["natural_sign"] = random.choice(["unusual weather", "astronomical event", "animal behavior", "plant anomaly"])
    
    # def _select_transformation_themes(self):
    #     """Select themes specific to transformation arcs."""
    #     self.theme_elements["transformation_type"] = random.choice(["human to animal", "mortal to immortal", "living to spirit", "animal to human"])
    #     self.theme_elements["catalyst"] = random.choice(["magical object", "divine encounter", "inner cultivation", "cosmic alignment"])
    #     self.theme_elements["price_of_change"] = random.choice(["memories", "human connection", "physical form", "mortal desires"])
    
    # def _select_origin_themes(self):
    #     """Select themes specific to origin myth arcs."""
    #     self.theme_elements["explained_phenomenon"] = random.choice(["natural feature", "animal trait", "human custom", "celestial event", "seasonal change"])
    #     self.theme_elements["mythic_agent"] = random.choice(["creator deity", "culture hero", "first ancestor", "elemental force", "cosmic animal"])
    #     self.theme_elements["primordial_element"] = random.choice(["water", "fire", "wood", "earth", "metal", "void"])
    
    # def _select_vengeance_themes(self):
    #     """Select themes specific to ancestral vengeance arcs."""
    #     self.theme_elements["injustice_type"] = random.choice(["murder", "false accusation", "betrayal", "stolen identity", "broken oath"])
    #     self.theme_elements["spirit_manifestation"] = random.choice(["dreams", "illness", "possession", "apparition", "animal messenger"])
    #     self.theme_elements["mortal_mediator"] = random.choice(["ritual specialist", "descendant", "official", "innocent bystander"])
    
    # def _select_trial_themes(self):
    #     """Select themes specific to bureaucratic trial arcs."""
    #     self.theme_elements["mortal_offense"] = random.choice(["corruption", "ritual impropriety", "moral failing", "cosmic disruption", "accidental transgression"])
    #     self.theme_elements["divine_authority"] = random.choice(["Judge of the Dead", "City God", "Celestial Emperor", "Karma Official", "Moon Goddess"])
    #     self.theme_elements["supernatural_evidence"] = random.choice(["soul records", "magic mirror", "otherworld witness", "karmic ledger", "spirit testimony"])
    
    def _setup_stage_triggers(self):
        """Define which action types are most appropriate to trigger stage advancements."""
        stage_trigger_mappings = {
            "quest": {
                "departure": ["character_action", "environmental_event"],
                "challenge": ["environmental_event", "cosmic_intervention"],
                "revelation": ["object_appearance", "cosmic_intervention"],
                "return": ["character_action", "environmental_event"],
                "transformation": ["cosmic_intervention", "plot_twist"]
            },
            "moral_lesson": {
                "harmony": ["character_action", "environmental_event"],
                "transgression": ["character_action", "plot_twist"],
                "consequence": ["cosmic_intervention", "environmental_event"],
                "realization": ["object_appearance", "cosmic_intervention"],
                "atonement": ["character_action", "cosmic_intervention"]
            },
            "cosmic_balance": {
                "order": ["environmental_event", "character_action"],
                "disruption": ["plot_twist", "cosmic_intervention"],
                "chaos": ["environmental_event", "wildcard"],
                "intervention": ["cosmic_intervention", "object_appearance"],
                "new_order": ["cosmic_intervention", "character_action"]
            },
            "transformation": {
                "ordinary": ["character_action", "environmental_event"],
                "encounter": ["object_appearance", "cosmic_intervention"],
                "change": ["cosmic_intervention", "character_action"],
                "challenge": ["environmental_event", "plot_twist"],
                "transcendence": ["cosmic_intervention", "wildcard"]
            },
            "origin_myth": {
                "void": ["environmental_event", "cosmic_intervention"],
                "creation": ["cosmic_intervention", "object_appearance"],
                "conflict": ["character_action", "environmental_event"],
                "resolution": ["cosmic_intervention", "plot_twist"],
                "explanation": ["cosmic_intervention", "environmental_event"]
            },
            "ancestral_vengeance": {
                "injustice": ["character_action", "plot_twist"],
                "suffering": ["environmental_event", "character_action"],
                "divine_sign": ["cosmic_intervention", "object_appearance"],
                "retribution": ["cosmic_intervention", "environmental_event"],
                "ancestral_peace": ["cosmic_intervention", "character_action"]
            },
            "bureaucratic_trial": {
                "mortal_case": ["character_action", "environmental_event"],
                "underworld_appeal": ["cosmic_intervention", "character_action"],
                "divine_judgment": ["cosmic_intervention", "object_appearance"],
                "cosmic_record": ["object_appearance", "cosmic_intervention"],
                "karmic_resolution": ["cosmic_intervention", "plot_twist"]
            }
        }
        
        self.stage_triggers = stage_trigger_mappings.get(self.arc_type, {})
    
    def get_current_stage(self, language=Language.ENGLISH):
        """Get the current narrative stage.
        
        Args:
            language: The language to return the stage name in.
            
        Returns:
            The current stage name in the requested language.
        """
        if language == Language.CHINESE:
            return self.zh_stages[self.current_stage_index]
        elif language == Language.BILINGUAL:
            return f"{self.stages[self.current_stage_index]} ({self.zh_stages[self.current_stage_index]})"
        return self.stages[self.current_stage_index]
    
    def advance_stage_if_appropriate(self, current_turn, action_type):
        """Determine if the story should advance to the next stage.
        
        Args:
            current_turn: The current turn number.
            action_type: The current action type.
            
        Returns:
            True if the stage advanced, False otherwise.
        """
        # If we've spent enough turns in the current stage, consider advancing
        current_stage = self.stages[self.current_stage_index]
        turns_in_stage = sum(self.stage_turns[:self.current_stage_index])
        
        # Check if we've used the allocated turns for this stage
        if current_turn >= turns_in_stage + self.stage_turns[self.current_stage_index]:
            self.current_stage_index = min(self.current_stage_index + 1, len(self.stages) - 1)
            return True
        
        # Or if the action type is a trigger for this stage's advancement
        if action_type in self.stage_triggers.get(current_stage, []):
            # Only advance if we're at least halfway through the allocated turns for this stage
            if current_turn >= turns_in_stage + (self.stage_turns[self.current_stage_index] // 2):
                self.current_stage_index = min(self.current_stage_index + 1, len(self.stages) - 1)
                return True
        
        return False
    
    def get_stage_guidance(self, language=Language.ENGLISH):
        """Get narrative guidance based on the current stage.
        
        Args:
            language: The language to return the guidance in.
            
        Returns:
            Guidance text for the current narrative stage in the requested language.
        """
        from narrative.stages import get_stage_guidance
        return get_stage_guidance(self.stages[self.current_stage_index], language)
    
    def get_related_literature(self, language=Language.ENGLISH):
        """Get related classical texts for the current story arc.
        
        Args:
            language: The language to return the literature references in.
            
        Returns:
            Text about related classical literature in the requested language.
        """
        related_text = self.arc_data.get("related_text", "")
        
        if language == Language.CHINESE:
            return f"相关典籍: {related_text}"
        elif language == Language.ENGLISH:
            return f"Related classical texts: {related_text}"
        else:  # BILINGUAL
            return f"Related classical texts / 相关典籍: {related_text}"
    
    def get_motifs(self, language=Language.ENGLISH):
        """Get the recurring motifs for this story.
        
        Args:
            language: The language to return the motifs in.
            
        Returns:
            Text describing the story motifs in the requested language.
        """
        from narrative.themes import get_motifs_text
        return get_motifs_text(self.motifs, language)
    
    def to_dict(self):
        """Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation of the StoryArc.
        """
        return {
            "arc_type": self.arc_type,
            "current_stage_index": self.current_stage_index,
            "max_turns": self.max_turns,
            "stage_turns": self.stage_turns,
            "theme_elements": self.theme_elements,
            "motifs": self.motifs
        }
    
    @classmethod
    def from_dict(cls, data):
        """Recreate from dictionary.
        
        Args:
            data: Dictionary containing StoryArc data.
            
        Returns:
            A new StoryArc instance with the provided data.
        """
        arc = cls(arc_type=data.get("arc_type"), max_turns=data.get("max_turns", 10))
        arc.current_stage_index = data.get("current_stage_index", 0)
        arc.stage_turns = data.get("stage_turns", arc.stage_turns)
        arc.theme_elements = data.get("theme_elements", {})
        arc.motifs = data.get("motifs", [])
        return arc