#!/usr/bin/env python3
import requests
import json
import sys
import os
import argparse
import time
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
        response = requests.post(f"{SERVER_URL}/start_story", 
                                 json=data, 
                                 headers={"Content-Type": "application/json"})
        
        if response.status_code != 200:
            print(f"❌ Error: Server returned status code {response.status_code}")
            print(response.text)
            return None
        
        story_data = response.json()
        display_story_turn(story_data, is_opening=True)
        return story_data
    
    except Exception as e:
        print(f"❌ Error starting story: {e}")
        return None

def next_turn():
    """Generate the next turn of the story"""
    print("⏭️ GENERATING NEXT TURN")
    
    try:
        response = requests.post(f"{SERVER_URL}/next_turn")
        
        if response.status_code != 200:
            print(f"❌ Error: Server returned status code {response.status_code}")
            print(response.text)
            return None
        
        story_data = response.json()
        display_story_turn(story_data)
        return story_data
    
    except Exception as e:
        print(f"❌ Error generating next turn: {e}")
        return None

def display_story_turn(data, is_opening=False):
    """Display story content in a well-formatted way"""
    print_separator()
    
    # For Chinese-only content
    if "narrative_zh" in data and data.get("language") == "zh":
        print("🇨🇳 CHINESE NARRATIVE:")
        zh_content = data.get("narrative_zh") or ""
        if zh_content:
            print(zh_content)
        else:
            print("[No Chinese content available]")
        # Don't display any other narrative sections
        
    # For bilingual content
    elif "narrative_zh" in data and "narrative_en" in data:
        print("🇨🇳 CHINESE NARRATIVE:")
        zh_content = data.get("narrative_zh") or ""
        if zh_content:
            print(zh_content)
        else:
            print("[No Chinese content available]")
            
        print("\n🇬🇧 ENGLISH NARRATIVE:")
        en_content = data.get("narrative_en") or ""
        if en_content:
            print(en_content)
        else:
            print("[No English content available]")
            
    # For English-only content
    elif "narrative" in data:
        print("📖 NARRATIVE:")
        print(data["narrative"])
    
    print_separator()
    
    # Print story metadata
    if is_opening:
        print(f"Story ID: {data.get('story_id', 'unknown')}")
        print(f"Language: {data.get('language', 'unknown')}")
        if "seed_from" in data:
            print(f"Seed Source: {data.get('seed_from', 'unknown')}")
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
    """Save the current story narrative to a file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        story_id = story_data.get("story_id", "unknown")
        filename = f"story_{story_id}_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"FOLKTALE STORY: {story_data.get('story_id', 'Unknown ID')}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Write narrative content based on language
            if "narrative_so_far" in story_data:
                for i, narrative in enumerate(story_data["narrative_so_far"]):
                    f.write(f"--- Turn {i} ---\n\n")
                    f.write(narrative + "\n\n")
            
            # Handle bilingual or single narrative from individual turns
            elif "narrative_zh" in story_data and "narrative_en" in story_data:
                f.write("CHINESE:\n")
                f.write(story_data["narrative_zh"] + "\n\n")
                f.write("ENGLISH:\n")
                f.write(story_data["narrative_en"] + "\n\n")
            elif "narrative" in story_data:
                f.write(story_data["narrative"] + "\n\n")
            
            # Add metadata
            f.write("-" * 40 + "\n")
            f.write(f"Language: {story_data.get('language', 'unknown')}\n")
            f.write(f"Cosmic Position: {story_data.get('cosmic_position', 'unknown')}\n")
            
            if "elements" in story_data:
                f.write("Elements:\n")
                for key, value in story_data["elements"].items():
                    if isinstance(value, dict) and "zh" in value and "en" in value:
                        f.write(f"  {key}: {value['zh']} / {value['en']}\n")
                    else:
                        f.write(f"  {key}: {value}\n")
        
        print(f"✅ Story saved to: {filename}")
        return filename
    
    except Exception as e:
        print(f"❌ Error saving story to file: {e}")
        return None

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
    default_filename = f"story_{story_id}_{timestamp}.txt"
    
    filename = input(f"Enter filename [default: {default_filename}]: ").strip()
    if not filename:
        filename = default_filename
    
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
    print("  7. Roll the story die")
    print("  8. Help")
    print("  9. Exit\n")
    return input("Enter your choice (1-9): ").strip()

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
            roll_die()
        elif choice == "8":
            display_help_menu()
        elif choice == "9":
            print("\nGoodbye! 👋")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 9.")
        
        # Pause before returning to the main menu
        input("\nPress Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen

def command_line_mode():
    """Process input as commands in a simpler interactive mode"""
    print("\n📚 FOLKTALE GENERATOR COMMAND MODE 📚\n")
    print("Type 'help' for a list of commands, or 'menu' for guided menu\n")
    
    while True:
        command = input("\nCommand > ").strip().lower()
        parts = command.split()
        base_cmd = parts[0] if parts else ""
        
        if base_cmd in ["exit", "quit"]:
            print("Goodbye! 👋")
            break
        
        elif base_cmd == "menu":
            interactive_mode()
            
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

def main():
    """Main function parsing command line arguments"""
    parser = argparse.ArgumentParser(description="Folktale Generator Client")
    parser.add_argument("--menu", "-m", action="store_true", 
                        help="Start in interactive menu mode (default is command mode)")
    parser.add_argument("--command", "-c", type=str, 
                        help="Execute a single command and exit")
    
    args = parser.parse_args()
    
    if args.command:
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