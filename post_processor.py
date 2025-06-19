#!/usr/bin/env python3
"""
Post-processing module for Han dynasty folktales.
Takes completed stories from archived_tales and improves them through editorial review.
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client for DeepSeek
client = OpenAI(
    base_url="https://api.deepseek.com",
    timeout=120.0
)

def scan_archived_tales() -> List[str]:
    """Scan archived_tales folder for completed Chinese story files."""
    archived_dir = "./archived_tales"
    if not os.path.exists(archived_dir):
        print(f"❌ Archive directory not found: {archived_dir}")
        return []
    
    # Look for Chinese story files with the completed format
    story_files = []
    for filename in os.listdir(archived_dir):
        if filename.endswith("_zh.txt") and any(arc in filename for arc in [
            "friendship-journey", "kind-deed-reward", "festival-adventure", 
            "learning-wisdom", "nature-harmony", "brave-little-hero"
        ]):
            story_files.append(os.path.join(archived_dir, filename))
    
    return sorted(story_files)

def extract_story_data(filepath: str) -> Optional[Dict]:
    """Extract story content and metadata from a completed story file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Initialize data structure
        story_data = {
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "chinese_narrative": "",
            "objects": [],
            "arc_type": "unknown",
            "cosmic_positions": [],
            "turns": 0,
            "word_count": 0
        }
        
        # Extract arc type from filename
        filename = story_data["filename"]
        for arc in ["friendship-journey", "kind-deed-reward", "festival-adventure", 
                   "learning-wisdom", "nature-harmony", "brave-little-hero"]:
            if arc in filename:
                story_data["arc_type"] = arc
                break
        
        # Extract summary section if present
        summary_match = re.search(r"=== STORY COMPLETED ===\n(.*?)\n========================", content, re.DOTALL)
        if summary_match:
            summary = summary_match.group(1)
            
            # Extract turns
            turns_match = re.search(r"Number of Turns: (\d+)", summary)
            if turns_match:
                story_data["turns"] = int(turns_match.group(1))
            
            # Extract cosmic positions
            cosmic_match = re.search(r"Cosmic Positions: (.+)", summary)
            if cosmic_match:
                positions = cosmic_match.group(1).split(' → ')
                story_data["cosmic_positions"] = [pos.strip() for pos in positions]
        
        # Extract Chinese narrative content (everything after summary and header)
        narrative_parts = []
        
        # Split content by turns
        turn_sections = re.split(r"--- Turn \d+ ---", content)
        
        for section in turn_sections:
            # Skip the header/summary section
            if "FOLKTALE STORY:" in section or "=== STORY COMPLETED ===" in section:
                continue
            
            # Clean up the section
            cleaned = section.strip()
            
            # Remove metadata lines (lines starting with specific patterns)
            lines = cleaned.split('\n')
            narrative_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Skip metadata lines
                if any(line.startswith(prefix) for prefix in [
                    "📖 STORY STATUS:", "ID:", "Turn:", "Cosmic Position:", "Language:",
                    "🎲 ACTION TYPE:", "🌟 Cosmic position:", "🎴 ELEMENTS SELECTED:",
                    "character:", "object:", "place:", "event:", "intervention:",
                    "cosmic_element:"
                ]):
                    continue
                
                # This is narrative content
                narrative_lines.append(line)
            
            if narrative_lines:
                narrative_parts.append('\n'.join(narrative_lines))
        
        # Combine all narrative parts
        story_data["chinese_narrative"] = '\n\n'.join(narrative_parts).strip()
        story_data["word_count"] = len(story_data["chinese_narrative"])
        
        # Extract objects from metadata sections
        objects_pattern = r"object: ([^\n]+)"
        object_matches = re.findall(objects_pattern, content)
        story_data["objects"] = list(set(object_matches))  # Remove duplicates
        
        print(f"✅ Extracted story data from {filename}")
        print(f"   Arc: {story_data['arc_type']}")
        print(f"   Turns: {story_data['turns']}")
        print(f"   Word count: {story_data['word_count']}")
        print(f"   Objects: {len(story_data['objects'])}")
        print(f"   Cosmic positions: {' → '.join(story_data['cosmic_positions'])}")
        
        return story_data
        
    except Exception as e:
        print(f"❌ Error extracting data from {filepath}: {str(e)}")
        return None

def create_editorial_prompt(story_data: Dict) -> str:
    """Create a prompt for editorial assessment and rewriting."""
    
    objects_list = "、".join(story_data["objects"]) if story_data["objects"] else "无特定物品"
    cosmic_positions = " → ".join(story_data["cosmic_positions"])
    
    prompt = f"""你是一位专业的儿童文学编辑，精通中国古代文化和汉代历史。请对以下儿童故事进行编辑改进。

故事信息：
- 故事类型：{story_data["arc_type"]}
- 五行轨迹：{cosmic_positions}
- 出现的汉代文物：{objects_list}
- 原始字数：{story_data["word_count"]}字

原始故事内容：
{story_data["chinese_narrative"]}

请完成以下任务：

1. 结构分析：评估故事的叙事结构、节奏和连贯性
2. 故事改写：重写整个故事，确保：
   - 保持儿童友好的语言和主题
   - 保留所有汉代文物，并让它们在故事中发挥重要作用
   - 改善故事的整体流畅性和连贯性
   - 加强情节发展和角色成长
   - 保持古代中国文化背景的真实性
   - 确保故事有明确的开头、发展、高潮和结尾
3. 故事标题：为改进后的故事创作一个吸引人的中文标题（6-10个字）

请按以下格式回答：

【结构分析】
[对原故事的分析评价]

【改进故事】
[完整的重写故事，确保流畅连贯]

【故事标题】
[6-10个字的中文标题]

注意：改写的故事应该是一个完整、连贯的叙述，而不是分段的。请确保所有汉代文物都在故事中有意义地出现。"""

    return prompt

def call_deepseek_api(prompt: str) -> Optional[str]:
    """Call DeepSeek API for editorial processing."""
    try:
        messages = [
            {
                "role": "system", 
                "content": "你是一位专业的儿童文学编辑，擅长改进和完善儿童故事，特别是中国古代背景的故事。你的任务是提高故事的文学质量，同时保持其教育价值和文化真实性。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent editorial quality
            max_tokens=4000
        )
        
        response = completion.choices[0].message.content.strip()
        
        # Log token usage
        print(f"🔢 Token usage - Prompt: {completion.usage.prompt_tokens}, "
              f"Completion: {completion.usage.completion_tokens}, "
              f"Total: {completion.usage.total_tokens}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error calling DeepSeek API: {str(e)}")
        return None

def parse_editorial_response(response: str) -> Optional[Dict]:
    """Parse the editorial response to extract components."""
    try:
        # Extract structural analysis
        analysis_match = re.search(r"【结构分析】\s*\n(.*?)(?=【改进故事】)", response, re.DOTALL)
        analysis = analysis_match.group(1).strip() if analysis_match else ""
        
        # Extract improved story
        story_match = re.search(r"【改进故事】\s*\n(.*?)(?=【故事标题】)", response, re.DOTALL)
        improved_story = story_match.group(1).strip() if story_match else ""
        
        # Extract title
        title_match = re.search(r"【故事标题】\s*\n(.+)", response)
        title = title_match.group(1).strip() if title_match else ""
        
        # Clean up title (remove quotes, brackets, etc.)
        title = re.sub(r'[「」『』"""''《》【】]', '', title).strip()
        
        if not improved_story or not title:
            print("❌ Could not parse editorial response properly")
            return None
        
        return {
            "analysis": analysis,
            "improved_story": improved_story,
            "title": title
        }
        
    except Exception as e:
        print(f"❌ Error parsing editorial response: {str(e)}")
        return None

def save_improved_story(story_data: Dict, editorial_result: Dict) -> str:
    """Save the improved story to completed_tales folder."""
    # Create completed_tales directory
    completed_dir = "./completed_tales"
    os.makedirs(completed_dir, exist_ok=True)
    
    # Generate filename: YYMMDD_ArcType_StoryTitle_Wordcount
    date_str = datetime.now().strftime("%y%m%d")
    arc_type = story_data["arc_type"].replace("-", "")  # Remove hyphens
    title = editorial_result["title"]
    word_count = len(editorial_result["improved_story"])
    
    # Clean title for filename (remove special characters)
    clean_title = re.sub(r'[^\w\u4e00-\u9fff]', '', title)
    
    filename = f"{date_str}_{arc_type}_{clean_title}_{word_count}.txt"
    filepath = os.path.join(completed_dir, filename)
    
    # Create file content
    objects_list = "、".join(story_data["objects"]) if story_data["objects"] else "无特定物品"
    cosmic_positions = " → ".join(story_data["cosmic_positions"])
    
    content = f"""故事标题：{editorial_result["title"]}
生成日期：{datetime.now().strftime("%Y年%m月%d日")}
故事类型：{story_data["arc_type"]}
字数统计：{word_count}字
五行轨迹：{cosmic_positions}
出现文物：{objects_list}

{'='*60}

{editorial_result["improved_story"]}

{'='*60}

编辑分析：
{editorial_result["analysis"]}

原始文件：{story_data["filename"]}
处理时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Improved story saved as: {filename}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error saving improved story: {str(e)}")
        return None

def process_single_story(filepath: str) -> bool:
    """Process a single story file through editorial improvement."""
    print(f"\n📝 Processing: {os.path.basename(filepath)}")
    
    # Extract story data
    story_data = extract_story_data(filepath)
    if not story_data:
        return False
    
    # Skip if narrative is too short
    if story_data["word_count"] < 50:
        print(f"⚠️ Story too short ({story_data['word_count']} chars), skipping")
        return False
    
    # Create editorial prompt
    prompt = create_editorial_prompt(story_data)
    
    # Call DeepSeek API
    print("🤖 Sending to DeepSeek for editorial review...")
    response = call_deepseek_api(prompt)
    if not response:
        return False
    
    # Parse response
    editorial_result = parse_editorial_response(response)
    if not editorial_result:
        return False
    
    print(f"📖 Generated title: {editorial_result['title']}")
    print(f"📊 Improved story length: {len(editorial_result['improved_story'])} characters")
    
    # Save improved story
    saved_path = save_improved_story(story_data, editorial_result)
    
    return saved_path is not None

def process_all_stories() -> Dict:
    """Process all stories in archived_tales folder."""
    print("🔍 Scanning for completed stories...")
    
    story_files = scan_archived_tales()
    if not story_files:
        print("❌ No completed story files found in archived_tales")
        return {"processed": 0, "failed": 0, "skipped": 0}
    
    print(f"📚 Found {len(story_files)} story files to process")
    
    results = {"processed": 0, "failed": 0, "skipped": 0}
    
    for i, filepath in enumerate(story_files, 1):
        print(f"\n{'='*60}")
        print(f"Processing story {i}/{len(story_files)}")
        print(f"{'='*60}")
        
        try:
            # Check if already processed
            filename = os.path.basename(filepath)
            date_part = filename.split('_')[0]
            
            # Look for existing processed version
            completed_dir = "./completed_tales"
            if os.path.exists(completed_dir):
                existing_files = [f for f in os.listdir(completed_dir) 
                                if f.startswith(date_part) and any(arc in f for arc in [
                                    "friendshipjourney", "kinddeedreward", "festivaladventure",
                                    "learningwisdom", "natureharmony", "bravelittlehero"
                                ])]
                if existing_files:
                    print(f"⏭️ Already processed (found {existing_files[0]}), skipping")
                    results["skipped"] += 1
                    continue
            
            success = process_single_story(filepath)
            if success:
                results["processed"] += 1
                print(f"✅ Successfully processed story {i}")
            else:
                results["failed"] += 1
                print(f"❌ Failed to process story {i}")
                
        except Exception as e:
            print(f"❌ Error processing {filepath}: {str(e)}")
            results["failed"] += 1
        
        # Brief pause between stories to be respectful to API
        if i < len(story_files):
            print("⏸️ Brief pause...")
            import time
            time.sleep(2)
    
    return results

def display_processing_summary(results: Dict):
    """Display a summary of the processing results."""
    print(f"\n{'='*60}")
    print("🎉 POST-PROCESSING COMPLETED!")
    print(f"{'='*60}")
    print(f"📊 SUMMARY:")
    print(f"   Stories Processed: {results['processed']}")
    print(f"   Stories Failed: {results['failed']}")
    print(f"   Stories Skipped: {results['skipped']}")
    print(f"   Total Files Found: {sum(results.values())}")
    print()
    
    if results["processed"] > 0:
        print(f"✅ Successfully improved {results['processed']} stories!")
        print(f"📁 Check the 'completed_tales' folder for the editorial versions.")
    
    if results["failed"] > 0:
        print(f"⚠️ {results['failed']} stories could not be processed.")
    
    if results["skipped"] > 0:
        print(f"ℹ️ {results['skipped']} stories were skipped (already processed).")

def main():
    """Main function for command-line usage."""
    print("📝 Han Dynasty Folktale Post-Processor")
    print("=====================================")
    
    # Check if archived_tales exists
    if not os.path.exists("./archived_tales"):
        print("❌ No archived_tales directory found. Generate some stories first!")
        return
    
    # Ask user what they want to do
    print("\nWhat would you like to do?")
    print("1. Process all stories")
    print("2. Process a specific story")
    print("3. Just scan and show available stories")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        results = process_all_stories()
        display_processing_summary(results)
    
    elif choice == "2":
        story_files = scan_archived_tales()
        if not story_files:
            print("❌ No story files found")
            return
        
        print("\nAvailable stories:")
        for i, filepath in enumerate(story_files, 1):
            print(f"  {i}. {os.path.basename(filepath)}")
        
        try:
            selection = int(input(f"Select story (1-{len(story_files)}): ")) - 1
            if 0 <= selection < len(story_files):
                success = process_single_story(story_files[selection])
                if success:
                    print("✅ Story successfully processed!")
                else:
                    print("❌ Failed to process story")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")
    
    elif choice == "3":
        story_files = scan_archived_tales()
        print(f"\n📚 Found {len(story_files)} completed story files:")
        for filepath in story_files:
            print(f"  - {os.path.basename(filepath)}")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
