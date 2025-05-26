#!/usr/bin/env python3
import requests
import json
import sys
import os
import argparse
import time
import re
from datetime import datetime

SERVER_URL = "http://localhost:5555"
AUTO_SAVE_TURNS = True  # Default value

#hello

# Try to load from config file
try:
    with open('./config.json', 'r') as f:
        config = json.load(f)
        AUTO_SAVE_TURNS = config.get("auto_save_turns", False)
except:
    pass  # Use default if file doesn't exist

def print_separator():
    """Print a visual separator"""
    print("\n" + "="*80 + "\n")

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"  {title}  ".center(80, "="))
    print("="*80 + "\n")

def start_story(language="en", arc_type=None, previous_story_id=None):
    """Start a new folktale story"""
    print("📚 STARTING NEW STORY")
    
    # Prepare request data
    data = {"language": language}
    if arc_type:
        data["arc_type"] = arc_type
    if previous_story_id:
        data["previous_story_id"] = previous_story_id
    
    # Make the request
    try:
        print(f"DEBUG: Sending data to server: {data}")
        
        response = requests.post(f"{SERVER_URL}/start_story", 
                                 json=data, 
                                 headers={"Content-Type": "application/json"})
        
        if response.status_code != 200:
            print(f"❌ Error: Server returned status code {response.status_code}")
            print(response.text)
            return None
        
        story_data = response.json()
        
        print(f"DEBUG: API Response length: {len(str(story_data))} characters")
        
        display_story_turn(story_data, is_opening=True)
        
        # For Chinese stories, save the opening narrative to a continuous file
        if language == "zh":
            # Check for Chinese content in various fields
            chinese_content = None
            
            # First check for opening_narrative_zh
            if "opening_narrative_zh" in story_data and story_data["opening_narrative_zh"]:
                chinese_content = story_data["opening_narrative_zh"]
                print("Found Chinese content in opening_narrative_zh")
            # Then check for narrative (which seems to be where it actually is)
            elif "narrative" in story_data and story_data["narrative"]:
                # Check if narrative contains Chinese
                chinese_chars = sum(1 for char in story_data["narrative"] if '\u4e00' <= char <= '\u9fff')
                if chinese_chars > 0:
                    chinese_content = story_data["narrative"]
                    print(f"Found Chinese content in narrative ({chinese_chars} Chinese chars)")
            
            # If we found Chinese content, save it
            if chinese_content:
                print("🔄 Chinese opening narrative detected - saving to continuous file...")
                
                # Create archive directory
                archive_dir = "./archived_tales"
                os.makedirs(archive_dir, exist_ok=True)
                
                # Get story ID 
                story_id = story_data.get("story_id", "unknown")
                
                # Define continuous file name based on story ID
                continuous_file = os.path.join(archive_dir, f"continuous_zh_{story_id}.txt")
                
                # Create or append to the continuous file
                try:
                    # Always create a new file for opening
                    with open(continuous_file, 'w', encoding='utf-8') as f:
                        # Add story header
                        f.write(f"FOLKTALE STORY: {story_id}\n")
                        f.write(f"Started: {datetime.now()}\n")
                        f.write("-" * 40 + "\n\n")
                        
                        # Add opening content
                        f.write("--- Opening ---\n\n")
                        f.write(chinese_content + "\n")
                    
                    print(f"✅ Chinese opening narrative saved to: {continuous_file}")
                except Exception as e:
                    print(f"❌ Error saving Chinese opening: {str(e)}")
        
        return story_data
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Could not connect to the server at {SERVER_URL}")
        print("   Make sure the API server is running.")
        return None
    except json.JSONDecodeError:
        print("❌ Error: Server returned invalid JSON")
        print(f"Raw response: {response.text[:200]}...")
        return None
    except Exception as e:
        print(f"❌ Error starting story: {str(e)}")
        return None

def examine_api_response(endpoint, method="GET", data=None):
    """Directly examine an API response for debugging"""
    print(f"🔍 Examining API endpoint: {endpoint}")
    
    try:
        url = f"{SERVER_URL}/{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        print(f"Status code: {response.status_code}")
        
        try:
            json_data = response.json()
            print("Response is valid JSON")
            print(f"Keys: {list(json_data.keys())}")
            print("Sample values:")
            for key, value in json_data.items():
                if isinstance(value, str):
                    print(f"  {key}: {value[:50]}...")
                else:
                    print(f"  {key}: {type(value)}")
        except:
            print("Response is not valid JSON")
            print(f"Raw response: {response.text[:500]}...")
        
        return response
        
    except Exception as e:
        print(f"❌ Error examining API: {str(e)}")
        return None

def display_story_turn(data, is_opening=False):
    """Display story content in a well-formatted way with bilingual support"""
    print_separator()
    
    # Debug the structure of the data received
    print("DEBUG: Response data structure:")
    keys = list(data.keys())
    print(f"Keys: {keys}")
    
    # Determine what content we have
    has_chinese = "narrative_zh" in keys and data["narrative_zh"]
    has_english = "narrative_en" in keys and data["narrative_en"]
    has_single_narrative = "narrative" in keys and data["narrative"]
    
    # Handle opening narrative naming
    if is_opening:
        if "opening_narrative_zh" in keys and data["opening_narrative_zh"]:
            has_chinese = True
            data["narrative_zh"] = data["opening_narrative_zh"]
        if "opening_narrative_en" in keys and data["opening_narrative_en"]:
            has_english = True
            data["narrative_en"] = data["opening_narrative_en"]
        if "opening_narrative" in keys and data["opening_narrative"]:
            has_single_narrative = True
            data["narrative"] = data["opening_narrative"]
    
    # Check for narrative in narrative_thread for last turn
    if "narrative_thread" in keys and data["narrative_thread"]:
        thread = data["narrative_thread"]
        if thread:
            last_turn = thread[-1]
            if "narrative_zh" in last_turn and last_turn["narrative_zh"]:
                has_chinese = True
                data["narrative_zh"] = last_turn["narrative_zh"]
                print("DEBUG: Found Chinese in last turn of narrative_thread")
            if "narrative" in last_turn and last_turn["narrative"]:
                if not has_english:  # Only override if we don't already have English
                    has_single_narrative = True
                    data["narrative"] = last_turn["narrative"]
                    print("DEBUG: Found narrative in last turn of narrative_thread")
    
    # Display Chinese content if available
    if has_chinese:
        print("\n🇨🇳 CHINESE NARRATIVE:")
        print(data["narrative_zh"])
        
        # Additional debug
        chinese_chars = sum(1 for char in data["narrative_zh"] if '\u4e00' <= char <= '\u9fff')
        print(f"DEBUG: Chinese narrative has {len(data['narrative_zh'])} total chars, {chinese_chars} Chinese chars")
    
    # Display English content if available
    if has_english:
        print("\n🇬🇧 ENGLISH NARRATIVE:")
        print(data["narrative_en"])
    elif has_single_narrative:
        print("\n📖 NARRATIVE:")
        print(data["narrative"])
        
        # Check if narrative might contain Chinese content
        chinese_chars = sum(1 for char in data["narrative"] if '\u4e00' <= char <= '\u9fff')
        if chinese_chars > 0 and not has_chinese:
            print(f"\nDEBUG: The 'narrative' field contains {chinese_chars} Chinese characters!")
            # Try to split it
            parts = split_bilingual_text(data["narrative"])
            if parts["zh"]:
                print("\n🇨🇳 EXTRACTED CHINESE CONTENT:")
                print(parts["zh"])
    
    # If no narrative content found, display a warning
    if not (has_chinese or has_english or has_single_narrative):
        print("\n⚠️ NO NARRATIVE CONTENT FOUND")
        
        # Try to extract from narrative_thread
        if "narrative_thread" in keys and data["narrative_thread"]:
            print("\nTrying to extract from narrative_thread...")
            thread = data["narrative_thread"]
            
            for i, turn in enumerate(thread):
                print(f"Turn {i} keys: {list(turn.keys())}")
                for key in turn.keys():
                    if "narrative" in key.lower() and turn[key]:
                        print(f"Turn {i} {key}: {turn[key][:50]}...")
    
    print_separator()
    
    # Print story metadata
    if is_opening:
        print(f"Story ID: {data.get('story_id', 'unknown')}")
        print(f"Language: {data.get('language', 'unknown')}")
        print(f"Seed Source: {data.get('seed_from', 'random')}")
    else:
        turn = data.get('turn', '?')
        remaining = data.get('remaining_turns', '?')
        total = int(turn) + int(remaining) if isinstance(turn, int) and isinstance(remaining, int) else '?'
        
        print(f"Turn: {turn}/{total}")
        print(f"Cosmic Position: {data.get('cosmic_position', 'unknown')}")
        print(f"Action Type: {data.get('action_type', 'unknown')}")
        
        # Print selected story elements if available
        if "elements" in data:
            print("\nElements in this turn:")
            for key, value in data["elements"].items():
                if key != "cosmic_element":  # Already displayed above
                    if isinstance(value, dict) and "zh" in value and "en" in value:
                        print(f"  {key}: {value['zh']} / {value['en']}")
                    else:
                        print(f"  {key}: {value}")

    # Print token usage if available
    if "token_usage" in data and data["token_usage"]:
        print(f"\nToken Usage: {data['token_usage'].get('total_tokens', '?')} tokens")

def get_story_arcs():
    """Get list of available story arc types"""
    try:
        response = requests.get(f"{SERVER_URL}/arc_types")
        
        if response.status_code != 200:
            print(f"❌ Error: Server returned status code {response.status_code}")
            print(response.text)
            return {}
        
        arc_data = response.json()
        return arc_data.get("arc_types", {})
    
    except Exception as e:
        print(f"❌ Error retrieving story arcs: {e}")
        return {}

def list_story_arcs():
    """Display available story arc types"""
    arc_types = get_story_arcs()
    
    if not arc_types:
        print("❌ Could not retrieve story arc types.")
        return
    
    print_header("AVAILABLE STORY ARCS")
    
    for arc_id, arc_info in arc_types.items():
        print(f"🔹 {arc_id}")
        print(f"   Description: {arc_info.get('description', 'No description')}")
        print(f"   Stages: {' → '.join(arc_info.get('stages', []))}")
        if "typical_motifs" in arc_info and arc_info["typical_motifs"]:
            print(f"   Motifs: {', '.join(arc_info.get('typical_motifs', []))}")
        print()

def next_turn():
    """Generate the next turn with metadata and continuous file saving for Chinese"""
    print("⏭️ GENERATING NEXT TURN")
    
    try:
        # Make request to the API
        response = requests.post(f"{SERVER_URL}/next_turn")
        
        # Check for error
        if response.status_code != 200:
            print(f"❌ Error: Server returned status code {response.status_code}")
            return None
        
        # Parse the response
        story_data = response.json()
        
        # Capture metadata that would be displayed
        metadata_lines = []
        
        # Story status metadata
        story_id = story_data.get("story_id", "unknown")
        turn = story_data.get("turn", "?")
        remaining = story_data.get("remaining_turns", "?")
        total = int(turn) + int(remaining) if isinstance(turn, int) and isinstance(remaining, int) else "?"
        cosmic_pos = story_data.get("cosmic_position", "unknown")
        language = story_data.get("language", "unknown")
        action_type = story_data.get("action_type", "unknown")
        
        metadata_lines.append("📖 STORY STATUS:")
        metadata_lines.append(f"   ID: {story_id}")
        metadata_lines.append(f"   Turn: {turn}/{total}")
        metadata_lines.append(f"   Cosmic Position: {cosmic_pos}")
        metadata_lines.append(f"   Language: {language}")
        
        # Add action type info (simulating die roll display)
        metadata_lines.append(f"🎲 ACTION TYPE: {action_type}")
        metadata_lines.append(f"🌟 Cosmic position: {cosmic_pos}")
        
        # Add elements if available
        if "elements" in story_data and story_data["elements"]:
            metadata_lines.append("🎴 ELEMENTS SELECTED:")
            for key, value in story_data["elements"].items():
                if isinstance(value, dict) and "zh" in value and "en" in value:
                    if language == "zh":
                        metadata_lines.append(f"   {key}: {value['zh']}")
                    else:
                        metadata_lines.append(f"   {key}: {value['zh']} / {value['en']}")
                else:
                    metadata_lines.append(f"   {key}: {value}")
        
        # Join metadata
        metadata_text = "\n".join(metadata_lines) + "\n\n"
        
        # Display the story turn
        display_story_turn(story_data)
        
        # Check if this is a Chinese story with content
        if "narrative_zh" in story_data and story_data["narrative_zh"]:
            print("🔄 Chinese content detected - saving to continuous file...")
            
            # Create archive directory
            archive_dir = "./archived_tales"
            os.makedirs(archive_dir, exist_ok=True)
            
            # Get story ID and turn number
            turn_num = story_data.get("turn", 0)
            
            # Adjust turn number for display (API returns 0 for second turn)
            display_turn_num = turn_num + 1
            
            # Define continuous file name based on story ID
            continuous_file = os.path.join(archive_dir, f"continuous_zh_{story_id}.txt")
            
            # Append to the continuous file with metadata
            try:
                # Check if file exists
                is_new_file = not os.path.exists(continuous_file)
                
                with open(continuous_file, 'a', encoding='utf-8') as f:
                    # Add header if this is a new file (shouldn't happen normally since opening creates it)
                    if is_new_file:
                        f.write(f"FOLKTALE STORY: {story_id}\n")
                        f.write(f"Started: {datetime.now()}\n")
                        f.write("-" * 40 + "\n\n")
                    
                    # Add turn header with metadata
                    f.write(f"\n--- Turn {display_turn_num} ---\n\n")
                    f.write(metadata_text)  # Add the metadata here
                    f.write(story_data["narrative_zh"] + "\n")
                
                print(f"✅ Chinese content with metadata appended to: {continuous_file}")
            except Exception as e:
                print(f"❌ Error saving Chinese content: {str(e)}")
        
        # Continue with normal flow
        if story_data.get('remaining_turns', 1) <= 0:
            print("🏁 Story has reached its conclusion!")
            
        return story_data
    
    except Exception as e:
        print(f"❌ Error generating next turn: {str(e)}")
        return None

def check_active_story():
    """Check if there's an active story and display its status with improved bilingual support"""
    try:
        response = requests.get(f"{SERVER_URL}/active_story")
        
        if response.status_code != 200:
            if response.status_code == 404:
                print("ℹ️ No active story found. Use 'start' to begin a new story.")
            else:
                print(f"❌ Error: Server returned status code {response.status_code}")
                print(response.text)
            return None
        
        story_data = response.json()
        
        print_header("ACTIVE STORY STATUS")
        
        print(f"Story ID: {story_data.get('story_id', 'unknown')}")
        print(f"Current Turn: {story_data.get('current_turn', '?')}/{story_data.get('max_turns', '?')}")
        print(f"Cosmic Position: {story_data.get('cosmic_position', 'unknown')}")
        print(f"Language: {story_data.get('language', 'unknown')}")
        
        # Check if this is a bilingual story
        is_bilingual = story_data.get('language') == "both"
        
        # Get narrative content based on what's available
        if "narrative_thread" in story_data and story_data["narrative_thread"]:
            thread = story_data["narrative_thread"]
            if thread:
                last_turn = thread[-1]
                
                # Print keys in last turn for debugging
                print(f"DEBUG: Last turn keys: {list(last_turn.keys())}")
                
                # For bilingual stories, show both Chinese and English
                if is_bilingual:
                    if "narrative_zh" in last_turn and last_turn["narrative_zh"]:
                        print("\nLast Chinese Narrative:")
                        print(last_turn["narrative_zh"])
                    
                    if "narrative" in last_turn and last_turn["narrative"]:
                        print("\nLast English Narrative:")
                        print(last_turn["narrative"])
                else:
                    # For non-bilingual stories, show the appropriate narrative
                    if story_data.get('language') == "zh" and "narrative_zh" in last_turn:
                        print("\nLast Narrative:")
                        print(last_turn["narrative_zh"])
                    elif "narrative" in last_turn:
                        print("\nLast Narrative:")
                        print(last_turn["narrative"])
        
        # If no narrative_thread, try narrative_so_far
        elif "narrative_so_far" in story_data and story_data["narrative_so_far"]:
            print("\nLast Narrative:")
            print(story_data["narrative_so_far"][-1])
        
        return story_data
    
    except Exception as e:
        print(f"❌ Error checking active story: {e}")
        return None

def change_language(language):
    """Change the language of the active story"""
    if language not in ["en", "zh", "both"]:
        print(f"❌ Invalid language: {language}. Must be 'en', 'zh', or 'both'.")
        return False
    
    try:
        url = f"{SERVER_URL}/language/{language}"
        print(f"📡 Sending request to: {url}")
        
        response = requests.post(url)
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📄 Response content: {response.text[:100]}...")
        
        if response.status_code != 200:
            print(f"❌ Error: Server returned status code {response.status_code}")
            print(response.text)
            return False
        
        print(f"✅ Language changed to: {language}")
        return True
    
    except Exception as e:
        print(f"❌ Error changing language: {e}")
        return False

def save_story_to_file(story_data, filename=None):
    """Save the current story narrative to a file in the archived_tales directory"""
    # Create archived_tales directory if it doesn't exist
    archive_dir = "./archived_tales"
    os.makedirs(archive_dir, exist_ok=True)
    
    # Get language from story data
    language = story_data.get("language", "unknown")
    
    # Generate default filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        story_id = story_data.get("story_id", "unknown")
        filename = f"tale_{story_id}_{timestamp}"
    
    # Remove file extension if provided
    if filename.endswith(".txt"):
        filename = filename[:-4]
    
    # Determine the correct file name based on language
    if language == "zh":
        final_filename = os.path.join(archive_dir, f"zh_{filename}.txt")
    elif language == "both":
        # For bilingual stories, we'll call a separate function
        return save_bilingual_story(story_data, filename)
    else:  # default to English
        final_filename = os.path.join(archive_dir, f"en_{filename}.txt")
    
    # Common header content for all files
    header_content = f"{'=' * 80}\n"
    header_content += f"FOLKTALE STORY: {story_data.get('story_id', 'Unknown ID')}\n"
    header_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header_content += f"{'=' * 80}\n\n"
    
    # Print available keys in story_data for debugging
    print("\nDEBUG: Story Data Keys:")
    for key in story_data.keys():
        print(f"  - {key}")
    
    # Extract narrative content
    content = extract_narrative_content(story_data, language)
    
    # Save the content if we found any
    if content:
        try:
            with open(final_filename, 'w', encoding='utf-8') as f:
                f.write(header_content)
                f.write(content + "\n\n")
                f.write(f"{'-' * 40}\n")
                f.write(f"Language: {language}\n")
                f.write(f"Cosmic Position: {story_data.get('cosmic_position', 'unknown')}\n")
            
            print(f"✅ Story saved to: {final_filename}")
            return final_filename
        except Exception as e:
            print(f"❌ Error saving story: {str(e)}")
            return None
    else:
        print("❌ No content found to save")
        return None

def save_generated_narrative(data, language="en", default_filename=None):
    """Save narrative content directly from the API response data - improved version"""
    if not data:
        print("❌ No data to save")
        return None
    
    # Print keys for debugging
    print("\nDEBUG: Direct Save Analysis")
    print(f"Available keys in response: {list(data.keys())}")
    
    # Check for narrative content
    has_narrative = "narrative" in data and data["narrative"]
    has_narrative_zh = "narrative_zh" in data and data["narrative_zh"]
    
    if has_narrative:
        print(f"Has narrative: {len(data['narrative'])} chars")
    if has_narrative_zh:
        print(f"Has narrative_zh: {len(data['narrative_zh'])} chars")
    
    # Generate default filename if not provided
    if not default_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        story_id = data.get("story_id", "unknown")
        turn = data.get("turn", "0")
        default_filename = f"tale_{story_id}_turn{turn}_{timestamp}"
    
    # Ask for filename
    filename = input(f"Enter filename (without extension) [default: {default_filename}]: ").strip()
    if not filename:
        filename = default_filename
    
    # Create archived_tales directory if it doesn't exist
    archive_dir = "./archived_tales"
    os.makedirs(archive_dir, exist_ok=True)
    
    saved_files = []
    
    # Save the raw JSON data for reference
    json_filename = os.path.join(archive_dir, f"raw_{filename}.json")
    try:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        saved_files.append(json_filename)
        print(f"✅ Raw JSON data saved to: {json_filename}")
    except Exception as e:
        print(f"❌ Error saving raw data: {str(e)}")
    
    # Create a header for the text files
    header_content = f"{'=' * 80}\n"
    header_content += f"FOLKTALE STORY: {data.get('story_id', 'Unknown ID')} - Turn {data.get('turn', '0')}\n"
    header_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header_content += f"{'=' * 80}\n\n"
    
    # Save Chinese content if available
    if has_narrative_zh:
        zh_filename = os.path.join(archive_dir, f"zh_{filename}.txt")
        try:
            with open(zh_filename, 'w', encoding='utf-8') as f:
                f.write(header_content)
                f.write(data["narrative_zh"] + "\n\n")
                f.write(f"{'-' * 40}\n")
                f.write(f"Language: Chinese (zh)\n")
                f.write(f"Cosmic Position: {data.get('cosmic_position', 'unknown')}\n")
                f.write(f"Turn: {data.get('turn', '?')}/{data.get('max_turns', '?')}\n")
                # Add elements if available
                if "elements" in data:
                    f.write("Elements:\n")
                    for key, value in data["elements"].items():
                        f.write(f"  {key}: {value}\n")
            saved_files.append(zh_filename)
            print(f"✅ Chinese content saved to: {zh_filename}")
        except Exception as e:
            print(f"❌ Error saving Chinese content: {str(e)}")
    else:
        print("⚠️ No Chinese content found in API response")
    
    # Save English content if available
    if has_narrative:
        en_filename = os.path.join(archive_dir, f"en_{filename}.txt")
        try:
            with open(en_filename, 'w', encoding='utf-8') as f:
                f.write(header_content)
                f.write(data["narrative"] + "\n\n")
                f.write(f"{'-' * 40}\n")
                f.write(f"Language: English (en)\n")
                f.write(f"Cosmic Position: {data.get('cosmic_position', 'unknown')}\n")
                f.write(f"Turn: {data.get('turn', '?')}/{data.get('max_turns', '?')}\n")
                # Add elements if available
                if "elements" in data:
                    f.write("Elements:\n")
                    for key, value in data["elements"].items():
                        f.write(f"  {key}: {value}\n")
            saved_files.append(en_filename)
            print(f"✅ English content saved to: {en_filename}")
        except Exception as e:
            print(f"❌ Error saving English content: {str(e)}")
    else:
        print("⚠️ No English content found in API response")
    
    # Display the narratives we just saved
    if has_narrative_zh:
        print("\n🇨🇳 CHINESE NARRATIVE THAT WAS JUST SAVED:")
        print(data["narrative_zh"])
    
    if has_narrative:
        print("\n🇬🇧 ENGLISH NARRATIVE THAT WAS JUST SAVED:")
        print(data["narrative"])
    
    return saved_files

def save_bilingual_story(story_data=None, filename=None):
    """Save current bilingual story with separate Chinese and English files - comprehensive fix"""
    print_header("SAVING BILINGUAL STORY")
    
    # If no story data provided, get from active story
    if story_data is None:
        try:
            response = requests.get(f"{SERVER_URL}/active_story")
            if response.status_code != 200:
                print("❌ No active story found or error connecting to server")
                return None
            
            story_data = response.json()
        except Exception as e:
            print(f"❌ Error retrieving active story: {str(e)}")
            return None
    
    # Create archived_tales directory if it doesn't exist
    archive_dir = "./archived_tales"
    os.makedirs(archive_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        story_id = story_data.get('story_id', "unknown")
        filename = f"tale_{story_id}_{timestamp}"
    
    # Remove file extension if provided
    if filename.endswith(".txt"):
        filename = filename[:-4]
    
    # Common header content
    header_content = f"{'=' * 80}\n"
    header_content += f"FOLKTALE STORY: {story_data.get('story_id', 'Unknown ID')}\n"
    header_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header_content += f"{'=' * 80}\n\n"
    
    # Print detailed debug about the story data
    print("\nDEBUG: Story Data Analysis")
    print(f"Keys: {list(story_data.keys())}")
    
    # Initialize content collections
    chinese_content = []
    english_content = []
    
    # Extract content from narrative_thread if available
    if "narrative_thread" in story_data and story_data["narrative_thread"]:
        thread = story_data["narrative_thread"]
        print(f"DEBUG: Found narrative_thread with {len(thread)} turns")
        
        for i, turn in enumerate(thread):
            # Print keys in this turn for debugging
            print(f"DEBUG: Turn {i} keys: {list(turn.keys())}")
            
            # Extract Chinese content
            if "narrative_zh" in turn and turn["narrative_zh"]:
                chinese_chars = sum(1 for char in turn["narrative_zh"] if '\u4e00' <= char <= '\u9fff')
                print(f"DEBUG: Turn {i} narrative_zh has {len(turn['narrative_zh'])} chars, {chinese_chars} Chinese chars")
                chinese_content.append(f"--- Turn {i} ---\n\n{turn['narrative_zh']}")
            
            # Extract English content
            if "narrative" in turn and turn["narrative"]:
                english_content.append(f"--- Turn {i} ---\n\n{turn['narrative']}")
                print(f"DEBUG: Turn {i} narrative has {len(turn['narrative'])} chars")
    
    # If we didn't find content in the thread, try direct fields
    if not chinese_content and "narrative_zh" in story_data and story_data["narrative_zh"]:
        chinese_content.append(story_data["narrative_zh"])
        print(f"DEBUG: Found narrative_zh directly in story_data")
    
    if not english_content and "narrative_en" in story_data and story_data["narrative_en"]:
        english_content.append(story_data["narrative_en"])
        print(f"DEBUG: Found narrative_en directly in story_data")
    elif not english_content and "narrative" in story_data and story_data["narrative"]:
        english_content.append(story_data["narrative"])
        print(f"DEBUG: Found narrative directly in story_data")
    
    # Combine content
    combined_chinese = "\n\n".join(chinese_content)
    combined_english = "\n\n".join(english_content)
    
    print(f"DEBUG: Final Chinese content length: {len(combined_chinese)} chars")
    print(f"DEBUG: Final English content length: {len(combined_english)} chars")
    
    saved_files = []
    
    # Save Chinese content if available
    if combined_chinese:
        zh_filename = os.path.join(archive_dir, f"zh_{filename}.txt")
        try:
            with open(zh_filename, 'w', encoding='utf-8') as f:
                f.write(header_content)
                f.write(combined_chinese + "\n\n")
                f.write(f"{'-' * 40}\n")
                f.write(f"Language: Chinese (zh)\n")
                f.write(f"Cosmic Position: {story_data.get('cosmic_position', 'unknown')}\n")
            saved_files.append(zh_filename)
            print(f"✅ Chinese content saved to: {zh_filename}")
        except Exception as e:
            print(f"❌ Error saving Chinese version: {str(e)}")
    else:
        print("⚠️ No Chinese content found to save")
    
    # Save English content if available
    if combined_english:
        en_filename = os.path.join(archive_dir, f"en_{filename}.txt")
        try:
            with open(en_filename, 'w', encoding='utf-8') as f:
                f.write(header_content)
                f.write(combined_english + "\n\n")
                f.write(f"{'-' * 40}\n")
                f.write(f"Language: English (en)\n")
                f.write(f"Cosmic Position: {story_data.get('cosmic_position', 'unknown')}\n")
            saved_files.append(en_filename)
            print(f"✅ English content saved to: {en_filename}")
        except Exception as e:
            print(f"❌ Error saving English version: {str(e)}")
    else:
        print("⚠️ No English content found to save")
    
    # Also save a combined version
    full_filename = os.path.join(archive_dir, f"full_{filename}.txt")
    try:
        with open(full_filename, 'w', encoding='utf-8') as f:
            f.write(header_content)
            
            # Include both languages
            if combined_chinese and combined_english:
                f.write("--- CHINESE VERSION ---\n\n")
                f.write(combined_chinese + "\n\n")
                f.write("--- ENGLISH VERSION ---\n\n")
                f.write(combined_english + "\n\n")
            elif combined_chinese:
                f.write(combined_chinese + "\n\n")
            elif combined_english:
                f.write(combined_english + "\n\n")
            else:
                f.write("[No narrative content could be extracted]\n\n")
                
            f.write(f"{'-' * 40}\n")
            f.write(f"Language: both\n")
            f.write(f"Cosmic Position: {story_data.get('cosmic_position', 'unknown')}\n")
        saved_files.append(full_filename)
        print(f"✅ Full version saved to: {full_filename}")
    except Exception as e:
        print(f"❌ Error saving full version: {str(e)}")
    
    return saved_files

def split_bilingual_text(text):
    """Split bilingual text into Chinese and English parts"""
    # For empty input
    if not text or not text.strip():
        return {"zh": "", "en": ""}
    
    # Initialize result
    result = {
        "zh": "",
        "en": ""
    }
    
    # First check for standard markers
    chinese_section = None
    english_section = None
    
    # Check for common section markers
    if any(marker in text.lower() for marker in ["chinese version:", "中文版:", "chinese:", "中文:"]):
        parts = re.split(r"chinese version:|中文版:|chinese:|中文:|english translation:|english version:|英文版:|english:|英文:", 
                         text, flags=re.IGNORECASE)
        
        # Clean up the parts
        parts = [p.strip() for p in parts if p.strip()]
        
        if len(parts) >= 2:  # We have at least two sections
            # Determine which is which
            for i, part in enumerate(parts):
                # Count Chinese characters
                chinese_char_count = sum(1 for char in part if '\u4e00' <= char <= '\u9fff')
                is_mostly_chinese = chinese_char_count > len(part) * 0.2  # Lower threshold to catch mixed content
                
                if is_mostly_chinese and chinese_section is None:
                    chinese_section = part
                elif not is_mostly_chinese and english_section is None and chinese_section is not None:
                    english_section = part
    
    # If no markers found, use character detection
    if chinese_section is None or english_section is None:
        # Split the text into lines
        lines = text.split('\n')
        
        # Track separate sections
        chinese_lines = []
        english_lines = []
        
        # First pass: identify language of each line
        line_languages = []
        for line in lines:
            line = line.strip()
            if not line:
                line_languages.append("empty")
                continue
                
            # Count Chinese characters
            chinese_char_count = sum(1 for char in line if '\u4e00' <= char <= '\u9fff')
            is_chinese = chinese_char_count > len(line) * 0.15  # Lower threshold
            
            if is_chinese:
                line_languages.append("zh")
            else:
                line_languages.append("en")
        
        # Second pass: identify sections based on language transitions
        current_language = None
        transition_points = []
        
        for i, lang in enumerate(line_languages):
            if lang == "empty":
                continue
                
            if current_language is None:
                current_language = lang
            elif lang != current_language and lang != "empty":
                # Found a language transition
                transition_points.append(i)
                current_language = lang
        
        # If we found a transition, split the text
        if transition_points:
            # Find the main transition point (usually there's just one major transition)
            main_transition = transition_points[0]
            
            # Chinese content is typically first
            for i in range(main_transition):
                if line_languages[i] != "empty":
                    chinese_lines.append(lines[i])
            
            # English content is typically second
            for i in range(main_transition, len(lines)):
                if line_languages[i] != "empty":
                    english_lines.append(lines[i])
                    
            # Combine the lines
            if chinese_lines:
                chinese_section = "\n".join(chinese_lines)
            
            if english_lines:
                english_section = "\n".join(english_lines)
    
    # Assign to result
    if chinese_section:
        result["zh"] = chinese_section
    
    if english_section:
        result["en"] = english_section
    
    # Fallback if no sections detected
    if not result["zh"] and not result["en"]:
        # If the text contains Chinese characters, try to split by paragraphs
        chinese_char_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        if chinese_char_count > 0:
            # Try to find a natural split point between paragraphs
            paragraphs = re.split(r'\n\s*\n', text)
            
            if len(paragraphs) >= 2:
                chinese_paragraphs = []
                english_paragraphs = []
                
                # Identify language of each paragraph
                for para in paragraphs:
                    chinese_char_count = sum(1 for char in para if '\u4e00' <= char <= '\u9fff')
                    is_chinese = chinese_char_count > len(para) * 0.15
                    
                    if is_chinese:
                        chinese_paragraphs.append(para)
                    else:
                        english_paragraphs.append(para)
                
                if chinese_paragraphs:
                    result["zh"] = "\n\n".join(chinese_paragraphs)
                
                if english_paragraphs:
                    result["en"] = "\n\n".join(english_paragraphs)
            else:
                # If we can't split by paragraphs, just assign the whole text to Chinese
                result["zh"] = text
        else:
            # If no Chinese characters, treat as English
            result["en"] = text
    
    # Print debug info
    print(f"DEBUG: Split bilingual text - Chinese: {len(result['zh'])} chars, English: {len(result['en'])} chars")
    
    return result

def roll_die():
    """Roll the D18 story die"""
    try:
        response = requests.post(f"{SERVER_URL}/roll_die")
        
        if response.status_code != 200:
            print(f"❌ Error: Server returned status code {response.status_code}")
            print(response.text)
            return
        
        roll_data = response.json()
        
        print(f"🎲 DIE ROLLED: {roll_data.get('roll', '?')} → {roll_data.get('action_type', 'unknown')}")
    
    except Exception as e:
        print(f"❌ Error rolling die: {e}")

def display_main_menu():
    """Display the main menu options with auto-save toggle"""
    auto_save_status = "enabled" if AUTO_SAVE_TURNS else "disabled"
    
    print_header("FOLKTALE GENERATOR")
    print("What would you like to do?\n")
    print("  1. Start a new story")
    print("  2. Continue active story (next turn)")
    print("  3. Check story status")
    print("  4. List available story arcs")
    print("  5. Change story language")
    print("  6. Toggle auto-save (currently: {})".format(auto_save_status))
    print("  7. Save current turn directly")  
    print("  8. Manual copy-paste save")
    print("  9. Export all stories")
    print("  0. Exit\n")
    return input("Enter your choice (0-9): ").strip()

def display_command_help(command):
    """Display detailed help for a specific command"""
    command = command.lower()
    
    if command == "start":
        print_header("START COMMAND HELP")
        print("Usage: start")
        print("Starts a new folktale story with interactive prompts for:")
        print("  - Language (English, Chinese, or bilingual)")
        print("  - Story arc type")
        print("  - Optional continuation from a previous story")
        
    elif command == "next":
        print_header("NEXT COMMAND HELP")
        print("Usage: next")
        print("Generates the next turn of the active story.")
        print("Each turn advances the story with:")
        print("  - A die roll determining the action type")
        print("  - Selection of narrative elements")
        print("  - Progression through the cosmic cycle")
        print("  - Advancement through the story arc stages")
        
    elif command == "arcs":
        print_header("ARCS COMMAND HELP")
        print("Usage: arcs")
        print("Lists all available story arc types with their:")
        print("  - Descriptions")
        print("  - Narrative stages")
        print("  - Typical motifs")
        
    elif command == "status":
        print_header("STATUS COMMAND HELP")
        print("Usage: status")
        print("Displays the status of the active story, including:")
        print("  - Story ID")
        print("  - Current turn")
        print("  - Maximum turns")
        print("  - Cosmic position")
        print("  - Latest narrative")
        
    elif command == "language":
        print_header("LANGUAGE COMMAND HELP")
        print("Usage: language")
        print("Change the language of the active story.")
        print("Options:")
        print("  - en: English-only")
        print("  - zh: Chinese-only")
        print("  - both: Bilingual (Chinese and English)")
        
    elif command == "save":
        print_header("SAVE COMMAND HELP")
        print("Usage: save")
        print("Saves the current story to a text file.")
        print("You'll be prompted for an optional filename.")
        print("The file will include:")
        print("  - All narrative turns")
        print("  - Story metadata")
        print("  - Cosmic elements and other story components")
        
    elif command == "roll":
        print_header("ROLL COMMAND HELP")
        print("Usage: roll")
        print("Rolls the 18-sided story die without advancing the story.")
        print("This is useful for testing and understanding how:")
        print("  - Die rolls determine action types")
        print("  - Different action types affect the narrative")
        
    elif command == "help":
        print_header("HELP COMMAND HELP")
        print("Usage: help [command]")
        print("Displays help information:")
        print("  - Without arguments: Shows the main help menu")
        print("  - With a command name: Shows detailed help for that command")
        
    elif command in ["exit", "quit"]:
        print_header("EXIT COMMAND HELP")
        print("Usage: exit or quit")
        print("Exits the folktale generator client.")
        
    else:
        print(f"❌ Unknown command: {command}")
        display_help_menu()

def guided_start_story():
    """Guide the user through starting a new story with interactive prompts"""
    print_header("START A NEW STORY")
    
    # 1. Choose language
    print("Choose a language for your story:")
    print("  1. English only (en)")
    print("  2. Chinese only (zh)")
    print("  3. Bilingual (both)")
    
    while True:
        lang_choice = input("Enter choice (1-3) [1]: ").strip()
        if not lang_choice:
            language = "en"
            break
        try:
            choice_num = int(lang_choice)
            if choice_num == 1:
                language = "en"
                break
            elif choice_num == 2:
                language = "zh"
                break
            elif choice_num == 3:
                language = "both"
                break
            else:
                print("❌ Please enter a number between 1 and 3.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    print(f"Selected language: {language}")
    
    # 2. Choose arc type
    arc_types = get_story_arcs()
    if arc_types:
        print("\nChoose a story arc type:")
        print("  0. Random (let the system choose)")
        
        # Display available arc types
        arc_list = list(arc_types.keys())
        for i, arc_id in enumerate(arc_list, 1):
            print(f"  {i}. {arc_id} - {arc_types[arc_id].get('description', '')[:60]}...")
        
        while True:
            arc_choice = input("Enter choice (0-{}) [0]: ".format(len(arc_list)))
            if not arc_choice:
                arc_type = None  # Random
                break
            try:
                choice_num = int(arc_choice)
                if choice_num == 0:
                    arc_type = None  # Random
                    break
                elif 1 <= choice_num <= len(arc_list):
                    arc_type = arc_list[choice_num - 1]
                    break
                else:
                    print(f"❌ Please enter a number between 0 and {len(arc_list)}.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        if arc_type:
            print(f"Selected arc type: {arc_type}")
        else:
            print("Selected arc type: Random")
    else:
        print("\nUnable to retrieve arc types. Using random arc type.")
        arc_type = None
    
    # 3. Choose continuation option
    print("\nDo you want to continue from a previous story?")
    print("  1. No, start fresh (default)")
    print("  2. Yes, continue from the most recent story")
    print("  3. Yes, provide a specific story ID")
    
    previous_id = None
    while True:
        cont_choice = input("Enter choice (1-3) [1]: ").strip()
        if not cont_choice:
            break  # Default: no continuation
        try:
            choice_num = int(cont_choice)
            if choice_num == 1:
                break
            elif choice_num == 2:
                # Get list of stories to find most recent
                try:
                    response = requests.get(f"{SERVER_URL}/list_stories")
                    if response.status_code == 200:
                        stories = response.json().get("stories", [])
                        if stories:
                            previous_id = stories[0].get("id")
                            print(f"Using most recent story: {previous_id}")
                        else:
                            print("No previous stories found. Starting fresh.")
                    else:
                        print("Could not retrieve story list. Starting fresh.")
                except Exception as e:
                    print(f"Error retrieving stories: {e}. Starting fresh.")
                break
            elif choice_num == 3:
                previous_id = input("Enter the story ID: ").strip()
                break
            else:
                print("❌ Please enter a number between 1 and 3.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    # 4. Confirm and start
    print("\nReady to start a new story with these settings:")
    print(f"  Language: {language}")
    print(f"  Arc Type: {arc_type or 'Random'}")
    print(f"  Continue from: {previous_id or 'None (fresh start)'}")
    
    confirm = input("\nStart the story? (Y/n): ").strip().lower()
    if confirm in ["", "y", "yes"]:
        return start_story(language, arc_type, previous_id)
    else:
        print("Story creation cancelled.")
        return None

    # After the story is started, verify that we have content
    if story_data:
        has_content = False
        if "opening_narrative" in story_data and story_data["opening_narrative"]:
            has_content = True
        elif "opening_narrative_zh" in story_data and story_data["opening_narrative_zh"]:
            has_content = True
        elif "opening_narrative_en" in story_data and story_data["opening_narrative_en"]:
            has_content = True
        
        if not has_content:
            print("\n⚠️ WARNING: Started story but received no narrative content!")
            print("Running API diagnostics...")
            examine_api_response("active_story")

def extract_narrative_content(story_data, language):
    """Extract narrative content from story data based on language - enhanced version"""
    content = ""
    
    # Debug what we're looking for
    print(f"DEBUG: Extracting {language} content from story data")
    
    # CRITICAL: Check narrative_thread first since that's the most reliable source
    if "narrative_thread" in story_data and story_data["narrative_thread"]:
        thread = story_data["narrative_thread"]
        print(f"DEBUG: Found narrative_thread with {len(thread)} entries")
        
        assembled_content = []
        for i, turn in enumerate(thread):
            turn_content = ""
            
            # For Chinese content
            if language == "zh":
                # First try narrative_zh
                if "narrative_zh" in turn and turn["narrative_zh"]:
                    turn_content = turn["narrative_zh"]
                    print(f"DEBUG: Found narrative_zh in turn {i}: {len(turn_content)} chars")
                # Then try checking if narrative contains Chinese
                elif "narrative" in turn:
                    chinese_chars = sum(1 for char in turn["narrative"] if '\u4e00' <= char <= '\u9fff')
                    if chinese_chars > 0:
                        # Try to extract only the Chinese part
                        parts = split_bilingual_text(turn["narrative"])
                        if parts["zh"]:
                            turn_content = parts["zh"]
                            print(f"DEBUG: Extracted Chinese from narrative in turn {i}: {len(turn_content)} chars")
            # For English content
            else:
                if "narrative" in turn and turn["narrative"]:
                    # For English, prioritize checking if the content doesn't have Chinese
                    chinese_chars = sum(1 for char in turn["narrative"] if '\u4e00' <= char <= '\u9fff')
                    if chinese_chars == 0 or language != "en":
                        turn_content = turn["narrative"]
                        print(f"DEBUG: Found narrative in turn {i}: {len(turn_content)} chars")
                    else:
                        # If it has Chinese characters, try to extract only the English part
                        parts = split_bilingual_text(turn["narrative"])
                        if parts["en"]:
                            turn_content = parts["en"]
                            print(f"DEBUG: Extracted English from mixed narrative in turn {i}: {len(turn_content)} chars")
                elif "narrative_en" in turn and turn["narrative_en"]:
                    turn_content = turn["narrative_en"]
                    print(f"DEBUG: Found narrative_en in turn {i}: {len(turn_content)} chars")
            
            if turn_content:
                assembled_content.append(f"--- Turn {i} ---\n\n{turn_content}")
        
        if assembled_content:
            content = "\n\n".join(assembled_content)
            print(f"DEBUG: Successfully assembled content from narrative_thread ({len(content)} chars)")
            # Return immediately if we found content in the thread
            return content
    
    # If we couldn't extract from narrative_thread, try direct fields
    if language == "zh":
        # First priority: narrative_zh field
        if "narrative_zh" in story_data and story_data["narrative_zh"]:
            content = story_data["narrative_zh"]
            print(f"DEBUG: Found narrative_zh in direct field ({len(content)} chars)")
        # Second priority: Chinese characters in narrative field
        elif "narrative" in story_data and story_data["narrative"]:
            chinese_chars = sum(1 for char in story_data["narrative"] if '\u4e00' <= char <= '\u9fff')
            if chinese_chars > 0:
                # Try to extract only the Chinese part
                parts = split_bilingual_text(story_data["narrative"])
                if parts["zh"]:
                    content = parts["zh"]
                    print(f"DEBUG: Extracted Chinese from narrative direct field ({len(content)} chars)")
        # Third priority: opening_narrative_zh field
        elif "opening_narrative_zh" in story_data and story_data["opening_narrative_zh"]:
            content = story_data["opening_narrative_zh"]
            print(f"DEBUG: Found opening_narrative_zh ({len(content)} chars)")
    else:  # English or other languages
        # First priority: narrative field
        if "narrative" in story_data and story_data["narrative"]:
            content = story_data["narrative"]
            print(f"DEBUG: Found narrative direct field ({len(content)} chars)")
        # Second priority: opening_narrative field
        elif "opening_narrative" in story_data and story_data["opening_narrative"]:
            content = story_data["opening_narrative"]
            print(f"DEBUG: Found opening_narrative ({len(content)} chars)")
        # Third priority: narrative_en field (sometimes used in bilingual)
        elif "narrative_en" in story_data and story_data["narrative_en"]:
            content = story_data["narrative_en"]
            print(f"DEBUG: Found narrative_en ({len(content)} chars)")
    
    # Last resort: Try to find in narrative_so_far
    if not content and "narrative_so_far" in story_data and story_data["narrative_so_far"]:
        print(f"DEBUG: Searching for {language} content in narrative_so_far")
        narratives = story_data["narrative_so_far"]
        
        # Check each narrative
        for i, narrative in enumerate(narratives):
            if language == "zh":
                chinese_chars = sum(1 for char in narrative if '\u4e00' <= char <= '\u9fff')
                if chinese_chars > 0:
                    # Try to extract only the Chinese part if it has both languages
                    if chinese_chars < len(narrative) / 2:  # If it's mixed content
                        parts = split_bilingual_text(narrative)
                        if parts["zh"]:
                            content = parts["zh"]
                            print(f"DEBUG: Extracted Chinese from narrative_so_far[{i}] ({len(content)} chars)")
                            break
                    else:
                        content = narrative
                        print(f"DEBUG: Found Chinese in narrative_so_far[{i}] ({len(content)} chars)")
                        break
            else:
                # For English, prioritize content without Chinese
                chinese_chars = sum(1 for char in narrative if '\u4e00' <= char <= '\u9fff')
                if chinese_chars == 0:
                    content = narrative
                    print(f"DEBUG: Found English in narrative_so_far[{i}] ({len(content)} chars)")
                    break
    
    # Extra debug info about what we found
    print(f"DEBUG: Final {language} content extraction result: {len(content)} chars found")
    
    return content

def guided_change_language():
    """Guide the user through changing the language"""
    print_header("CHANGE STORY LANGUAGE")
    
    print("Choose a new language for your story:")
    print("  1. English only (en)")
    print("  2. Chinese only (zh)")
    print("  3. Bilingual (both)")
    
    while True:
        lang_choice = input("Enter choice (1-3): ").strip()
        try:
            choice_num = int(lang_choice)
            if choice_num == 1:
                return change_language("en")
            elif choice_num == 2:
                return change_language("zh")
            elif choice_num == 3:
                return change_language("both")
            else:
                print("❌ Please enter a number between 1 and 3.")
        except ValueError:
            print("❌ Please enter a valid number.")

def guided_save_story():
    """Guide the user through saving the story with improved bilingual support"""
    story_data = check_active_story()
    if not story_data:
        return None
    
    print_header("SAVE STORY")
    
    # Check if this is a bilingual story
    is_bilingual = story_data.get('language') == "both"
    
    # Generate default filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    story_id = story_data.get('story_id', "unknown")
    default_filename = f"tale_{story_id}_{timestamp}"
    
    filename = input(f"Enter filename (without extension) [default: {default_filename}]: ").strip()
    if not filename:
        filename = default_filename
    
    # For bilingual stories, use the specialized saving function
    if is_bilingual:
        print("Bilingual story detected. Using specialized saving function.")
        
        # Ensure we have the complete story data
        try:
            # First try to get the full story data from the server
            response = requests.get(f"{SERVER_URL}/active_story")
            if response.status_code == 200:
                complete_story_data = response.json()
                print("Retrieved complete story data from server.")
                return save_bilingual_story(complete_story_data, filename)
            else:
                # If that fails, use the story_data we already have
                print("Using cached story data for saving.")
                return save_bilingual_story(story_data, filename)
        except Exception as e:
            print(f"❌ Error retrieving complete story data: {e}")
            print("Using cached story data for saving.")
            return save_bilingual_story(story_data, filename)
    else:
        # For non-bilingual stories, use the regular save function
        return save_story_to_file(story_data, filename)

# Modified display_main_menu function to clarify arc selection
def display_main_menu():
    """Display the main menu options with automatic modes"""
    print_header("FOLKTALE GENERATOR")
    print("What would you like to do?\n")
    print("  1. Start a new story")
    print("  2. Continue active story (next turn)")
    print("  3. Check story status")
    print("  4. List available story arcs")
    print("  5. Change story language")
    print("  6. Save story to file (standard)")
    print("  7. EMERGENCY: Generate and save directly")
    print("  8. EMERGENCY: Save last turn")
    print("  9. EMERGENCY: Manual copy-paste save")
    print("  10. 🤖 FULLY AUTOMATIC MODE (single story, select arc)")
    print("  11. 🚀 BATCH AUTOMATIC MODE (multiple stories, same arc)")  # Updated description
    print("  0. Exit\n")
    return input("Enter your choice (0-11): ").strip()



# Modified interactive_mode function to handle the new option
def interactive_mode():
    """Run an interactive storytelling session with auto-save option"""
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
    
    print("\n📚 FOLKTALE GENERATOR INTERACTIVE SESSION 📚")
    print("Version 1.0.0 - Han Dynasty Storytelling")
    
    while True:
        choice = display_main_menu()
        
        # Process the menu choice
        if choice == "1":
            guided_start_story()
        elif choice == "2":
            next_turn()
        elif choice == "3":
            check_active_story()
        elif choice == "4":
            list_story_arcs()
        elif choice == "5":
            guided_change_language()
        elif choice == "6":
            guided_save_story()
        elif choice == "7":
            # Get current story data and save directly
            try:
                response = requests.get(f"{SERVER_URL}/active_story")
                if response.status_code == 200:
                    story_data = response.json()
                    # Also try to get the last turn from API
                    last_turn_response = requests.post(f"{SERVER_URL}/next_turn")
                    if last_turn_response.status_code == 200:
                        last_turn_data = last_turn_response.json()
                        save_generated_narrative(last_turn_data, last_turn_data.get("language", "en"))
                    else:
                        # Fall back to active story data
                        save_generated_narrative(story_data, story_data.get("language", "en"))
                else:
                    print("❌ No active story found or error connecting to server")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        elif choice == "8":
            emergency_save_last_turn()
        elif choice == "9":
            manual_copy_paste_save()
        elif choice == "10":  # Single fully automatic mode
            fully_automatic_mode()
        elif choice == "11":  # Batch automatic mode
            batch_automatic_mode()
        elif choice == "0":
            print("\nGoodbye! 👋")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 0 and 11.")
        
        # Pause before returning to the main menu
        input("\nPress Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen

def auto_save_every_turn(enable=True):
    """Enable or disable auto-saving of each turn as it's generated"""
    global AUTO_SAVE_TURNS
    AUTO_SAVE_TURNS = enable
    status = "enabled" if enable else "disabled"
    print(f"🔄 Auto-save for each turn is now {status}")
    
    # Save setting to a configuration file
    try:
        with open('./config.json', 'w') as f:
            json.dump({"auto_save_turns": enable}, f)
        print("✅ Setting saved")
    except Exception as e:
        print(f"❌ Error saving setting: {str(e)}")
    
    return enable

def command_line_mode():
    """Process input as commands in a simpler interactive mode"""
    print("\n📚 FOLKTALE GENERATOR COMMAND MODE 📚\n")
    print("Type 'help' for a list of commands, 'menu' for guided menu, or 'auto' for quick story generation\n")
    
    while True:
        command = input("\nCommand > ").strip().lower()
        parts = command.split()
        base_cmd = parts[0] if parts else ""
        
        if base_cmd in ["exit", "quit"]:
            print("Goodbye! 👋")
            break
        
        elif base_cmd == "menu":
            interactive_mode()
        
        elif base_cmd == "auto":
            auto_mode()
            
        elif base_cmd == "help":
            if len(parts) > 1:
                display_command_help(parts[1])
            else:
                display_help_menu()
        
        elif base_cmd == "start":
            guided_start_story()
        
        elif base_cmd == "next":
            next_turn()
        
        elif base_cmd == "arcs":
            list_story_arcs()
        
        elif base_cmd == "status":
            check_active_story()
        
        elif base_cmd == "language":
            if len(parts) > 1 and parts[1] in ["en", "zh", "both"]:
                change_language(parts[1])
            else:
                guided_change_language()
        
        elif base_cmd == "save":
            guided_save_story()
        
        elif base_cmd == "roll":
            roll_die()
        
        elif base_cmd == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
            
        elif not base_cmd:
            continue  # Empty input, just continue
            
        else:
            print(f"❌ Unknown command: {base_cmd}")
            print("Type 'help' for a list of commands or 'menu' for guided menu")

def auto_mode():
    """Run the folktale generator in automatic mode with minimal user input"""
    print_header("AUTO MODE - FOLKTALE GENERATOR")
    
    # Get language preference only
    print("Choose a language for your story:")
    print("  1. English only (en)")
    print("  2. Chinese only (zh)")
    print("  3. Bilingual (both)")
    
    language = "en"  # Default
    while True:
        lang_choice = input("Enter choice (1-3) [1]: ").strip()
        if not lang_choice:
            language = "en"
            break
        try:
            choice_num = int(lang_choice)
            if choice_num == 1:
                language = "en"
                break
            elif choice_num == 2:
                language = "zh"
                break
            elif choice_num == 3:
                language = "both"
                break
            else:
                print("❌ Please enter a number between 1 and 3.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    print(f"\nSelected language: {language}")
    print("All other settings will be randomized...")
    
    # Start a story with random settings
    story_data = start_story(language=language)
    if not story_data:
        print("❌ Failed to start story")
        return
    
    # Store whether this is a bilingual story
    is_bilingual = (language == "both")
    
    # Ask whether to continue generating turns automatically
    auto_continue = input("\nContinue generating turns automatically? (Y/n): ").strip().lower()
    if auto_continue in ["", "y", "yes"]:
        num_turns = 0
        max_turns = 10  # Default maximum
        
        try:
            max_turns_input = input(f"Maximum number of turns to generate [10]: ").strip()
            if max_turns_input:
                max_turns = int(max_turns_input)
        except ValueError:
            print(f"❌ Invalid number, using default: {max_turns}")
        
        print(f"\nGenerating up to {max_turns} turns automatically...")
        
        try:
            while num_turns < max_turns:
                input("\nPress Enter for next turn (or Ctrl+C to stop)...")
                turn_data = next_turn()
                if not turn_data:
                    print("❌ Failed to generate turn")
                    break
                
                # Check if we have reached the end
                if turn_data.get('remaining_turns', 1) <= 0:
                    print("🏁 Story has reached its conclusion!")
                    break
                
                num_turns += 1
            
            print(f"\nCompleted {num_turns} turns. Story generation complete.")
            
            # Ask if user wants to save the story
            save_prompt = input("\nSave this story to file? (Y/n): ").strip().lower()
            if save_prompt in ["", "y", "yes"]:
                if is_bilingual:
                    # For bilingual stories, offer the manual saving option
                    bilingual_save_prompt = input("Would you like to use manual bilingual saving for better results? (Y/n): ").strip().lower()
                    if bilingual_save_prompt in ["", "y", "yes"]:
                        save_bilingual_story()
                    else:
                        guided_save_story()
                else:
                    guided_save_story()
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Auto generation stopped by user")
    
    print("\nReturning to main menu...")

# Add this helper function to select story arc type
def select_story_arc_type():
    """Let user select a story arc type from available options"""
    print("📖 Selecting Story Arc Type...")
    
    # Get available arc types
    arc_types = get_story_arcs()
    if not arc_types:
        print("❌ Could not retrieve story arc types. Using 'quest' as fallback.")
        return "quest"
    
    print("\nAvailable story arc types:")
    print("  0. Random (let the system choose)")
    
    # Display available arc types
    arc_list = list(arc_types.keys())
    for i, arc_id in enumerate(arc_list, 1):
        description = arc_types[arc_id].get('description', '')
        print(f"  {i}. {arc_id} - {description[:60]}{'...' if len(description) > 60 else ''}")
    
    while True:
        choice = input(f"\nEnter choice (0-{len(arc_list)}) [0]: ").strip()
        if not choice:
            return None  # Random
        try:
            choice_num = int(choice)
            if choice_num == 0:
                return None  # Random
            elif 1 <= choice_num <= len(arc_list):
                selected_arc = arc_list[choice_num - 1]
                print(f"✅ Selected arc type: {selected_arc}")
                return selected_arc
            else:
                print(f"❌ Please enter a number between 0 and {len(arc_list)}.")
        except ValueError:
            print("❌ Please enter a valid number.")

# Add this new function for batch automatic story generation
def batch_automatic_mode():
    """Run multiple automatic story generations"""
    print_header("BATCH AUTOMATIC MODE - HAN DYNASTY FOLKTALES")
    
    # First, get the story arc type selection
    selected_arc_type = select_story_arc_type()
    arc_display = selected_arc_type if selected_arc_type else "Random"
    
    # Get number of stories to generate
    while True:
        try:
            num_stories = input("How many stories would you like to generate? (1-20): ").strip()
            num_stories = int(num_stories)
            if 1 <= num_stories <= 20:
                break
            else:
                print("❌ Please enter a number between 1 and 20.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    print(f"\n🤖 Starting batch generation of {num_stories} stories...")
    print("   Language: Chinese (zh)")
    print(f"   Arc Type: {arc_display}")
    print("   Mode: Fully automatic until completion")
    print()
    
    batch_start_time = datetime.now()
    successful_stories = []
    failed_stories = []
    
    for story_num in range(1, num_stories + 1):
        print(f"\n{'='*60}")
        print(f"📚 GENERATING STORY {story_num} OF {num_stories}")
        print(f"{'='*60}")
        
        try:
            # Generate one complete story with the selected arc type
            story_info = fully_automatic_mode(selected_arc_type=selected_arc_type)
            
            if story_info and story_info.get("turns_completed", 0) > 0:
                successful_stories.append({
                    "number": story_num,
                    "arc_type": story_info.get("arc_type", selected_arc_type or "unknown"),
                    "turns": story_info.get("turns_completed", 0),
                    "cosmic_positions": story_info.get("cosmic_positions", []),
                    "duration": (datetime.now() - story_info["start_time"]).total_seconds()
                })
                print(f"✅ Story {story_num} completed successfully!")
            else:
                failed_stories.append(story_num)
                print(f"❌ Story {story_num} failed to complete properly.")
            
        except Exception as e:
            failed_stories.append(story_num)
            print(f"❌ Story {story_num} failed with error: {str(e)}")
        
        # Brief pause between stories
        if story_num < num_stories:
            print(f"\n⏸️ Brief pause before next story...")
            time.sleep(2)
    
    # Generate batch summary
    batch_end_time = datetime.now()
    total_duration = batch_end_time - batch_start_time
    
    print(f"\n{'='*80}")
    print("🎉 BATCH GENERATION COMPLETED!")
    print(f"{'='*80}")
    
    print(f"\n📊 BATCH SUMMARY:")
    print(f"   Total Stories Requested: {num_stories}")
    print(f"   Successfully Completed: {len(successful_stories)}")
    print(f"   Failed: {len(failed_stories)}")
    print(f"   Arc Type Used: {arc_display}")
    print(f"   Total Duration: {total_duration.total_seconds():.1f} seconds")
    print(f"   Average Time per Story: {total_duration.total_seconds()/max(len(successful_stories), 1):.1f} seconds")
    
    if successful_stories:
        print(f"\n📖 STORY DETAILS:")
        total_turns = 0
        
        for story in successful_stories:
            print(f"   Story {story['number']}: {story['arc_type']} ({story['turns']} turns, {story['duration']:.1f}s)")
            total_turns += story['turns']
        
        print(f"\n📈 STATISTICS:")
        print(f"   Total Turns Generated: {total_turns}")
        print(f"   Average Turns per Story: {total_turns/len(successful_stories):.1f}")
    
    if failed_stories:
        print(f"\n❌ FAILED STORIES: {', '.join(map(str, failed_stories))}")
    
    print(f"\n✅ All generated stories have been saved to the archived_tales directory.")
    
    return {
        "requested": num_stories,
        "successful": len(successful_stories),
        "failed": len(failed_stories),
        "stories": successful_stories,
        "duration": total_duration.total_seconds(),
        "arc_type": selected_arc_type
    }

# Add this new function for fully automatic story generation
def fully_automatic_mode(selected_arc_type=None):
    """Run a completely automatic story generation with no user input"""
    print_header("FULLY AUTOMATIC MODE - HAN DYNASTY FOLKTALE")
    
    # If no arc type provided, prompt user to select one
    if selected_arc_type is None:
        selected_arc_type = select_story_arc_type()
    
    arc_display = selected_arc_type if selected_arc_type else "Random"
    
    print("🤖 Starting fully automatic story generation...")
    print("   Language: Chinese (zh)")
    print(f"   Arc Type: {arc_display}")
    print("   Mode: Continuous until completion")
    print()
    
    # Start a story with Chinese language and the selected arc type
    print("📚 Starting new story automatically...")
    story_data = start_story(language="zh", arc_type=selected_arc_type)
    if not story_data:
        print("❌ Failed to start story automatically")
        return
    
    story_id = story_data.get("story_id", "unknown")
    print(f"✅ Story started with ID: {story_id}")
    
    # Track story information for summary - use the selected arc type directly
    story_info = {
        "arc_type": selected_arc_type or "random",
        "turns_completed": 0,
        "cosmic_positions": [],
        "start_time": datetime.now()
    }
    
    print(f"📖 Story Arc Type: {story_info['arc_type']}")
    print()
    
    # Continue generating turns until story is complete
    turn_count = 0
    max_attempts = 20  # Safety limit
    
    try:
        while turn_count < max_attempts:
            print(f"🎲 Generating turn {turn_count + 1}...")
            
            turn_data = next_turn()
            if not turn_data:
                print("❌ Failed to generate turn")
                break
            
            turn_count += 1
            story_info["turns_completed"] = turn_count
            
            # Track cosmic position if available
            cosmic_pos = turn_data.get('cosmic_position', 'unknown')
            if cosmic_pos not in story_info["cosmic_positions"]:
                story_info["cosmic_positions"].append(cosmic_pos)
            
            remaining_turns = turn_data.get('remaining_turns', 1)
            print(f"✅ Turn {turn_count} completed. Remaining turns: {remaining_turns}")
            
            # Check if story is complete
            if remaining_turns <= 0:
                print("🏁 Story has reached its natural conclusion!")
                break
            
            # Small delay to be respectful to the API
            time.sleep(1)
        
        if turn_count >= max_attempts:
            print(f"⚠️ Reached maximum turn limit ({max_attempts}). Stopping.")
        
    except KeyboardInterrupt:
        print("\n⚠️ Automatic generation interrupted by user")
    except Exception as e:
        print(f"❌ Error during automatic generation: {str(e)}")
    
    # Generate and display summary
    end_time = datetime.now()
    duration = end_time - story_info["start_time"]
    
    summary = f"""
=== STORY COMPLETED ===
Story Arc Type: {story_info['arc_type']}
Number of Turns: {story_info['turns_completed']}
Cosmic Positions: {' → '.join(story_info['cosmic_positions'])}
Duration: {duration.total_seconds():.1f} seconds
Generated: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
========================
"""
    
    print(summary)
    
    # Prepend summary to the story file and rename with new format
    archive_dir = "./archived_tales"
    old_continuous_file = os.path.join(archive_dir, f"continuous_zh_{story_id}.txt")
    
    # Create new filename format: YYYYMMDD_HHMMSS_arctype_X-turns_zh
    arc_type_clean = story_info['arc_type'].replace('_', '-')  # Replace underscores with hyphens for readability
    new_filename = f"{story_id}_{arc_type_clean}_{story_info['turns_completed']}-turns_zh.txt"
    new_continuous_file = os.path.join(archive_dir, new_filename)
    
    if os.path.exists(old_continuous_file):
        try:
            # Read existing content
            with open(old_continuous_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Write summary + existing content to new filename
            with open(new_continuous_file, 'w', encoding='utf-8') as f:
                f.write(summary + "\n\n")
                f.write(existing_content)
            
            # Remove the old file
            os.remove(old_continuous_file)
            
            print(f"✅ Story summary prepended and file renamed to: {new_filename}")
        except Exception as e:
            print(f"❌ Error processing story file: {str(e)}")
    
    print("\n🎉 Fully automatic story generation completed!")
    return story_info

def direct_save_current_turn_raw():
    """Save the current turn directly from raw API response data with minimal processing"""
    print_header("EMERGENCY DIRECT SAVE")
    
    try:
        # Make a direct request to next_turn to get the raw response
        response = requests.post(f"{SERVER_URL}/next_turn")
        
        # Check for error
        if response.status_code != 200:
            print(f"❌ Error: Server returned status code {response.status_code}")
            return None
        
        # Get the raw JSON response
        raw_data = response.json()
        
        # Print all keys for debugging
        print("Available keys in raw response:")
        for key in raw_data.keys():
            print(f"  - {key}")
        
        # Check specifically for narrative content
        has_narrative = "narrative" in raw_data and raw_data["narrative"]
        has_narrative_zh = "narrative_zh" in raw_data and raw_data["narrative_zh"]
        
        print(f"Has narrative: {has_narrative}")
        print(f"Has narrative_zh: {has_narrative_zh}")
        
        if has_narrative:
            print(f"Narrative length: {len(raw_data['narrative'])} chars")
        if has_narrative_zh:
            print(f"Narrative_zh length: {len(raw_data['narrative_zh'])} chars")
        
        # Generate a filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"emergency_save_{timestamp}"
        filename = input(f"Enter filename (without extension) [default: {default_filename}]: ").strip()
        if not filename:
            filename = default_filename
        
        # Create archived_tales directory if it doesn't exist
        archive_dir = "./archived_tales"
        os.makedirs(archive_dir, exist_ok=True)
        
        saved_files = []
        
        # Save the raw JSON data for reference
        json_filename = os.path.join(archive_dir, f"raw_{filename}.json")
        try:
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, ensure_ascii=False, indent=2)
            saved_files.append(json_filename)
            print(f"✅ Raw JSON data saved to: {json_filename}")
        except Exception as e:
            print(f"❌ Error saving raw data: {str(e)}")
        
        # Attempt to save Chinese content if available
        if has_narrative_zh:
            zh_filename = os.path.join(archive_dir, f"zh_{filename}.txt")
            try:
                chinese_content = raw_data["narrative_zh"]
                with open(zh_filename, 'w', encoding='utf-8') as f:
                    f.write(chinese_content)
                saved_files.append(zh_filename)
                print(f"✅ Chinese content saved to: {zh_filename}")
            except Exception as e:
                print(f"❌ Error saving Chinese content: {str(e)}")
        else:
            print("⚠️ No Chinese content found in API response")
        
        # Attempt to save English content if available
        if has_narrative:
            en_filename = os.path.join(archive_dir, f"en_{filename}.txt")
            try:
                english_content = raw_data["narrative"]
                with open(en_filename, 'w', encoding='utf-8') as f:
                    f.write(english_content)
                saved_files.append(en_filename)
                print(f"✅ English content saved to: {en_filename}")
            except Exception as e:
                print(f"❌ Error saving English content: {str(e)}")
        else:
            print("⚠️ No English content found in API response")
        
        # Display the narratives we just received
        if has_narrative_zh:
            print("\n🇨🇳 CHINESE NARRATIVE THAT WAS JUST SAVED:")
            print(raw_data["narrative_zh"])
        
        if has_narrative:
            print("\n🇬🇧 ENGLISH NARRATIVE THAT WAS JUST SAVED:")
            print(raw_data["narrative"])
        
        return saved_files
    
    except Exception as e:
        print(f"❌ Error in emergency direct save: {str(e)}")
        return None

def emergency_save_last_turn():
    """Try to save the last turn by directly querying the active story"""
    print_header("EMERGENCY SAVE LAST TURN")
    
    try:
        # Get the active story
        response = requests.get(f"{SERVER_URL}/active_story")
        
        # Check for error
        if response.status_code != 200:
            print(f"❌ Error: Server returned status code {response.status_code}")
            return None
        
        # Parse the response
        story_data = response.json()
        
        # Check for narrative_thread
        if "narrative_thread" not in story_data or not story_data["narrative_thread"]:
            print("❌ No narrative_thread found in active story")
            return None
        
        # Get the last turn
        thread = story_data["narrative_thread"]
        if not thread:
            print("❌ narrative_thread is empty")
            return None
        
        last_turn = thread[-1]
        print("Last turn keys:")
        for key in last_turn.keys():
            print(f"  - {key}")
        
        # Check for narrative content
        has_narrative = "narrative" in last_turn and last_turn["narrative"]
        has_narrative_zh = "narrative_zh" in last_turn and last_turn["narrative_zh"]
        
        print(f"Has narrative: {has_narrative}")
        print(f"Has narrative_zh: {has_narrative_zh}")
        
        # Generate a filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        story_id = story_data.get("story_id", "unknown")
        default_filename = f"last_turn_{story_id}_{timestamp}"
        filename = input(f"Enter filename (without extension) [default: {default_filename}]: ").strip()
        if not filename:
            filename = default_filename
        
        # Create archived_tales directory if it doesn't exist
        archive_dir = "./archived_tales"
        os.makedirs(archive_dir, exist_ok=True)
        
        saved_files = []
        
        # Save Chinese content if available
        if has_narrative_zh:
            zh_filename = os.path.join(archive_dir, f"zh_{filename}.txt")
            try:
                with open(zh_filename, 'w', encoding='utf-8') as f:
                    f.write(last_turn["narrative_zh"])
                saved_files.append(zh_filename)
                print(f"✅ Chinese content saved to: {zh_filename}")
            except Exception as e:
                print(f"❌ Error saving Chinese content: {str(e)}")
        else:
            print("⚠️ No Chinese content found in last turn")
        
        # Save English content if available
        if has_narrative:
            en_filename = os.path.join(archive_dir, f"en_{filename}.txt")
            try:
                with open(en_filename, 'w', encoding='utf-8') as f:
                    f.write(last_turn["narrative"])
                saved_files.append(en_filename)
                print(f"✅ English content saved to: {en_filename}")
            except Exception as e:
                print(f"❌ Error saving English content: {str(e)}")
        else:
            print("⚠️ No English content found in last turn")
        
        return saved_files
    
    except Exception as e:
        print(f"❌ Error in emergency save: {str(e)}")
        return None

def manual_copy_paste_save():
    """Save content via manual copy-paste from the console"""
    print_header("MANUAL COPY-PASTE SAVE")
    
    print("This function allows you to save content you can see on your screen.")
    print("You'll need to copy and paste the text directly from the console display.")
    
    # Ask for the language
    print("\nWhat language do you want to save?")
    print("1. Chinese")
    print("2. English")
    print("3. Both")
    
    lang_choice = input("Enter choice (1-3): ").strip()
    
    save_chinese = lang_choice in ["1", "3"]
    save_english = lang_choice in ["2", "3"]
    
    # Generate a filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"manual_save_{timestamp}"
    filename = input(f"Enter filename (without extension) [default: {default_filename}]: ").strip()
    if not filename:
        filename = default_filename
    
    # Create archived_tales directory if it doesn't exist
    archive_dir = "./archived_tales"
    os.makedirs(archive_dir, exist_ok=True)
    
    saved_files = []
    
    # Save Chinese content if requested
    if save_chinese:
        print("\nPlease copy and paste the Chinese content from the console:")
        print("(Look for text under '🇨🇳 CHINESE NARRATIVE:' headings)")
        chinese_content = input("Paste Chinese content here (then press Enter):\n")
        
        if chinese_content.strip():
            zh_filename = os.path.join(archive_dir, f"zh_{filename}.txt")
            try:
                with open(zh_filename, 'w', encoding='utf-8') as f:
                    f.write(chinese_content)
                saved_files.append(zh_filename)
                print(f"✅ Chinese content saved to: {zh_filename}")
            except Exception as e:
                print(f"❌ Error saving Chinese content: {str(e)}")
        else:
            print("⚠️ No Chinese content provided")
    
    # Save English content if requested
    if save_english:
        print("\nPlease copy and paste the English content from the console:")
        print("(Look for text under '🇬🇧 ENGLISH NARRATIVE:' or '📖 NARRATIVE:' headings)")
        english_content = input("Paste English content here (then press Enter):\n")
        
        if english_content.strip():
            en_filename = os.path.join(archive_dir, f"en_{filename}.txt")
            try:
                with open(en_filename, 'w', encoding='utf-8') as f:
                    f.write(english_content)
                saved_files.append(en_filename)
                print(f"✅ English content saved to: {en_filename}")
            except Exception as e:
                print(f"❌ Error saving English content: {str(e)}")
        else:
            print("⚠️ No English content provided")
    
    # Save combined version if both were requested
    if save_chinese and save_english and chinese_content.strip() and english_content.strip():
        full_filename = os.path.join(archive_dir, f"full_{filename}.txt")
        try:
            with open(full_filename, 'w', encoding='utf-8') as f:
                f.write("--- CHINESE VERSION ---\n\n")
                f.write(chinese_content + "\n\n")
                f.write("--- ENGLISH VERSION ---\n\n")
                f.write(english_content + "\n\n")
            saved_files.append(full_filename)
            print(f"✅ Combined content saved to: {full_filename}")
        except Exception as e:
            print(f"❌ Error saving combined content: {str(e)}")
    
    return saved_files

def main():
    """Main function parsing command line arguments"""
    parser = argparse.ArgumentParser(description="Folktale Generator Client")
    parser.add_argument("--menu", "-m", action="store_true", 
                        help="Start in interactive menu mode (default is command mode)")
    parser.add_argument("--command", "-c", type=str, 
                        help="Execute a single command and exit")
    parser.add_argument("--auto", "-a", action="store_true",
                        help="Start in auto mode (quick story generation)")
    
    args = parser.parse_args()
    
    if args.auto:
        # Start in auto mode
        auto_mode()
    elif args.command:
        # Execute single command mode
        if args.command == "start":
            guided_start_story()
        elif args.command == "next":
            next_turn()
        elif args.command == "arcs":
            list_story_arcs()
        elif args.command == "status":
            check_active_story()
        elif args.command.startswith("language "):
            lang = args.command.split()[1]
            if lang in ["en", "zh", "both"]:
                change_language(lang)
            else:
                print(f"❌ Invalid language: {lang}")
        elif args.command == "roll":
            roll_die()
        else:
            print(f"❌ Unknown command: {args.command}")
    elif args.menu:
        # Start in menu mode
        interactive_mode()
    else:
        # Start in command line mode
        command_line_mode()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")