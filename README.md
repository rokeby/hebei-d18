#folktale generator

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Run the application
python api.py

# Start a bilingual story
curl -X POST http://localhost:5555/start_story \
  -H "Content-Type: application/json" \
  -d '{"language": "both"}'

# Start a Chinese-only story
curl -X POST http://localhost:5555/start_story \
  -H "Content-Type: application/json" \
  -d '{"language": "zh"}'

# Start an English-only story
curl -X POST http://localhost:5555/start_story \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'

# Switch language of active story
curl -X POST http://localhost:5555/language/both
curl -X POST http://localhost:5555/language/zh
curl -X POST http://localhost:5555/language/en

# Continue story (language is saved in the story state)
curl -X POST http://localhost:5555/next_turn

# Get a list of all available story arc types
curl http://localhost:5555/story_arcs

# Start a classic "quest" story
curl -X POST http://localhost:5555/start_story \
  -H "Content-Type: application/json" \
  -d '{"language": "both", "arc_type": "quest"}'

# Generate a bureaucratic trial story (underworld judgment)
curl -X POST http://localhost:5555/start_story \
  -H "Content-Type: application/json" \
  -d '{"language": "zh", "arc_type": "bureaucratic_trial"}'


# Core Pipeline Overview
The folktale generation pipeline can be summarized as follows:

Initialization: The system loads the data files (characters, places, objects, etc.) and initializes a story state.
Story Seeding: A story is started with a seed sentence, either randomly selected or derived from a previous story.
Turn-based Generation: For each turn, the system:

Rolls a virtual 18-sided die to determine the action type
Advances the cosmic position through the Wu Xing cycle
Selects appropriate narrative elements
Generates a prompt for the LLM (DeepSeek)
Processes the response and adds it to the narrative thread
Progresses the story arc

Story Completion: The story concludes when reaching max turns, rolling a story ending, or completing all arc stages.

# Key Files and Prompting Mechanisms
1. engine/engine.py - Core Story Engine
This contains the StoryEngine class which is responsible for most of the story generation pipeline:

Line 333-399: The build_prompt method - This is where the prompts for each story turn are constructed.
Line 138-155: The select_elements method - Determines which narrative elements to include in each turn.
Line 277-312: The create_opening_prompt method - Special prompt for story beginnings.
Line 314-329: The create_ending_prompt method - Special prompt for story conclusions.

# 2. engine/prompt.py - Prompt Construction
This is dedicated to prompt construction and is a critical file for tweaking:

Line 13-228: The create_prompt function - The main function that builds prompts based on the current state, elements, and action type.
Lines 155-211: The helper functions that add specific components to the prompt:

```_add_thematic_elements - Adds theme elements
_add_story_elements - Adds story elements
_add_style_instructions - Adds style instructions
```

# 3. api.py - API and Generation Coordination
This file handles the API endpoints and orchestrates the generation process:

Line 62-178: The generate_narrative_with_llm function - Makes the actual API call to DeepSeek LLM.
Line 214-330: The start_story endpoint - Begins a new story.
Line 332-526: The next_turn endpoint - Generates the next turn of the story.

# 4. narrative/arc.py - Story Arc Management
This manages the narrative structure of the stories:

Line 8-462: The StoryArc class - Defines different story arc types.
Line 81-170: Various theme selection methods that influence prompt content.

# Example Prompt Analysis
Here's an example of a generated prompt (from engine/prompt.py):

```
	You are a master storyteller versed in Han dynasty (206 BCE-220 CE) traditions and folklore.
	Continue the following story with a single paragraph.

	Story arc: A hero embarks on a journey, faces trials, gains wisdom, and returns transformed
	Current stage: challenge
	Stage guidance: The protagonist faces obstacles that test their resolve and abilities.
	Related classical texts: 《穆天子传》《西游记》
	Story motifs: jade talisman, celestial guidance

	Current cosmic element: fire (season: summer, direction: south, color: red)
	Action type: character_action
	Current turn: 3/10

	Previous narrative: [previous narrative text]

	Include these elements in your continuation:
	- character: Confucian scholar from Handan

	Write in a style authentic to Han dynasty folklore, referencing elements from classical texts like Huainanzi, Records of the Seeking of Spirits, or Records of the Grand Historian. Incorporate the qualities and seasonal aspects of the current cosmic element. Ensure your narrative advances the current story stage (challenge) appropriately. Your style should evoke the mystery, moral dimensions, and cosmological worldview characteristic of Han dynasty stories.
```

# To Modify and Fine-tune

```
	To modify how stories are seeded, look at:
	engine/engine.py, method get_story_seed_from_previous (lines 227-254)`


	To adjust the narrative style and tone:
	engine/prompt.py, method _add_style_instructions (lines 184-199)


	To change how cosmic elements influence the story:
	cosmology/wuxing.py - The WuXing class (lines 46-284)


	To modify the LLM parameters:
	api.py, function generate_narrative_with_llm (lines 62-178)


	To adjust story arcs and progression:
	narrative/arc.py - The ARC_TYPES dictionary and StoryArc class
```

The most direct way to influence the output is by editing the prompt templates in engine/prompt.py and the system prompts in api.py. These determine how the instructions are presented to the LLM and significantly impact the generated narratives.