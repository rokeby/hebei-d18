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

    # Process each line
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Check for section markers
        lower_line = line.lower()
        if any(marker in lower_line for marker in ["chinese version", "中文", "chinese:", "中文版"]):
            current_section = "zh"
            continue  # Skip the marker line
        elif any(marker in lower_line for marker in ["english translation", "english version", "英文", "english:", "英文版"]):
            current_section = "en"
            continue  # Skip the marker line
        
        # If no marker found yet, check content
        if current_section is None:
            # Count Chinese characters
            chinese_char_count = sum(1 for char in line if '\u4e00' <= char <= '\u9fff')
            is_mostly_chinese = chinese_char_count > len(line) * 0.2  # Lower threshold to catch mixed lines
            
            if is_mostly_chinese:
                current_section = "zh"
            else:
                current_section = "en"
        
        # Add to the appropriate section
        if current_section == "zh":
            chinese_text.append(line)
        else:
            english_text.append(line)
    
    # Join the sections
    zh_content = "\n".join(chinese_text).strip()
    en_content = "\n".join(english_text).strip()
    
    # Checking for repetition requires external state and shouldn't be done here
    # Instead, let's return both parts and handle repetition elsewhere
    
    return {
        "zh": zh_content,
        "en": en_content
    }