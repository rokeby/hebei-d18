from flask import Flask, jsonify, request
import random
import json
import pickle
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import re

# Import from new modular structure
from config import API_HOST, API_PORT, API_DEBUG
from engine import StoryEngine, StoryState
from utils.language import Language, parse_bilingual_response
from utils.logging import print_story_status
from narrative.arc import StoryArc

load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client and story engine

client = OpenAI(
    base_url="https://api.deepseek.com",
    timeout=120.0  # Increase timeout to 120 seconds
    )
story_engine = StoryEngine()

# Ensure required directories exist
os.makedirs('./cache', exist_ok=True)
os.makedirs('./stories', exist_ok=True)

def print_separator():
    """Print a visual separator for readability"""
    print("\n" + "="*60 + "\n")

def generate_narrative_with_llm(prompt: str, language=Language.ENGLISH, system_prompt: str = None) -> dict:
    """Generate narrative using DeepSeek API, handling bilingual content and tracking token usage"""
    try:
        if system_prompt is None:
            if language == Language.CHINESE:
                system_prompt = """

                你是一位精通汉代历史和文化的故事大师。
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
                
                请保持故事段落简洁(2-3句)但生动。

                """
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
                
                Keep each narrative turn concise (2-3 sentences) but evocative.]
                """
            elif language == Language.BILINGUAL:
                system_prompt = """You are a master storyteller specializing in Han dynasty Chinese folktales. You are fully bilingual in Chinese and English.

                IMPORTANT FORMAT INSTRUCTIONS:
                1. First write your narrative in Chinese under a "Chinese Version:" heading
                2. Then provide the English translation under an "English Translation:" heading
                
                Do NOT include the headings in the actual narrative content. Keep each version separate and clearly marked.
                
                Your stories should incorporate authentic elements:
                - Wu Xing (Five Elements) theory (五行)
                - Classical Chinese mythology and cosmology (中国古代神话和宇宙观)
                - Han dynasty cultural references (汉代文化元素)
                
                Write in a style that:
                - Captures the essence of ancient Chinese storytelling
                - Remains culturally appropriate in both languages
                - Maintains consistency between versions
                
                Keep your narrative concise (2-3 sentences in each language).
                """
        
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

        # Use regex to check for Chinese characters
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', narrative))
        
        # Log the details
        print("\n📄 RAW RESPONSE FROM LLM:")
        print(f"First 200 chars: {narrative[:200]}")
        print(f"Length: {len(narrative)} characters")
        print(f"Contains Chinese characters: {has_chinese}")   

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

        if language == Language.BILINGUAL:
            try:
                parsed = parse_bilingual_response(narrative)
                print("\n📊 PARSED BILINGUAL RESULT:")
                print(f"Chinese content length: {len(parsed['zh'])} chars")
                print(f"English content length: {len(parsed['en'])} chars")
                print(f"Chinese sample: {parsed['zh'][:100]}")
                print(f"English sample: {parsed['en'][:100]}")
                # Make sure we have values for both languages, even if empty
                return {
                    "zh": parsed.get("zh", ""), 
                    "en": parsed.get("en", ""),
                    "token_usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens
                    }
                }
            except Exception as e:
                print(f"❌ Error parsing bilingual response: {e}")
                # Provide a fallback
                return {
                    "zh": "[错误: 无法解析双语响应]",
                    "en": "[Error: Unable to parse bilingual response]",
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
    """Start a new story with language option and story arc choice"""
    print_separator()
    print("🚀 STARTING NEW STORY")
    
    try:
        # Get language preference, story arc, and previous story ID
        request_data = request.json if request.is_json else {}
        language = request_data.get('language', Language.ENGLISH)
        arc_type = request_data.get('arc_type')  # Optional arc type
        previous_id = request_data.get('previous_story_id')
        
        print(f"   Language: {language}")
        if arc_type:
            print(f"   Story Arc: {arc_type}")
        else:
            print("   Story Arc: Random")
        print(f"   Previous story ID: {previous_id or 'None (fresh start)'}")
        
        seed_data = story_engine.get_story_seed_from_previous(previous_id)
        print(f"   Seed source: {'Previous story' if previous_id else 'Random seed'}")
        
        # Create new story state with language preference and story arc
        state = StoryState(language=language)
        
        # NEW: Set story_engine reference
        state.story_engine = story_engine  
        
        if arc_type:
            # Verify arc_type is valid
            if arc_type in StoryArc.ARC_TYPES:
                state.story_arc = StoryArc(arc_type=arc_type, max_turns=state.max_turns)
            else:
                print(f"   Invalid arc type '{arc_type}'. Using random arc type.")
                state.story_arc = StoryArc(max_turns=state.max_turns)
        else:
            state.story_arc = StoryArc(max_turns=state.max_turns)
        
        # Print selected arc information
        print(f"   Selected arc: {state.story_arc.arc_type}")
        print(f"   Arc stages: {' → '.join(state.story_arc.stages)}")
        print(f"   Thematic elements: {state.story_arc.theme_elements}")
        print(f"   Motifs: {state.story_arc.motifs}")
        
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
        
        # CHANGED: Use story_engine to create opening prompt
        opening_prompt = story_engine.create_opening_prompt(state)
        
        print("📝 GENERATING OPENING NARRATIVE")
        opening_result = generate_narrative_with_llm(opening_prompt, language)
        
        # Handle different response formats based on language
        if language == Language.BILINGUAL and isinstance(opening_result, dict) and "zh" in opening_result:
            opening_narrative_zh = opening_result.get("zh", "")
            opening_narrative_en = opening_result.get("en", "")
            token_usage = opening_result.get("token_usage", {})
            
            # Add fallbacks for empty content
            if not opening_narrative_zh:
                opening_narrative_zh = "[无法生成故事]"
            if not opening_narrative_en:
                opening_narrative_en = "[Unable to generate narrative]"

            elif language == Language.CHINESE:
                # Add debugging
                print(f"DEBUG: opening_result type: {type(opening_result)}")
                print(f"DEBUG: opening_result content: {opening_result}")
                
                # This is where opening_narrative is likely being set incorrectly
                if isinstance(opening_result, dict) and "content" in opening_result:
                    opening_narrative = opening_result["content"]
                else:
                    # This path is probably being taken, resulting in None
                    opening_narrative = str(opening_result) if opening_result is not None else "[Unable to generate narrative]"
                
            else:
                # Handle the case where opening_result is now a dict with content and token_usage
                if isinstance(opening_result, dict) and "content" in opening_result:
                    opening_narrative = opening_result["content"]
                    token_usage = opening_result.get("token_usage", {})
                else:
                    # Add explicit fallback for None or unexpected format
                    opening_narrative = str(opening_result) if opening_result is not None else "[Error: Unable to generate narrative]"
                    token_usage = {}
                
                # Record with token usage - with safety checks
                state.narrative_thread.append({
                    "turn": 0,
                    "roll": None,
                    "action_type": "opening",
                    "elements": {"cosmic_element": state.cosmic_position},
                    "narrative": opening_narrative,
                    "narrative_zh": opening_narrative if language == Language.CHINESE else "",
                    "token_usage": token_usage
                })
                
                # Safe printing with None check
                if opening_narrative is not None:
                    print(f"   Opening narrative: '{opening_narrative[:100]}...'")
                else:
                    print("   Opening narrative: [None]")
            
            # Update previous sentences
            state.previous_sentence = opening_narrative_en
            state.previous_sentence_zh = opening_narrative_zh
            
            print("✨ NEW BILINGUAL STORY CREATED!")
            print(f"   Story ID: {state.story_id}")
            print(f"   Opening (ZH): '{opening_narrative_zh[:50]}...'")
            print(f"   Opening (EN): '{opening_narrative_en[:50]}...'")
            
            # Save as active story
            with open('./cache/active_story.pkl', 'wb') as f:
                pickle.dump(state, f)
            
            print_separator()
            
            # Return bilingual response
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
            print(f"    Opening narrative: '{opening_narrative[:100] if opening_narrative is not None else '[None]'}...'")
            
            # Save as active story
            with open('./cache/active_story.pkl', 'wb') as f:
                pickle.dump(state, f)
            
            print_separator()
            
            # Return non-bilingual response
            return jsonify({
                "message": "New story started",
                "story_id": state.story_id,
                "opening_narrative": opening_narrative,
                "cosmic_position": state.cosmic_position,
                "seed_from": previous_id if previous_id else "random",
                "language": language
            })
    except Exception as e:
        print(f"❌ ERROR in start_story: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to start story: {str(e)}"}), 500

@app.route('/next_turn', methods=['POST'])
def next_turn():
    """Generate the next turn of the current story with token tracking"""
    print_separator()
    print("⏭️  NEXT TURN REQUESTED")
    
    # Load active story
    try:
        with open('./cache/active_story.pkl', 'rb') as f:
            state = pickle.load(f)
            
        # NEW: Ensure story_engine reference is set
        if not hasattr(state, 'story_engine'):
            state.story_engine = story_engine
            
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
    
    # Check for story arc stage advancement
    old_stage = state.story_arc.get_current_stage(language)
    stage_advanced = state.story_arc.advance_stage_if_appropriate(state.current_turn, action_type)
    new_stage = state.story_arc.get_current_stage(language)
    
    if stage_advanced:
        print(f"📖 STORY ARC ADVANCED: {old_stage} → {new_stage}")
        print(f"   New stage guidance: {state.story_arc.get_stage_guidance(language)}")
    else:
        print(f"📖 STORY ARC STAGE: {new_stage}")
    
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
    
    # Build prompt
    prompt = story_engine.build_prompt(state, selected_elements, action_type)

    # Add even more explicit instruction
    if language == Language.CHINESE:
        prompt += "\n\n【特别提示】：请从新情节直接开始，勿重复前文内容。"
    elif language == Language.ENGLISH:
        prompt += "\n\n[SPECIAL NOTE]: Start directly with new narrative development. Do not repeat previous content."
    else:  # BILINGUAL
        prompt += "\n\n[SPECIAL NOTE / 特别提示]: Start directly with new narrative development in both languages. Do not repeat previous content."

    narrative_result = generate_narrative_with_llm(prompt, language)

    # Handle different response formats based on language
    if language == Language.BILINGUAL and isinstance(narrative_result, dict) and "zh" in narrative_result:
        narrative_zh = narrative_result["zh"]
        narrative_en = narrative_result["en"]
        token_usage = narrative_result.get("token_usage", {})
        
        # Check for empty content and provide fallbacks
        if not narrative_zh.strip():
            print("⚠️ WARNING: Empty Chinese content received")
            narrative_zh = "【未能生成中文内容】"
        
        if not narrative_en.strip():
            print("⚠️ WARNING: Empty English content received")
            narrative_en = "[Unable to generate English content]"
        
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
        
        # Update previous sentences
        state.previous_sentence = narrative_en
        state.previous_sentence_zh = narrative_zh

    # Handle different response formats based on language
    elif language == Language.CHINESE:
        # Handle the case where narrative_result is now a dict with content and token_usage
        if isinstance(narrative_result, dict) and "content" in narrative_result:
            narrative = narrative_result["content"]
            token_usage = narrative_result.get("token_usage", {})
        else:
            narrative = narrative_result
            token_usage = {}
        
        # Add explicit fallback for empty response
        if not narrative or narrative.strip() == "":
            print("⚠️ WARNING: Empty narrative response received. Using fallback text.")
            narrative = "故事继续..."  # Fallback text
        
        # Log the narrative to debug
        print(f"📜 Final narrative to be saved (first 100 chars): {narrative[:100]}")
        
        # Add to narrative thread with checks
        state.narrative_thread.append({
            "turn": state.current_turn,
            "roll": roll,
            "action_type": action_type,
            "elements": selected_elements,
            "narrative": "",
            "narrative_zh": narrative,
            "token_usage": token_usage
        })
        
        # Update previous sentences
        state.previous_sentence_zh = narrative

    else:
        # Handle single language or other format
        if isinstance(narrative_result, dict) and "content" in narrative_result:
            narrative = narrative_result["content"]
            token_usage = narrative_result.get("token_usage", {})
        else:
            narrative = narrative_result
            token_usage = {}
        
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
        
        # Update previous sentences
        if language == Language.CHINESE:
            state.previous_sentence_zh = narrative
        else:
            state.previous_sentence = narrative
    
    state.current_turn += 1
    print(f"📈 Turn counter incremented to {state.current_turn}/{state.max_turns}")
    
    # Check if the story should end
    if story_engine.should_end_story(state, roll):
        print("🏁 STORY ENDING TRIGGERED")
        
        # Generate an ending if needed
        if roll == 18:
            print("   Reason: Die rolled 18 (forced ending)")
            
            # CHANGED: Use story_engine for ending prompt
            ending_prompt = story_engine.create_ending_prompt(state, current_element)
            
            print("📜 GENERATING FINAL ENDING...")
            ending_result = generate_narrative_with_llm(ending_prompt, language)
    print(f"   Selected arc: {state.story_arc.arc_type}")
    print(f"   Arc stages: {' → '.join(state.story_arc.stages)}")
    print(f"   Thematic elements: {state.story_arc.theme_elements}")
    print(f"   Motifs: {state.story_arc.motifs}")
        
    print(f"   Initial cosmic position: {state.cosmic_position}")
    if language == Language.CHINESE:
        print(f"   种子文本: '{state.previous_sentence_zh[:100]}...'")
    elif language == Language.ENGLISH:
        print(f"   Seed text: '{state.previous_sentence[:100]}...'")
    else:
        print(f"   Seed text (ZH): '{state.previous_sentence_zh[:50]}...'")
        print(f"   Seed text (EN): '{state.previous_sentence[:50]}...'")
    print()
    
    # CHANGED: Use story_engine to create opening prompt
    opening_prompt = story_engine.create_opening_prompt(state)
    
    print("📝 GENERATING NEXT NARRATIVE SECTION")
    opening_result = generate_narrative_with_llm(opening_prompt, language)
    
    # Save updated state
    with open('./cache/active_story.pkl', 'wb') as f:
        pickle.dump(state, f)
    print("💾 Story state saved")

    print_separator()

    # Return response based on language
    if language == Language.BILINGUAL:
        # Make sure we're not returning "[Chinese content unavailable]"
        narrative_zh = state.narrative_thread[-1].get("narrative_zh", "")
        if narrative_zh == "[Chinese content unavailable]" and "zh" in narrative_result:
            narrative_zh = narrative_result["zh"]
            
        return jsonify({
            "message": "Turn generated successfully",
            "story_id": state.story_id,
            "turn": state.current_turn - 1,
            "remaining_turns": state.max_turns - state.current_turn,
            "narrative_zh": narrative_zh,
            "narrative_en": state.narrative_thread[-1].get("narrative", ""),
            "cosmic_position": state.cosmic_position,
            "action_type": action_type,
            "elements": selected_elements
        })
    elif language == Language.CHINESE:
        # Return response for Chinese
        return jsonify({
            "message": "Turn generated successfully",
            "story_id": state.story_id,
            "turn": state.current_turn - 1,
            "remaining_turns": state.max_turns - state.current_turn,
            "narrative": "",  # Empty for Chinese-only
            "narrative_zh": narrative,  # Include the Chinese narrative
            "cosmic_position": state.cosmic_position,
            "action_type": action_type,
            "elements": selected_elements,
            "token_usage": token_usage
        })
    else:
        return jsonify({
            "message": "Turn generated successfully",
            "story_id": state.story_id,
            "turn": state.current_turn - 1,  # We've already incremented
            "remaining_turns": state.max_turns - state.current_turn,
            "narrative": state.narrative_thread[-1].get("narrative", ""),
            "cosmic_position": state.cosmic_position,
            "action_type": action_type,
            "elements": selected_elements,
            "token_usage": token_usage if 'token_usage' in locals() else {}
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

@app.route('/arc_types', methods=['GET'])
def list_arc_types():
    """List all available story arc types and their descriptions"""
    print("\n📚 Listing available story arc types")
    
    arc_types = {}
    for arc_id, arc_data in StoryArc.ARC_TYPES.items():
        arc_types[arc_id] = {
            "name": arc_id,
            "description": arc_data.get("description", ""),
            "stages": arc_data.get("stages", []),
            "zh_stages": arc_data.get("zh_stages", []),
            "related_text": arc_data.get("related_text", ""),
            "typical_motifs": arc_data.get("typical_motifs", [])
        }
    
    print(f"   Returning {len(arc_types)} arc types")
    return jsonify({
        "arc_types": arc_types,
        "total": len(arc_types),
        "usage": "Use arc_type parameter in /start_story with any of these names"
    })

@app.route('/arc_types/<arc_name>', methods=['GET'])
def get_arc_type(arc_name):
    """Get details about a specific story arc type"""
    print(f"\n📖 Fetching details for arc type: {arc_name}")
    
    if arc_name not in StoryArc.ARC_TYPES:
        print(f"❌ Arc type not found: {arc_name}")
        return jsonify({
            "error": f"Arc type '{arc_name}' not found", 
            "available_types": list(StoryArc.ARC_TYPES.keys())
        }), 404
    
    arc_data = StoryArc.ARC_TYPES[arc_name]
    
    # Create a sample arc to get more details
    sample_arc = StoryArc(arc_type=arc_name, max_turns=10)
    theme_examples = sample_arc.theme_elements
    motif_examples = sample_arc.motifs
    
    result = {
        "name": arc_name,
        "description": arc_data.get("description", ""),
        "description_zh": arc_data.get("description_zh", ""),
        "stages": arc_data.get("stages", []),
        "zh_stages": arc_data.get("zh_stages", []),
        "related_text": arc_data.get("related_text", ""),
        "typical_motifs": arc_data.get("typical_motifs", []),
        "sample_theme_elements": theme_examples,
        "sample_motifs": motif_examples
    }
    
    print("✅ Arc details returned")
    return jsonify(result)

if __name__ == '__main__':
    # Make sure you have OpenAI API key set in .env file
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment variables")
        print("   Make sure to create a .env file with your OpenAI API key")
    else:
        print("✅ OpenAI API key found")
    
    print("\n🚀 Starting Folktale Generator API...")
    print(f"   Host: {API_HOST}")
    print(f"   Port: {API_PORT}")
    print()

    app.config['TIMEOUT'] = 30  # secs timeout
    app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)

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

