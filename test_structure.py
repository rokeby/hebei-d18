# test_structure.py
from engine import StoryEngine
from utils.language import Language
from narrative.arc import StoryArc

# Initialize the engine
engine = StoryEngine()

# Create a story state
from engine import StoryState
state = StoryState(language=Language.BILINGUAL)
state.story_arc = StoryArc(arc_type="quest")

# Test element selection
elements = engine.select_elements("character_action", "wood", Language.BILINGUAL)
print("Selected elements:", elements)

# Test prompt generation
prompt = engine.build_prompt(state, elements, "character_action")
print("\nGenerated prompt (excerpt):")
print(prompt[:300] + "...")

print("\nStructure test completed successfully!")