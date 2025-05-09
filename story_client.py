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

def next_turn():
    """Generate the next turn of the story"""
    print("⏭️ GENERATING NEXT TURN")
    
    try:
        # Make request to the API
        response = requests.post(f"{SERVER_URL}/next_turn")
        
        # Check for error
        if response.status_code != 200:
            print(f"❌ Error: Server returned status code {response.status_code}")
            print(response.text)
            return None
        
        # Parse the response
        story_data = response.json()
        
        # Log the raw response for debugging
        print(f"DEBUG: API Response length: {len(str(story_data))} characters")
        
        # Display the story turn
        display_story_turn(story_data)
        
        # Check if the story has reached its conclusion
        if story_data.get('remaining_turns', 1) <= 0:
            print("🏁 Story has reached its conclusion!")
            
            # Check language and offer appropriate save option
            is_bilingual = story_data.get('language') == "both"
            
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
        print(f"❌ Error generating next turn: {str(e)}")
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
    """Display story content in a well-formatted way"""
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
    
    # Display Chinese content if available
    if has_chinese:
        print("\n🇨🇳 CHINESE NARRATIVE:")
        print(data["narrative_zh"])
    
    # Display English content if available
    if has_english:
        print("\n🇬🇧 ENGLISH NARRATIVE:")
        print(data["narrative_en"])
    elif has_single_narrative:
        print("\n📖 NARRATIVE:")
        print(data["narrative"])
    
    # If no narrative content found, display a warning
    if not (has_chinese or has_english or has_single_narrative):
        print("\n⚠️ NO NARRATIVE CONTENT FOUND")
        if "raw_response" in keys:
            print("\nRaw LLM Response:")
            print(data["raw_response"])
    
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
        print(f"Cosmic Element: {data.get('cosmic_position', 'unknown')}")
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

def check_active_story():
    """Check if there's an active story and display its status"""
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
        
        if "narrative_so_far" in story_data and story_data["narrative_so_far"]:
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
        # For bilingual stories, we'll save two files - just prepare the path for now
        # This will be handled separately
        final_filename = os.path.join(archive_dir, f"full_{filename}.txt")
    else:  # default to English
        final_filename = os.path.join(archive_dir, f"en_{filename}.txt")
    
    # Common header content for all files
    header_content = f"{'=' * 80}\n"
    header_content += f"FOLKTALE STORY: {story_data.get('story_id', 'Unknown ID')}\n"
    header_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header_content += f"{'=' * 80}\n\n"
    
    # Debug what data we have available
    print("\nDEBUG: Story Data Keys:")
    for key in story_data.keys():
        if isinstance(story_data[key], str):
            print(f"{key}: {len(story_data[key])} chars")
        else:
            print(f"{key}: {type(story_data[key])}")
    
    # Special handling for bilingual stories
    if language == "both":
        # Call our specialized bilingual saving function
        return save_bilingual_story()
    
    # Get narrative content with better handling for Chinese-only stories
    content = ""
    if language == "zh":
        # Check for Chinese content in various possible locations
        if "narrative_zh" in story_data and story_data["narrative_zh"]:
            content = story_data["narrative_zh"]
            print(f"DEBUG: Found narrative_zh ({len(content)} chars)")
        elif "narrative" in story_data and story_data["narrative"]:
            # Some endpoints might put Chinese content in the narrative field
            if any('\u4e00' <= char <= '\u9fff' for char in story_data["narrative"]):
                content = story_data["narrative"]
                print(f"DEBUG: Found Chinese in narrative ({len(content)} chars)")
        elif "opening_narrative_zh" in story_data and story_data["opening_narrative_zh"]:
            content = story_data["opening_narrative_zh"]
            print(f"DEBUG: Found opening_narrative_zh ({len(content)} chars)")
    else:  # English or other languages
        if "narrative" in story_data and story_data["narrative"]:
            content = story_data["narrative"]
            print(f"DEBUG: Found narrative ({len(content)} chars)")
        elif "opening_narrative" in story_data and story_data["opening_narrative"]:
            content = story_data["opening_narrative"]
            print(f"DEBUG: Found opening_narrative ({len(content)} chars)")
    
    # If we didn't find content in the expected fields, look for Last Narrative
    if not content and "narrative_so_far" in story_data and story_data["narrative_so_far"]:
        last_narrative = story_data["narrative_so_far"][-1]
        content = last_narrative
        print(f"DEBUG: Using last narrative from narrative_so_far ({len(content)} chars)")
    
    # Extract narrative_thread content if available
    if not content and "narrative_thread" in story_data and story_data["narrative_thread"]:
        thread = story_data["narrative_thread"]
        assembled_content = []
        for i, turn in enumerate(thread):
            turn_content = ""
            if language == "zh" and "narrative_zh" in turn and turn["narrative_zh"]:
                turn_content = turn["narrative_zh"]
            elif "narrative" in turn and turn["narrative"]:
                turn_content = turn["narrative"]
            
            if turn_content:
                assembled_content.append(f"--- Turn {i} ---\n\n{turn_content}")
        
        if assembled_content:
            content = "\n\n".join(assembled_content)
            print(f"DEBUG: Assembled content from narrative_thread ({len(content)} chars)")
    
    # Finally, check active_story fields if nothing else worked
    if not content and "Last Narrative:" in str(story_data):
        # This is a bit of a hack, but sometimes the narrative is in a formatted string
        full_text = str(story_data)
        narrative_section = full_text.split("Last Narrative:", 1)[1].split("\n")[0].strip()
        content = narrative_section
        print(f"DEBUG: Extracted from Last Narrative section ({len(content)} chars)")
    
    # Save the content if we found any
    if content:
        try:
            with open(final_filename, 'w', encoding='utf-8') as f:
                f.write(header_content)
                f.write(content + "\n\n")
                f.write(f"{'-' * 40}\n")
                f.write(f"Language: {language}\n")
                f.write(f"Cosmic Position: {story_data.get('cosmic_position', 'unknown')}\n")
                
                # Add elements if available
                if "elements" in story_data:
                    f.write("Elements:\n")
                    for key, value in story_data["elements"].items():
                        if isinstance(value, dict) and "zh" in value and language == "zh":
                            f.write(f"  {key}: {value['zh']}\n")
                        elif isinstance(value, dict) and "en" in value and language != "zh":
                            f.write(f"  {key}: {value['en']}\n")
                        else:
                            f.write(f"  {key}: {value}\n")
            
            print(f"✅ Story saved to: {final_filename}")
            return final_filename
        except Exception as e:
            print(f"❌ Error saving story: {str(e)}")
            return None
    else:
        print("❌ No content found to save")
        return None

def save_bilingual_story(story_data=None, filename=None):
    """Save current bilingual story with separate Chinese and English files"""
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
        story_id = story_data.get("story_id", "unknown")
        filename = f"tale_{story_id}_{timestamp}"
    
    # Remove file extension if provided
    if filename.endswith(".txt"):
        filename = filename[:-4]
    
    # Common header content
    header_content = f"{'=' * 80}\n"
    header_content += f"FOLKTALE STORY: {story_data.get('story_id', 'Unknown ID')}\n"
    header_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header_content += f"{'=' * 80}\n\n"
    
    # Get narrative content
    chinese_content = ""
    english_content = ""
    
    # Get raw output directly from the console if available
    raw_output = None
    
    # Debug available keys
    print("DEBUG: Available keys in story_data:")
    for key in story_data.keys():
        print(f"  - {key}")
    
    # Check for content in narrative_thread
    if "narrative_thread" in story_data and story_data["narrative_thread"]:
        thread = story_data["narrative_thread"]
        chinese_parts = []
        english_parts = []
        
        print(f"DEBUG: Found narrative_thread with {len(thread)} entries")
        
        for i, turn in enumerate(thread):
            turn_keys = list(turn.keys())
            print(f"DEBUG: Turn {i} keys: {turn_keys}")
            
            if "narrative_zh" in turn and turn["narrative_zh"]:
                chinese_parts.append(f"--- Turn {i} ---\n\n{turn['narrative_zh']}")
                print(f"DEBUG: Found Chinese in turn {i}: {len(turn['narrative_zh'])} chars")
            
            if "narrative" in turn and turn["narrative"]:
                english_parts.append(f"--- Turn {i} ---\n\n{turn['narrative']}")
                print(f"DEBUG: Found English in turn {i}: {len(turn['narrative'])} chars")
        
        if chinese_parts:
            chinese_content = "\n\n".join(chinese_parts)
        
        if english_parts:
            english_content = "\n\n".join(english_parts)
    
    # Check for content in narrative_so_far
    elif "narrative_so_far" in story_data and story_data["narrative_so_far"]:
        narratives = story_data["narrative_so_far"]
        print(f"DEBUG: Found narrative_so_far with {len(narratives)} entries")
        
        # For each narrative, try to split into Chinese and English
        chinese_parts = []
        english_parts = []
        
        for i, narrative in enumerate(narratives):
            # Split the narrative based on Chinese characters
            parts = split_bilingual_text(narrative)
            
            if parts["zh"]:
                chinese_parts.append(f"--- Turn {i} ---\n\n{parts['zh']}")
                print(f"DEBUG: Found Chinese in narrative {i}: {len(parts['zh'])} chars")
            
            if parts["en"]:
                english_parts.append(f"--- Turn {i} ---\n\n{parts['en']}")
                print(f"DEBUG: Found English in narrative {i}: {len(parts['en'])} chars")
        
        if chinese_parts:
            chinese_content = "\n\n".join(chinese_parts)
        
        if english_parts:
            english_content = "\n\n".join(english_parts)
    
    # Check for single-turn content (like next_turn responses)
    else:
        if "narrative_zh" in story_data and story_data["narrative_zh"]:
            chinese_content = story_data["narrative_zh"]
            print(f"DEBUG: Found narrative_zh: {len(chinese_content)} chars")
        
        if "narrative_en" in story_data and story_data["narrative_en"]:
            english_content = story_data["narrative_en"]
            print(f"DEBUG: Found narrative_en: {len(english_content)} chars")
        elif "narrative" in story_data and story_data["narrative"]:
            english_content = story_data["narrative"]
            print(f"DEBUG: Found narrative: {len(english_content)} chars")
    
    # If we still don't have content, try to extract from Last Narrative
    if (not chinese_content or not english_content) and "Last Narrative:" in str(story_data):
        # Try to extract from the raw response data
        full_text = str(story_data)
        narrative_parts = full_text.split("Last Narrative:", 1)
        if len(narrative_parts) > 1:
            raw_narrative = narrative_parts[1].split("\n\n", 1)[0].strip()
            print(f"DEBUG: Extracted raw narrative: {len(raw_narrative)} chars")
            
            # Split by Chinese/English
            parts = split_bilingual_text(raw_narrative)
            
            if parts["zh"] and not chinese_content:
                chinese_content = parts["zh"]
                print(f"DEBUG: Extracted Chinese from raw: {len(chinese_content)} chars")
            
            if parts["en"] and not english_content:
                english_content = parts["en"]
                print(f"DEBUG: Extracted English from raw: {len(english_content)} chars")
    
    saved_files = []
    
    # Save Chinese content if available
    if chinese_content:
        zh_filename = os.path.join(archive_dir, f"zh_{filename}.txt")
        try:
            with open(zh_filename, 'w', encoding='utf-8') as f:
                f.write(header_content)
                f.write(chinese_content + "\n\n")
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
    if english_content:
        en_filename = os.path.join(archive_dir, f"en_{filename}.txt")
        try:
            with open(en_filename, 'w', encoding='utf-8') as f:
                f.write(header_content)
                f.write(english_content + "\n\n")
                f.write(f"{'-' * 40}\n")
                f.write(f"Language: English (en)\n")
                f.write(f"Cosmic Position: {story_data.get('cosmic_position', 'unknown')}\n")
            saved_files.append(en_filename)
            print(f"✅ English content saved to: {en_filename}")
        except Exception as e:
            print(f"❌ Error saving English version: {str(e)}")
    else:
        print("⚠️ No English content found to save")
    
    # If neither content was found, save the raw output as fallback
    if not saved_files:
        # Try to get the raw narrative from the active story
        full_filename = os.path.join(archive_dir, f"full_{filename}.txt")
        try:
            with open(full_filename, 'w', encoding='utf-8') as f:
                f.write(header_content)
                
                # Write whatever content we have
                if "narrative_so_far" in story_data and story_data["narrative_so_far"]:
                    for i, narrative in enumerate(story_data["narrative_so_far"]):
                        f.write(f"--- Turn {i} ---\n\n{narrative}\n\n")
                elif raw_output:
                    f.write(raw_output + "\n\n")
                else:
                    f.write("[No narrative content could be extracted]\n\n")
                    
                f.write(f"{'-' * 40}\n")
                f.write(f"Language: both\n")
                f.write(f"Cosmic Position: {story_data.get('cosmic_position', 'unknown')}\n")
            saved_files.append(full_filename)
            print(f"⚠️ Could not separate languages. Full content saved to: {full_filename}")
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
    if "Chinese Version:" in text or "中文版:" in text:
        parts = re.split(r"Chinese Version:|中文版:|English Translation:|英文版:", text, flags=re.IGNORECASE)
        if len(parts) >= 3:  # We have both markers
            chinese_section = parts[1].strip()
            english_section = parts[2].strip()
    
    # If no markers found, use character detection
    if chinese_section is None or english_section is None:
        # Identify language by character content
        lines = text.split("\n")
        
        current_section = None
        chinese_lines = []
        english_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Count Chinese characters
            chinese_char_count = sum(1 for char in line if '\u4e00' <= char <= '\u9fff')
            is_mostly_chinese = chinese_char_count > len(line) * 0.15  # Lower threshold to catch mixed lines
            
            if is_mostly_chinese:
                # If we were in English section, assume we've switched to Chinese
                if current_section == "en":
                    # Only switch if we have a substantial Chinese content
                    if chinese_char_count > 5:
                        current_section = "zh"
                else:
                    current_section = "zh"
                
                if current_section == "zh":
                    chinese_lines.append(line)
            else:
                # If we have almost no Chinese characters, it's probably English
                if current_section == "zh":
                    # Only switch if line has some content and very few Chinese characters
                    if len(line) > 10 and chinese_char_count < 2:
                        current_section = "en"
                else:
                    current_section = "en"
                    
                if current_section == "en":
                    english_lines.append(line)
        
        # If we got consistent sections
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
        # If the text contains Chinese characters, assume it's Chinese
        chinese_char_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        if chinese_char_count > 0:
            result["zh"] = text
        else:
            result["en"] = text
    
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

def display_help_menu():
    """Display help menu with available commands"""
    print_header("FOLKTALE GENERATOR HELP")
    print("Available commands:")
    print("  1. start - Start a new story")
    print("  2. next - Generate the next turn")
    print("  3. arcs - List available story arcs")
    print("  4. status - Check active story status")
    print("  5. language - Change story language")
    print("  6. save - Save current story to file")
    print("  7. roll - Roll the story die")
    print("  8. help - Display this help menu")
    print("  9. exit/quit - Exit the program")
    print("\nFor more details on any command, type 'help <command>'")

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
    """Guide the user through saving the story"""
    story_data = check_active_story()
    if not story_data:
        return None
    
    print_header("SAVE STORY")
    
    # Generate default filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    story_id = story_data.get("story_id", "unknown")
    default_filename = f"tale_{story_id}_{timestamp}"
    
    filename = input(f"Enter filename (without extension) [default: {default_filename}]: ").strip()
    if not filename:
        filename = default_filename
    
    # Check language and use appropriate saving method
    language = story_data.get("language", "unknown")
    if language == "both":
        return save_bilingual_story(story_data, filename)
    else:
        return save_story_to_file(story_data, filename)

def display_main_menu():
    """Display the main menu options"""
    print_header("FOLKTALE GENERATOR")
    print("What would you like to do?\n")
    print("  1. Start a new story")
    print("  2. Continue active story (next turn)")
    print("  3. Check story status")
    print("  4. List available story arcs")
    print("  5. Change story language")
    print("  6. Save story to file")
    print("  7. Save bilingual story (manual)")  # New option
    print("  8. Roll the story die")
    print("  9. Help")
    print("  0. Exit\n")
    return input("Enter your choice (0-9): ").strip()

def interactive_mode():
    """Run an interactive storytelling session with guided menus"""
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
            save_bilingual_story()  # New option
        elif choice == "8":
            roll_die()
        elif choice == "9":
            display_help_menu()
        elif choice == "0":
            print("\nGoodbye! 👋")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 0 and 9.")
        
        # Pause before returning to the main menu
        input("\nPress Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen

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