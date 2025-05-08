from flask import Flask, jsonify, request
import random
import json
import pickle
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from story_engine import StoryEngine, StoryState, Language  # Add Language here

load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client and story engine

client = OpenAI(base_url="https://api.deepseek.com")
story_engine = StoryEngine()

# Ensure required directories exist
os.makedirs('./cache', exist_ok=True)
os.makedirs('./stories', exist_ok=True)

def print_separator():
    """Print a visual separator for readability"""
    print("\n" + "="*60 + "\n")

def print_story_status(state: StoryState):
    """Print current story status with language support"""
    print(f"📖 STORY STATUS:")
    print(f"   ID: {state.story_id}")
    print(f"   Turn: {state.current_turn}/{state.max_turns}")
    print(f"   Cosmic Position: {state.cosmic_position}")
    print(f"   Language: {state.language}")
    print()

def generate_narrative_with_llm(prompt: str, language=Language.ENGLISH, system_prompt: str = None) -> dict:
    """Generate narrative using DeepSeek API, handling bilingual content and tracking token usage"""
    try:
        if system_prompt is None:
            if language == Language.CHINESE:
                system_prompt = """你是一位精通汉代历史和文化的故事大师。
                你的故事融合了中国古代神话、宇宙观和民间传说元素，包括:
                - 五行相生相克理论
                - 阴阳宇宙观
                - 天庭体系和神仙
                - 昆仑山和西方仙境
                - 黄帝和古代圣贤
                - 青铜器礼器和玉器
                - 早期道家和儒家思想
                
                你的写作风格应:
                - 唤起古代故事的韵味但保持易懂
                - 使用中国古典叙事结构
                - 融入宇宙和道德维度
                - 保持神秘感和永恒性
                - 引用真实的汉代文化和信仰
                
                请保持故事段落简洁(2-3句)但生动。"""
            elif language == Language.ENGLISH:
                system_prompt = """You are a master storyteller of ancient Chinese folktales from the Han dynasty period (206 BCE - 220 CE). 
                Your stories draw from classical Chinese mythology, cosmology, and folklore including:
                - Wu Xing (Five Elements) theory
                - Yin-Yang cosmology  
                - Celestial bureaucracy and immortals
                - Mount Kunlun and the western paradise
                - The Yellow Emperor and ancient sage kings
                - Bronze age ritual vessels and jade objects
                - Early Daoist and Confucian philosophy
                
                Write in a style that:
                - Evokes ancient tales but remains accessible
                - Uses classical Chinese narrative structures
                - Incorporates cosmic and moral dimensions
                - Maintains an air of mystery and timelessness
                - References authentic Han dynasty culture and beliefs
                
                Keep each narrative turn concise (2-3 sentences) but evocative."""
            else:  # BILINGUAL
                system_prompt = """You are a master storyteller specializing in Han dynasty Chinese folktales. You are fully bilingual in Chinese and English.

                For this task, you will generate narrative content in BOTH Chinese and English. First write a paragraph in Chinese, then provide its English translation.
                
                Your stories should incorporate authentic elements:
                - Wu Xing (Five Elements) theory (五行)
                - Classical Chinese mythology and cosmology (中国古代神话和宇宙观)
                - Han dynasty cultural references (汉代文化元素)
                - References to historical artifacts and places (历史文物和地点)
                
                Write in a style that:
                - Captures the essence of ancient Chinese storytelling
                - Remains culturally appropriate in both languages
                - Maintains consistency between versions
                
                First provide your narrative in Chinese (2-3 sentences), followed by its English translation.
                VERY IMPORTANT: You must provide BOTH the Chinese and English versions."""
        
        # Fix the message format for DeepSeek API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Call DeepSeek API
        completion = client.chat.completions.create(
            model="deepseek-chat",  # or whatever model you're using
            messages=messages,
            temperature=0.5,
            max_tokens=2000
        )
        
        # Extract narrative content
        narrative = completion.choices[0].message.content.strip()
        
        # Extract token usage information
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        total_tokens = completion.usage.total_tokens
        
        # Log token usage
        print(f"🔢 TOKEN USAGE:")
        print(f"   Prompt tokens: {prompt_tokens}")
        print(f"   Completion tokens: {completion_tokens}")
        print(f"   Total tokens: {total_tokens}")
        print()
        
        # For bilingual responses, parse to separate Chinese and English
        if language == Language.BILINGUAL:
            parsed = story_engine.parse_bilingual_response(narrative)
            return {
                "zh": parsed["zh"], 
                "en": parsed["en"],
                "token_usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
            }
        
        # Return token usage along with the narrative
        return {
            "content": narrative,
            "token_usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        }
    
    except Exception as e:
        print(f"❌ ERROR generating narrative: {e}")
        print(f"Exception details: {str(e)}")  # Add more detailed error output
        if language == Language.BILINGUAL:
            return {"zh": f"[错误: 无法生成叙述]", "en": f"[Error: Unable to generate narrative]"}
        return {"content": f"[Error: Unable to generate narrative]"}

@app.route('/')
def home():
    """Show currently active story or latest completed story"""
    print("\n🏠 HOME ENDPOINT ACCESSED")
    
    try:
        # Check for active story
        with open('./cache/active_story.pkl', 'rb') as f:
            active_state = pickle.load(f)
        
        if active_state.current_turn < active_state.max_turns:
            print("📚 Returning active story")
            print_story_status(active_state)
            return jsonify({
                "status": "active",
                "story": active_state.to_dict(),
                "narrative": [turn["narrative"] for turn in active_state.narrative_thread]
            })
    except FileNotFoundError:
        print("❌ No active story found")
    
    # Fall back to latest completed story
    story_files = [f for f in os.listdir("./stories") if f.endswith('.json')]
    if story_files:
        story_files.sort()
        print(f"📜 Returning latest completed story: {story_files[-1]}")
        with open(f"./stories/{story_files[-1]}", 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    
    print("💤 No stories available yet")
    return jsonify({"message": "No stories available yet. Start a new story!"})

@app.route('/start_story', methods=['POST'])
def start_story():
    """Start a new story with language option"""
    print_separator()
    print("🚀 STARTING NEW STORY")
    
    # Get language preference and previous story ID
    request_data = request.json if request.is_json else {}
    language = request_data.get('language', Language.ENGLISH)
    previous_id = request_data.get('previous_story_id')
    
    print(f"   Language: {language}")
    print(f"   Previous story ID: {previous_id or 'None (fresh start)'}")
    
    seed_data = story_engine.get_story_seed_from_previous(previous_id)
    print(f"   Seed source: {'Previous story' if previous_id else 'Random seed'}")
    
    # Create new story state with language preference
    state = StoryState(language=language)
    state.previous_sentence = seed_data.get("seed", "Long ago, in the time when dragons still walked among mortals...")
    state.previous_sentence_zh = seed_data.get("seed_zh", "很久以前，当龙还行走在人间的时候...")
    state.cosmic_position = seed_data.get("cosmic_position", "wood")
    
    print(f"   Initial cosmic position: {state.cosmic_position}")
    if language == Language.CHINESE:
        print(f"   种子文本: '{state.previous_sentence_zh[:100]}...'")
    elif language == Language.ENGLISH:
        print(f"   Seed text: '{state.previous_sentence[:100]}...'")
    else:
        print(f"   Seed text (ZH): '{state.previous_sentence_zh[:50]}...'")
        print(f"   Seed text (EN): '{state.previous_sentence[:50]}...'")
    print()
    
    # Generate an opening narrative based on the seed
    if language == Language.CHINESE:
        opening_prompt = f"""以这个开头创作一个新的中国民间故事: "{state.previous_sentence_zh}"
        故事发生在汉代，应包含中国传统宇宙观的元素。
        从{story_engine.get_element_text(state.cosmic_position, Language.CHINESE)}元素开始。写一个引人入胜的开场段落。"""
    elif language == Language.ENGLISH:
        opening_prompt = f"""Begin a new Chinese folktale based on this opening: "{state.previous_sentence}"
        The story takes place during the Han dynasty and should incorporate elements of Chinese cosmology. 
        Start with the cosmic element of {state.cosmic_position}. Write an engaging opening paragraph."""
    else:  # BILINGUAL
        opening_prompt = f"""Create a new Chinese folktale in BOTH Chinese and English. First write in Chinese, then provide its English translation.

        Chinese opening line: "{state.previous_sentence_zh}"
        English opening line: "{state.previous_sentence}"
        
        The story takes place during the Han dynasty and should incorporate elements of Chinese cosmology.
        Start with the cosmic element of {state.cosmic_position} ({story_engine.get_element_text(state.cosmic_position, Language.CHINESE)}).
        
        Write an engaging opening paragraph in Chinese first, followed by its English translation."""
    
    print("📝 GENERATING OPENING NARRATIVE")
    opening_result = generate_narrative_with_llm(opening_prompt, language)
    
    # Handle different response formats based on language
    if language == Language.BILINGUAL and isinstance(opening_result, dict) and "zh" in opening_result:
        opening_narrative_zh = opening_result["zh"]
        opening_narrative_en = opening_result["en"]
        token_usage = opening_result.get("token_usage", {})
        
        # Record the opening as the first turn
        state.narrative_thread.append({
            "turn": 0,
            "roll": None,
            "action_type": "opening",
            "elements": {"cosmic_element": state.cosmic_position},
            "narrative": opening_narrative_en,
            "narrative_zh": opening_narrative_zh,
            "token_usage": token_usage
        })
        state.previous_sentence = opening_narrative_en
        state.previous_sentence_zh = opening_narrative_zh
        
        print("✨ NEW BILINGUAL STORY CREATED!")
        print(f"   Story ID: {state.story_id}")
        print(f"   Opening (ZH): '{opening_narrative_zh[:50]}...'")
        print(f"   Opening (EN): '{opening_narrative_en[:50]}...'")
    else:
        # Handle the case where opening_result is now a dict with content and token_usage
        if isinstance(opening_result, dict) and "content" in opening_result:
            opening_narrative = opening_result["content"]
            token_usage = opening_result.get("token_usage", {})
        else:
            opening_narrative = opening_result
            token_usage = {}
        
        # Record with token usage
        state.narrative_thread.append({
            "turn": 0,
            "roll": None,
            "action_type": "opening",
            "elements": {"cosmic_element": state.cosmic_position},
            "narrative": opening_narrative,
            "narrative_zh": opening_narrative if language == Language.CHINESE else "",
            "token_usage": token_usage
        })
        
        if language == Language.CHINESE:
            state.previous_sentence_zh = opening_narrative
        else:
            state.previous_sentence = opening_narrative
        
        print("✨ NEW STORY CREATED!")
        print(f"   Story ID: {state.story_id}")
        print(f"   Opening narrative: '{opening_narrative[:100]}...'")
    
    # Save as active story
    with open('./cache/active_story.pkl', 'wb') as f:
        pickle.dump(state, f)
    
    print_separator()
    
    # Return response based on language
    if language == Language.BILINGUAL and isinstance(opening_result, dict):
        return jsonify({
            "message": "New bilingual story started",
            "story_id": state.story_id,
            "opening_narrative_zh": opening_result["zh"],
            "opening_narrative_en": opening_result["en"],
            "cosmic_position": state.cosmic_position,
            "seed_from": previous_id if previous_id else "random",
            "language": language
        })
    else:
        return jsonify({
            "message": "New story started",
            "story_id": state.story_id,
            "opening_narrative": opening_narrative,
            "cosmic_position": state.cosmic_position,
            "seed_from": previous_id if previous_id else "random",
            "language": language
        })

@app.route('/next_turn', methods=['POST'])
def next_turn():
    """Generate the next turn of the current story with token tracking"""
    print_separator()
    print("⏭️  NEXT TURN REQUESTED")
    
    # Load active story
    try:
        with open('./cache/active_story.pkl', 'rb') as f:
            state = pickle.load(f)
        print("✅ Active story loaded")
        print_story_status(state)
    except FileNotFoundError:
        print("❌ ERROR: No active story found")
        return jsonify({"error": "No active story found. Please start a new story first."}), 404
    
    language = state.language
    
    # Check if story is already completed
    if state.current_turn >= state.max_turns:
        print("🏁 Story already completed")
        return jsonify({"error": "Story is already completed", "story_id": state.story_id}), 400
    
    # Roll the die
    roll, action_type = story_engine.die.roll()
    print(f"🎲 DIE ROLLED: {roll} → {action_type}")
    
    # Get cosmic position
    current_element = story_engine.get_cosmic_position(state)
    state.cosmic_position = current_element
    print(f"🌟 Cosmic position advanced to: {current_element}")
    
    # Select elements for this turn based on language
    selected_elements = story_engine.select_elements(action_type, current_element, language)
    print(f"🎴 ELEMENTS SELECTED:")
    for key, value in selected_elements.items():
        if isinstance(value, dict) and 'zh' in value and 'en' in value:
            if language == Language.BILINGUAL:
                print(f"   {key}: {value['zh']} / {value['en']}")
            else:
                print(f"   {key}: {value['zh'] if language == Language.CHINESE else value['en']}")
        else:
            print(f"   {key}: {value}")
    print()
    
    # Create prompt for the narrative
    prompt = story_engine.create_prompt(state, selected_elements, action_type)
    print("📋 PROMPT CREATED")
    print(f"   Action type: {action_type}")
    print(f"   Cosmic element: {current_element}")
    print()
    
    # Generate narrative using API
    print("🖋️  GENERATING NARRATIVE...")
    narrative_result = generate_narrative_with_llm(prompt, language)
    
    # Handle different response formats based on language
    if language == Language.BILINGUAL and isinstance(narrative_result, dict) and "zh" in narrative_result:
        narrative_zh = narrative_result["zh"]
        narrative_en = narrative_result["en"]
        token_usage = narrative_result.get("token_usage", {})
        
        # Update state
        state.current_turn += 1
        state.previous_sentence = narrative_en
        state.previous_sentence_zh = narrative_zh
        
        # Add to narrative thread
        state.narrative_thread.append({
            "turn": state.current_turn,
            "roll": roll,
            "action_type": action_type,
            "elements": selected_elements,
            "narrative": narrative_en,
            "narrative_zh": narrative_zh,
            "token_usage": token_usage
        })
        
        print("✍️  BILINGUAL NARRATIVE ADDED TO STORY")
        print(f"   Turn: {state.current_turn}")
        print(f"   Text (ZH): '{narrative_zh[:50]}...'")
        print(f"   Text (EN): '{narrative_en[:50]}...'")
        print(f"   Tokens used: {token_usage.get('total_tokens', 'unknown')}")
    else:
        # Handle the case where narrative_result is now a dict with content and token_usage
        if isinstance(narrative_result, dict) and "content" in narrative_result:
            narrative = narrative_result["content"]
            token_usage = narrative_result.get("token_usage", {})
        else:
            narrative = narrative_result
            token_usage = {}
        
        # Update state
        state.current_turn += 1
        if language == Language.CHINESE:
            state.previous_sentence_zh = narrative
        else:
            state.previous_sentence = narrative
        
        # Add to narrative thread
        state.narrative_thread.append({
            "turn": state.current_turn,
            "roll": roll,
            "action_type": action_type,
            "elements": selected_elements,
            "narrative": narrative if language != Language.CHINESE else "",
            "narrative_zh": narrative if language == Language.CHINESE else "",
            "token_usage": token_usage
        })
        
        print("✍️  NARRATIVE ADDED TO STORY")
        print(f"   Turn: {state.current_turn}")
        print(f"   Text: '{narrative[:100]}...'")
        print(f"   Tokens used: {token_usage.get('total_tokens', 'unknown')}")
    print()
    
    # Check if story should end
    if roll == 18 or state.current_turn >= state.max_turns:
        print("🏁 STORY ENDING TRIGGERED")
        
        # Generate an ending if needed
        if roll == 18:
            print("   Reason: Die rolled 18 (forced ending)")
            
            # Your existing ending prompt generation code...
            
            print("📜 GENERATING FINAL ENDING...")
            ending_result = generate_narrative_with_llm(ending_prompt, language)
            
            # Handle different response formats based on language
            if language == Language.BILINGUAL and isinstance(ending_result, dict) and "zh" in ending_result:
                ending_narrative_zh = ending_result["zh"]
                ending_narrative_en = ending_result["en"]
                ending_token_usage = ending_result.get("token_usage", {})
                
                state.narrative_thread.append({
                    "turn": state.current_turn + 1,
                    "roll": roll,
                    "action_type": "ending",
                    "elements": selected_elements,
                    "narrative": ending_narrative_en,
                    "narrative_zh": ending_narrative_zh,
                    "token_usage": ending_token_usage
                })
                
                print(f"   Ending (ZH): '{ending_narrative_zh[:50]}...'")
                print(f"   Ending (EN): '{ending_narrative_en[:50]}...'")
                print(f"   Tokens used: {ending_token_usage.get('total_tokens', 'unknown')}")
            else:
                # Handle the case where ending_result is now a dict with content and token_usage
                if isinstance(ending_result, dict) and "content" in ending_result:
                    ending_narrative = ending_result["content"]
                    ending_token_usage = ending_result.get("token_usage", {})
                else:
                    ending_narrative = ending_result
                    ending_token_usage = {}
                
                state.narrative_thread.append({
                    "turn": state.current_turn + 1,
                    "roll": roll,
                    "action_type": "ending",
                    "elements": selected_elements,
                    "narrative": ending_narrative if language != Language.CHINESE else "",
                    "narrative_zh": ending_narrative if language == Language.CHINESE else "",
                    "token_usage": ending_token_usage
                })
                
                print(f"   Ending: '{ending_narrative[:100]}...'")
                print(f"   Tokens used: {ending_token_usage.get('total_tokens', 'unknown')}")
        else:
            print(f"   Reason: Reached max turns ({state.max_turns})")
        
        # Calculate total token usage for the story
        total_prompt_tokens = sum(turn.get('token_usage', {}).get('prompt_tokens', 0) for turn in state.narrative_thread)
        total_completion_tokens = sum(turn.get('token_usage', {}).get('completion_tokens', 0) for turn in state.narrative_thread)
        total_tokens = sum(turn.get('token_usage', {}).get('total_tokens', 0) for turn in state.narrative_thread)
        
        print(f"📊 TOTAL TOKEN USAGE FOR STORY:")
        print(f"   Prompt tokens: {total_prompt_tokens}")
        print(f"   Completion tokens: {total_completion_tokens}")
        print(f"   Total tokens: {total_tokens}")
        
        # Save completed story with token usage
        story_data = {
            "id": state.story_id,
            "completed_at": datetime.now().isoformat(),
            "final_narrative": state.narrative_thread,
            "cosmic_position": state.cosmic_position,
            "total_turns": state.current_turn,
            "max_turns": state.max_turns,
            "language": state.language,
            "token_usage": {
                "prompt_tokens": total_prompt_tokens,
                "completion_tokens": total_completion_tokens,
                "total_tokens": total_tokens
            }
        }
        
        # Ensure stories directory exists
        os.makedirs("./stories", exist_ok=True)
        
        filepath = f"./stories/{state.story_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(story_data, f, ensure_ascii=False, indent=2)
            
        print(f"💾 STORY SAVED: {state.story_id}.json")
        
        # Clear active story
        os.remove('./cache/active_story.pkl')
        print("🗑️  Active story cache cleared")
        
        # Print final story
        print("\n📚 COMPLETE STORY:")
        print_separator()
        
        # Your existing code for printing the story...
        
        # Prepare response based on language with token usage
        token_usage_data = {
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "total_tokens": total_tokens
        }
        
        if language == Language.BILINGUAL:
            complete_narrative_zh = [turn.get("narrative_zh", "") for turn in state.narrative_thread if "narrative_zh" in turn]
            complete_narrative_en = [turn.get("narrative", "") for turn in state.narrative_thread if "narrative" in turn]
            
            return jsonify({
                "status": "completed",
                "story_id": state.story_id,
                "final_narrative_zh": state.narrative_thread[-1].get("narrative_zh", ""),
                "final_narrative_en": state.narrative_thread[-1].get("narrative", ""),
                "total_turns": state.current_turn,
                "complete_story_zh": complete_narrative_zh,
                "complete_story_en": complete_narrative_en,
                "language": language,
                "token_usage": token_usage_data
            })
        elif language == Language.CHINESE:
            return jsonify({
                "status": "completed",
                "story_id": state.story_id,
                "final_narrative": state.narrative_thread[-1].get("narrative_zh", ""),
                "total_turns": state.current_turn,
                "complete_story": [turn.get("narrative_zh", "") for turn in state.narrative_thread if "narrative_zh" in turn],
                "language": language,
                "token_usage": token_usage_data
            })
        else:
            return jsonify({
                "status": "completed",
                "story_id": state.story_id,
                "final_narrative": state.narrative_thread[-1].get("narrative", ""),
                "total_turns": state.current_turn,
                "complete_story": [turn.get("narrative", "") for turn in state.narrative_thread if "narrative" in turn],
                "language": language,
                "token_usage": token_usage_data
            })
    
    # Save updated state
    with open('./cache/active_story.pkl', 'wb') as f:
        pickle.dump(state, f)
    print("💾 Story state saved")
    
    print_separator()
    
    # Prepare response based on language with token usage for this turn
    current_token_usage = state.narrative_thread[-1].get("token_usage", {})
    
    # Prepare response based on language with token usage
    if language == Language.BILINGUAL and isinstance(narrative_result, dict) and "zh" in narrative_result:
        narrative_zh = narrative_result["zh"]
        narrative_en = narrative_result["en"]
        
        return jsonify({
            "status": "continuing",
            "turn": state.current_turn,
            "roll": roll,
            "action_type": action_type,
            "elements": selected_elements,
            "narrative_zh": narrative_zh,
            "narrative_en": narrative_en,
            "cosmic_position": state.cosmic_position,
            "remaining_turns": state.max_turns - state.current_turn,
            "language": language,
            "token_usage": current_token_usage
        })
    else:
        # Get the content if narrative_result is a dict
        narrative_content = narrative_result.get("content", narrative_result) if isinstance(narrative_result, dict) else narrative_result
        
        return jsonify({
            "status": "continuing",
            "turn": state.current_turn,
            "roll": roll,
            "action_type": action_type,
            "elements": selected_elements,
            "narrative": narrative_content,
            "cosmic_position": state.cosmic_position,
            "remaining_turns": state.max_turns - state.current_turn,
            "language": language,
            "token_usage": current_token_usage
        })

@app.route('/get_story/<story_id>', methods=['GET'])
def get_story(story_id):
    """Retrieve a specific completed story"""
    print(f"\n📖 Fetching story: {story_id}")
    try:
        with open(f"./stories/{story_id}.json", 'r', encoding='utf-8') as f:
            story_data = json.load(f)
        print("✅ Story found and returned")
        return jsonify(story_data)
    except FileNotFoundError:
        print("❌ Story not found")
        return jsonify({"error": "Story not found"}), 404

@app.route('/list_stories', methods=['GET'])
def list_stories():
    """List all completed stories"""
    print("\n📚 Listing all stories")
    story_files = [f.replace('.json', '') for f in os.listdir("./stories") if f.endswith('.json')]
    story_files.sort(reverse=True)  # Most recent first
    print(f"   Found {len(story_files)} stories")
    
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
    
    print(f"   Returning {len(stories)} stories")
    return jsonify({"stories": stories})

@app.route('/active_story', methods=['GET'])
def get_active_story():
    """Get the current active story state"""
    print("\n📊 Checking active story")
    try:
        with open('./cache/active_story.pkl', 'rb') as f:
            state = pickle.load(f)
        
        print("✅ Active story found")
        print_story_status(state)
        
        return jsonify({
            "story_id": state.story_id,
            "current_turn": state.current_turn,
            "max_turns": state.max_turns,
            "cosmic_position": state.cosmic_position,
            "narrative_so_far": [turn["narrative"] for turn in state.narrative_thread]
        })
    except FileNotFoundError:
        print("❌ No active story")
        return jsonify({"message": "No active story"}), 404

@app.route('/roll_die', methods=['POST'])
def roll_die():
    """Roll the D18 die independently (for testing)"""
    roll, action_type = story_engine.die.roll()
    print(f"\n🎲 Independent die roll: {roll} → {action_type}")
    return jsonify({
        "roll": roll,
        "action_type": action_type
    })

if __name__ == '__main__':
    # Make sure you have OpenAI API key set in .env file
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment variables")
        print("   Make sure to create a .env file with your OpenAI API key")
    else:
        print("✅ OpenAI API key found")
    
    print("\n🚀 Starting Folktale Generator API...")
    print("   Host: 0.0.0.0")
    print("   Port: 5000")
    print()
    
    app.run(host='0.0.0.0', port=5555, debug=True)

@app.route('/language/<lang>', methods=['POST'])
def set_language(lang):
    """Set language for current story"""
    print(f"\n🌍 Setting language to: {lang}")
    
    try:
        with open('./cache/active_story.pkl', 'rb') as f:
            state = pickle.load(f)
            
        if lang.lower() in ["zh", "chinese"]:
            state.language = Language.CHINESE
        elif lang.lower() in ["both", "bilingual"]:
            state.language = Language.BILINGUAL
        else:
            state.language = Language.ENGLISH
            
        with open('./cache/active_story.pkl', 'wb') as f:
            pickle.dump(state, f)
            
        print(f"✅ Language updated to: {state.language}")
        return jsonify({"message": f"Language set to {state.language}", "language": state.language})
        
    except FileNotFoundError:
        print("❌ No active story found")
        return jsonify({"error": "No active story found. Please start a new story first."}), 404

