"""Language utility classes and functions."""

class Language:
    """Enumeration of supported languages."""
    CHINESE = "zh"
    ENGLISH = "en"
    BILINGUAL = "both"

def parse_bilingual_response(response: str) -> dict:
    """Parse a bilingual response to extract Chinese and English parts."""
    # Simple parsing strategy - try to detect Chinese vs English
    lines = response.strip().split('\n')
    chinese_text = []
    english_text = []
    current_section = "zh"  # Start with Chinese assumption
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line contains mostly Chinese characters
        chinese_char_count = sum(1 for char in line if '\u4e00' <= char <= '\u9fff')
        is_chinese = chinese_char_count > len(line) * 0.5
        
        # Detect section change based on character composition
        if current_section == "zh" and not is_chinese:
            current_section = "en"
        
        # Add to appropriate section
        if current_section == "zh":
            chinese_text.append(line)
        else:
            english_text.append(line)
    
    return {
        "zh": "\n".join(chinese_text),
        "en": "\n".join(english_text)
    }