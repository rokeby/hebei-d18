"""Wu Xing (Five Elements) cosmology system."""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

from utils.language import Language

class Element(Enum):
    """The five elements of Wu Xing cosmology."""
    WOOD = "wood"
    FIRE = "fire"
    EARTH = "earth"
    METAL = "metal"
    WATER = "water"

class Direction(Enum):
    """Cardinal directions in Chinese cosmology."""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    CENTER = "center"

@dataclass
class ElementalProperties:
    """Properties associated with each element in Wu Xing cosmology."""
    element: Element
    season: str
    direction: Direction
    color: str
    virtue: str
    animal: str
    emotion: str
    organ: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "element": self.element.value,
            "season": self.season,
            "direction": self.direction.value,
            "color": self.color,
            "virtue": self.virtue,
            "animal": self.animal,
            "emotion": self.emotion,
            "organ": self.organ
        }

class WuXing:
    """Wu Xing (Five Elements) system for Chinese cosmology."""
    
    def __init__(self):
        """Initialize the Wu Xing system with element properties and relationships."""
        self.elements = {
            Element.WOOD: ElementalProperties(
                element=Element.WOOD,
                season="spring",
                direction=Direction.EAST,
                color="green/blue",
                virtue="benevolence",
                animal="azure dragon",
                emotion="anger/frustration",
                organ="liver"
            ),
            Element.FIRE: ElementalProperties(
                element=Element.FIRE,
                season="summer",
                direction=Direction.SOUTH,
                color="red",
                virtue="propriety",
                animal="vermilion bird",
                emotion="joy/excitement",
                organ="heart"
            ),
            Element.EARTH: ElementalProperties(
                element=Element.EARTH,
                season="late summer",
                direction=Direction.CENTER,
                color="yellow",
                virtue="trustworthiness",
                animal="yellow dragon",
                emotion="pensiveness",
                organ="spleen"
            ),
            Element.METAL: ElementalProperties(
                element=Element.METAL,
                season="autumn",
                direction=Direction.WEST,
                color="white",
                virtue="righteousness",
                animal="white tiger",
                emotion="sadness/grief",
                organ="lungs"
            ),
            Element.WATER: ElementalProperties(
                element=Element.WATER,
                season="winter",
                direction=Direction.NORTH,
                color="black",
                virtue="wisdom",
                animal="black turtle",
                emotion="fear/fright",
                organ="kidneys"
            )
        }
        
        # Productive cycle (生)
        self.productive_cycle = {
            Element.WOOD: Element.FIRE,
            Element.FIRE: Element.EARTH,
            Element.EARTH: Element.METAL,
            Element.METAL: Element.WATER,
            Element.WATER: Element.WOOD
        }
        
        # Destructive cycle (克)
        self.destructive_cycle = {
            Element.WOOD: Element.EARTH,
            Element.EARTH: Element.WATER,
            Element.WATER: Element.FIRE,
            Element.FIRE: Element.METAL,
            Element.METAL: Element.WOOD
        }
        
        # Element translations
        self.element_names_zh = {
            "wood": "木",
            "fire": "火",
            "earth": "土",
            "metal": "金",
            "water": "水"
        }
        
        # Bilingual element properties
        self.bilingual_elements = {
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
    
    def get_element_properties(self, element: Element) -> ElementalProperties:
        """Get properties for a specific element.
        
        Args:
            element: The element to get properties for.
            
        Returns:
            ElementalProperties for the specified element.
        """
        return self.elements[element]
    
    def get_element_text(self, element_name: str, language=Language.ENGLISH) -> str:
        """Get element name in specified language.
        
        Args:
            element_name: The element name in English.
            language: The language to get the name in.
            
        Returns:
            Element name in the specified language.
        """
        if language == Language.CHINESE:
            return self.element_names_zh.get(element_name, element_name)
        elif language == Language.BILINGUAL:
            return f"{element_name} ({self.element_names_zh.get(element_name, '')})"
        return element_name
    
    def get_bilingual_properties(self, element_name: str, language=Language.ENGLISH) -> Dict:
        """Get element properties in specified language.
        
        Args:
            element_name: The element name in English.
            language: The language to get properties in.
            
        Returns:
            Element properties in the specified language.
        """
        if element_name not in self.bilingual_elements:
            return {}
            
        if language == Language.CHINESE:
            return self.bilingual_elements[element_name]["zh"]
        elif language == Language.ENGLISH:
            return self.bilingual_elements[element_name]["en"]
        else:  # BILINGUAL
            zh_props = self.bilingual_elements[element_name]["zh"]
            en_props = self.bilingual_elements[element_name]["en"]
            return {
                "season": f"{en_props['season']} ({zh_props['season']})",
                "direction": f"{en_props['direction']} ({zh_props['direction']})",
                "color": f"{en_props['color']} ({zh_props['color']})",
                "virtue": f"{en_props['virtue']} ({zh_props['virtue']})",
                "animal": f"{en_props['animal']} ({zh_props['animal']})"
            }
    
    def get_productive_relationship(self, element: Element) -> Element:
        """Get what this element produces.
        
        Args:
            element: The source element.
            
        Returns:
            The element produced by the source element.
        """
        return self.productive_cycle[element]
    
    def get_destructive_relationship(self, element: Element) -> Element:
        """Get what this element destroys.
        
        Args:
            element: The source element.
            
        Returns:
            The element destroyed by the source element.
        """
        return self.destructive_cycle[element]
    
    def get_compatible_elements(self, element: Element) -> List[Element]:
        """Get elements that are compatible (productive relationship).
        
        Args:
            element: The source element.
            
        Returns:
            List of elements compatible with the source element.
        """
        return [self.get_productive_relationship(element), element]
    
    def transition_element(self, current: Element, narrative_type: str) -> Element:
        """Transition to next element based on narrative progression.
        
        Args:
            current: The current element.
            narrative_type: The type of narrative progression.
            
        Returns:
            The next element in the sequence.
        """
        if narrative_type in ["peaceful", "harmonious"]:
            return self.get_productive_relationship(current)
        elif narrative_type in ["conflict", "challenge"]:
            return self.get_destructive_relationship(current)
        else:
            # Default progression through the cycle
            cycle_order = [Element.WOOD, Element.FIRE, Element.EARTH, Element.METAL, Element.WATER]
            current_index = cycle_order.index(current)
            return cycle_order[(current_index + 1) % len(cycle_order)]
    
    def get_element_cycle(self) -> List[str]:
        """Get the standard Wu Xing cycle as string values.
        
        Returns:
            List of element names in standard cycle order.
        """
        return ["wood", "fire", "earth", "metal", "water"]
        
    def calculate_next_position(self, current_position: str, turns: int) -> str:
        """Calculate cosmic position after a number of turns.
        
        Args:
            current_position: The current element name.
            turns: Number of turns to advance.
            
        Returns:
            The resulting element name.
        """
        elements_cycle = self.get_element_cycle()
        base_index = elements_cycle.index(current_position)
        new_index = (base_index + turns) % len(elements_cycle)
        return elements_cycle[new_index]