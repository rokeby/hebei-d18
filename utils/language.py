"""Language utility classes and functions."""

class Language:
    """Enumeration of supported languages."""
    CHINESE = "zh"
    ENGLISH = "en"
    BILINGUAL = "both"

def parse_bilingual_response(response: str) -> dict:
    """Parse a bilingual response to extract Chinese and English parts."""
    lines = response.strip().split('\n')
    chinese_text = []
    english_text = []
    current_section = None
    
    # Look for section markers first
    chinese_found = False
    english_found = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        lower_line = line.lower()
        
        # Check for explicit section markers
        if any(marker in lower_line for marker in ["chinese version", "中文", "chinese:", "中文版"]):
            current_section = "zh"
            chinese_found = True
            continue
        elif any(marker in lower_line for marker in ["english translation", "english version", "英文", "english:", "英文版"]):
            current_section = "en"
            english_found = True
            continue
        
        # If we've found a section marker, add content to the appropriate section
        if current_section == "zh":
            chinese_text.append(line)
        elif current_section == "en":
            english_text.append(line)
    
    # If we didn't find explicit markers, try to infer based on content
    if not (chinese_found and english_found):
        # Reset and try a different approach
        chinese_text = []
        english_text = []
        
        # Identify which lines contain Chinese characters
        chinese_lines = []
        for i, line in enumerate(lines):
            if not line.strip():
                continue
                
            # Count Chinese characters
            chinese_char_count = sum(1 for char in line if '\u4e00' <= char <= '\u9fff')
            is_chinese = chinese_char_count > 0
            
            if is_chinese:
                chinese_lines.append(i)
        
        # If we found Chinese lines, assume everything before is Chinese and after is English
        if chinese_lines:
            max_chinese_line = max(chinese_lines)
            
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                    
                if i <= max_chinese_line:
                    chinese_text.append(line)
                else:
                    english_text.append(line)
    
    # Join the sections
    zh_content = "\n".join(chinese_text).strip()
    en_content = "\n".join(english_text).strip()
    
    # Debug information
    print(f"DEBUG: Chinese content length: {len(zh_content)} characters")
    print(f"DEBUG: English content length: {len(en_content)} characters")
    
    return {
        "zh": zh_content,
        "en": en_content
    }