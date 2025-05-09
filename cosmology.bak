from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class Element(Enum):
    WOOD = "wood"
    FIRE = "fire"
    EARTH = "earth"
    METAL = "metal"
    WATER = "water"

class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    CENTER = "center"

@dataclass
class ElementalProperties:
    element: Element
    season: str
    direction: Direction
    color: str
    virtue: str
    animal: str
    emotion: str
    organ: str
    
    def to_dict(self):
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
    """Wu Xing (Five Elements) system for Chinese cosmology"""
    
    def __init__(self):
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
    
    def get_element_properties(self, element: Element) -> ElementalProperties:
        return self.elements[element]
    
    def get_productive_relationship(self, element: Element) -> Element:
        """Get what this element produces"""
        return self.productive_cycle[element]
    
    def get_destructive_relationship(self, element: Element) -> Element:
        """Get what this element destroys"""
        return self.destructive_cycle[element]
    
    def get_compatible_elements(self, element: Element) -> List[Element]:
        """Get elements that are compatible (productive relationship)"""
        return [self.get_productive_relationship(element), element]
    
    def transition_element(self, current: Element, narrative_type: str) -> Element:
        """Transition to next element based on narrative progression"""
        if narrative_type in ["peaceful", "harmonious"]:
            return self.get_productive_relationship(current)
        elif narrative_type in ["conflict", "challenge"]:
            return self.get_destructive_relationship(current)
        else:
            # Default progression through the cycle
            cycle_order = [Element.WOOD, Element.FIRE, Element.EARTH, Element.METAL, Element.WATER]
            current_index = cycle_order.index(current)
            return cycle_order[(current_index + 1) % len(cycle_order)]

class BaguaDirections:
    """Ba Gua (Eight Trigrams) directional system"""
    
    def __init__(self):
        self.trigrams = {
            "qian": {"direction": Direction.SOUTH, "element": Element.METAL, "meaning": "heaven"},
            "kun": {"direction": Direction.NORTH, "element": Element.EARTH, "meaning": "earth"},
            "zhen": {"direction": Direction.EAST, "element": Element.WOOD, "meaning": "thunder"},
            "xun": {"direction": "southeast", "element": Element.WOOD, "meaning": "wind"},
            "kan": {"direction": Direction.NORTH, "element": Element.WATER, "meaning": "water"},
            "li": {"direction": Direction.SOUTH, "element": Element.FIRE, "meaning": "fire"},
            "gen": {"direction": "northeast", "element": Element.EARTH, "meaning": "mountain"},
            "dui": {"direction": "northwest", "element": Element.METAL, "meaning": "lake"}
        }
    
    def get_trigram_for_direction(self, direction: str) -> str:
        for trigram, properties in self.trigrams.items():
            if properties["direction"] == direction:
                return trigram
        return None

class ChineseCosmos:
    """Combined cosmological system"""
    
    def __init__(self):
        self.wuxing = WuXing()
        self.bagua = BaguaDirections()
        
        # Celestial stems and earthly branches could be added here
        self.celestial_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    def get_cosmic_context(self, element: Element, turn_number: int) -> Dict:
        """Get full cosmic context for a story turn"""
        props = self.wuxing.get_element_properties(element)
        
        return {
            "element": props.to_dict(),
            "productive_next": self.wuxing.get_productive_relationship(element).value,
            "destructive_target": self.wuxing.get_destructive_relationship(element).value,
            "compatible_elements": [e.value for e in self.wuxing.get_compatible_elements(element)],
            "turn_number": turn_number,
            # Add more cosmic calculations as needed
        }