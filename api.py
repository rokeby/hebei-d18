from flask import Flask, jsonify, request
import random
import json
import pickle
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from story_engine import StoryEngine, StoryState

load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client and story engine
client = OpenAI()
story_engine = StoryEngine()

# Ensure required directories exist
os.makedirs('./cache', exist_ok=True)
os.makedirs('./stories', exist_ok=True)

def generate_narrative_with_llm(prompt: str, system_prompt: str = None) -> str:
    """Generate narrative using OpenAI API"""
    try:
        if system_prompt is None:
            system_prompt = """You are a master storyteller of ancient Chinese folktales from the Han dynasty period. 
            Your stories draw from classical Chinese mythology, cosmology, and folklore. 
            Write in a style that evokes ancient tales but remains accessible to modern readers. 
            Keep each narrative turn concise (1-2 paragraphs maximum) but evocative."""
        
        completion = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper option
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,  # Higher temperature for more creative storytelling
            max_tokens=200    # Keep narrative turns concise
        )
        
        return completion.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Error generating narrative: {e}")
        return f"[Error: Unable to generate narrative]"

@app.route('/')
def home():
    """Show currently active story or latest completed story"""
    try:
        # Check for active story
        with open('./cache/active_story.pkl', 'rb') as f:
            active_state = pickle.load(f)
        
        if active_state.current_turn < active_state.max_turns:
            return jsonify({
                "status": "active",
                "story": active_state.to_dict(),
                "narrative": [turn["narrative"] for turn in active_state.narrative_thread]
            })
    except FileNotFoundError:
        pass
    
    # Fall back to latest completed story
    story_files = [f for f in os.listdir("./stories") if f.endswith('.json')]
    if story_files:
        story_files.sort()
        with open(f"./stories/{story_files[-1]}", 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    
    return jsonify({"message": "No stories available yet. Start a new story!"})

@app.route('/start_story', methods=['POST'])
def start_story():
    """Start a new story"""
    # Get seed from previous story
    previous_id = request.json.get('previous_story_id', None) if request.is_json else None
    seed_data = story_engine.get_story_seed_from_previous(previous_id)
    
    # Create new story state
    state = StoryState()
    state.previous_sentence = seed_data.get("seed", "Long ago, in the time when dragons still walked among mortals...")
    state.cosmic_position = seed_data.get("cosmic_position", "wood")
    
    # Generate an opening narrative based on the seed
    opening_prompt = f"""Begin a new Chinese folktale based on this opening: "{state.previous_sentence}"
    The story takes place during the Han dynasty and should incorporate elements of Chinese cosmology. 
    Start with the cosmic element of {state.cosmic_position}. Write an engaging opening paragraph."""
    
    opening_narrative = generate_narrative_with_llm(opening_prompt)
    
    # Record the opening as the first turn
    state.narrative_thread.append({
        "turn": 0,
        "roll": None,
        "action_type": "opening",
        "elements": {"cosmic_element": state.cosmic_position},
        "narrative": opening_narrative
    })
    state.previous_sentence = opening_narrative
    
    # Save as active story
    with open('./cache/active_story.pkl', 'wb') as f:
        pickle.dump(state, f)
    
    return jsonify({
        "message": "New story started",
        "story_id": state.story_id,
        "opening_narrative": opening_narrative,
        "cosmic_position": state.cosmic_position,
        "seed_from": previous_id if previous_id else "random"
    })

@app.route('/next_turn', methods=['POST'])
def next_turn():
    """Generate the next turn of the current story"""
    # Load active story
    try:
        with open('./cache/active_story.pkl', 'rb') as f:
            state = pickle.load(f)
    except FileNotFoundError:
        return jsonify({"error": "No active story found. Please start a new story first."}), 404
    
    # Check if story is already completed
    if state.current_turn >= state.max_turns:
        return jsonify({"error": "Story is already completed", "story_id": state.story_id}), 400
    
    # Roll the die
    roll, action_type = story_engine.die.roll()
    
    # Get cosmic position
    current_element = story_engine.get_cosmic_position(state)
    state.cosmic_position = current_element
    
    # Select elements for this turn
    selected_elements = story_engine.select_elements(action_type, current_element)
    
    # Create prompt for the narrative
    prompt = story_engine.create_prompt(state, selected_elements, action_type)
    
    # Generate narrative using OpenAI
    narrative = generate_narrative_with_llm(prompt)
    
    # Update state
    state.current_turn += 1
    state.previous_sentence = narrative
    state.narrative_thread.append({
        "turn": state.current_turn,
        "roll": roll,
        "action_type": action_type,
        "elements": selected_elements,
        "narrative": narrative
    })
    
    # Check if story should end
    if roll == 18 or state.current_turn >= state.max_turns:
        # Generate an ending if needed
        if roll == 18:
            ending_prompt = f"""Complete this Chinese folktale with a fitting conclusion. 
            The story has taken place in the cosmic element of {current_element}. 
            Previous narrative: {narrative}
            Write a satisfying ending that ties together the themes and elements introduced."""
            
            ending_narrative = generate_narrative_with_llm(ending_prompt)
            state.narrative_thread.append({
                "turn": state.current_turn + 1,
                "roll": roll,
                "action_type": "ending",
                "elements": selected_elements,
                "narrative": ending_narrative
            })
        
        # Save completed story
        story_engine.save_story(state)
        
        # Clear active story
        os.remove('./cache/active_story.pkl')
        
        return jsonify({
            "status": "completed",
            "story_id": state.story_id,
            "final_narrative": state.narrative_thread[-1]["narrative"],
            "total_turns": state.current_turn,
            "complete_story": [turn["narrative"] for turn in state.narrative_thread]
        })
    
    # Save updated state
    with open('./cache/active_story.pkl', 'wb') as f:
        pickle.dump(state, f)
    
    return jsonify({
        "status": "continuing",
        "turn": state.current_turn,
        "roll": roll,
        "action_type": action_type,
        "elements": selected_elements,
        "narrative": narrative,
        "cosmic_position": state.cosmic_position,
        "remaining_turns": state.max_turns - state.current_turn
    })

@app.route('/get_story/<story_id>', methods=['GET'])
def get_story(story_id):
    """Retrieve a specific completed story"""
    try:
        with open(f"./stories/{story_id}.json", 'r', encoding='utf-8') as f:
            story_data = json.load(f)
        return jsonify(story_data)
    except FileNotFoundError:
        return jsonify({"error": "Story not found"}), 404

@app.route('/list_stories', methods=['GET'])
def list_stories():
    """List all completed stories"""
    story_files = [f.replace('.json', '') for f in os.listdir("./stories") if f.endswith('.json')]
    story_files.sort(reverse=True)  # Most recent first
    
    stories = []
    for story_id in story_files[:10]:  # Limit to 10 most recent
        try:
            with open(f"./stories/{story_id}.json", 'r', encoding='utf-8') as f:
                story_data = json.load(f)
                stories.append({
                    "id": story_id,
                    "completed_at": story_data.get("completed_at"),
                    "turns": story_data.get("total_turns", 0),
                    "final_element": story_data.get("cosmic_position", "unknown")
                })
        except:
            continue
    
    return jsonify({"stories": stories})

@app.route('/active_story', methods=['GET'])
def get_active_story():
    """Get the current active story state"""
    try:
        with open('./cache/active_story.pkl', 'rb') as f:
            state = pickle.load(f)
        
        return jsonify({
            "story_id": state.story_id,
            "current_turn": state.current_turn,
            "max_turns": state.max_turns,
            "cosmic_position": state.cosmic_position,
            "narrative_so_far": [turn["narrative"] for turn in state.narrative_thread]
        })
    except FileNotFoundError:
        return jsonify({"message": "No active story"}), 404

@app.route('/roll_die', methods=['POST'])
def roll_die():
    """Roll the D18 die independently (for testing)"""
    roll, action_type = story_engine.die.roll()
    return jsonify({
        "roll": roll,
        "action_type": action_type
    })

if __name__ == '__main__':
    # Make sure you have OpenAI API key set in .env file
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables")
    
    app.run(host='0.0.0.0', port=5000, debug=True)