"""Prompt generation for the folktale generator."""

from typing import Dict

from utils.language import Language
from engine.state import StoryState
from cosmology.wuxing import WuXing

def create_prompt(state: StoryState, elements: Dict, action_type: str, wuxing: WuXing) -> str:
    """Build the prompt for the LLM based on current state and elements, incorporating story arc with Han elements.
    
    Args:
        state: The current story state.
        elements: Story elements to include in the narrative.
        action_type: The current action type.
        wuxing: The Wu Xing system for cosmological references.
        
    Returns:
        A formatted prompt for the language model.
    """
    lang = state.language
    cosmic_element = elements["cosmic_element"]
    
    # Get element properties in appropriate language
    element_props = wuxing.get_bilingual_properties(cosmic_element, lang)
    element_name = wuxing.get_element_text(cosmic_element, lang)


    # Handle action_type_text safely
    if hasattr(state, 'story_engine') and state.story_engine and hasattr(state.story_engine, 'die'):
        action_type_text = state.story_engine.die.get_action_type_bilingual(action_type, lang)
    else:
        # Fallback to simple format when story_engine not available
        action_type_text = action_type
    
    # Get current narrative stage and guidance
    current_stage = state.story_arc.get_current_stage(lang)
    stage_guidance = state.story_arc.get_stage_guidance(lang)
    
    # Get related traditional literature and motifs
    related_texts = state.story_arc.get_related_literature(lang)
    motifs = state.story_arc.get_motifs(lang)
    
    # Build base prompt with story arc information and Han dynasty references
    if lang == Language.CHINESE:
        prompt_base = _create_chinese_prompt(state, element_name, element_props, 
                                            action_type_text, current_stage, 
                                            stage_guidance, related_texts, motifs)
    elif lang == Language.ENGLISH:
        prompt_base = _create_english_prompt(state, element_name, element_props, 
                                            action_type_text, current_stage, 
                                            stage_guidance, related_texts, motifs)
    else:  # BILINGUAL
        prompt_base = _create_bilingual_prompt(state, element_name, element_props, 
                                              action_type_text, current_stage, 
                                              stage_guidance, related_texts, motifs)
    
    # Add thematic elements if they exist
    if state.story_arc.theme_elements:
        prompt_base += _add_thematic_elements(state.story_arc.theme_elements, lang)
    
    # Add elements based on language
    prompt_base += _add_story_elements(elements, lang)
    
    # Add style instructions with Han dynasty specific guidance
    prompt_base += _add_style_instructions(lang, current_stage)
    
    return prompt_base

def _create_chinese_prompt(state, element_name, element_props, action_type_text, 
                          current_stage, stage_guidance, related_texts, motifs):
    """Create the base prompt in Chinese."""
    return f"""
        你是一位精通汉代传统的故事大师。
        请继续以下故事，添加新的情节发展。不要重复前面的内容，只需继续故事。

        故事结构: {state.story_arc.arc_data['description_zh']}
        当前阶段: {current_stage}
        阶段指导: {stage_guidance}
        {related_texts}
        {motifs}

        当前五行元素: {element_name} (季节: {element_props['season']}, 方向: {element_props['direction']}, 颜色: {element_props['color']})
        动作类型: {action_type_text}
        当前回合: {state.current_turn + 1}/{state.max_turns}

        前一段落: {state.previous_sentence_zh}

        请在你的新叙述中包含以下元素:
        """

def _create_english_prompt(state, element_name, element_props, action_type_text, 
                          current_stage, stage_guidance, related_texts, motifs):
    """Create the base prompt in English."""
    return f"""You are a master storyteller versed in Han dynasty (206 BCE-220 CE) traditions and folklore.
Continue the following story with a single paragraph.

Story arc: {state.story_arc.arc_data['description']}
Current stage: {current_stage}
Stage guidance: {stage_guidance}
{related_texts}
{motifs}

Current cosmic element: {element_name} (season: {element_props['season']}, direction: {element_props['direction']}, color: {element_props['color']})
Action type: {action_type_text}
Current turn: {state.current_turn + 1}/{state.max_turns}

Previous narrative: {state.previous_sentence}

Include these elements in your continuation:
"""

def _create_bilingual_prompt(state, element_name, element_props, action_type_text, 
                            current_stage, stage_guidance, related_texts, motifs):
    """Create the base prompt for bilingual output."""
    return f"""You are a master storyteller of Han dynasty (206 BCE-220 CE) folktales, deeply versed in traditional Chinese narratives and cosmology. Your task is to continue a story in BOTH Chinese and English.
First write a paragraph in Chinese, then provide its English translation.

Story arc: {state.story_arc.arc_data['description']} / {state.story_arc.arc_data['description_zh']}
Current stage: {current_stage}
Stage guidance: 
- Chinese: {stage_guidance['zh'] if isinstance(stage_guidance, dict) else ''}
- English: {stage_guidance['en'] if isinstance(stage_guidance, dict) else stage_guidance}
{related_texts}
{motifs}

Current cosmic element: {element_name}
Season: {element_props['season']}
Direction: {element_props['direction']}
Color: {element_props['color']}
Virtue: {element_props['virtue']}
Celestial animal: {element_props['animal']}

Action type: {action_type_text}
Current turn: {state.current_turn + 1}/{state.max_turns}

Previous Chinese narrative: {state.previous_sentence_zh}
Previous English narrative: {state.previous_sentence}

Include these elements in your continuation:
"""

def _add_thematic_elements(theme_elements, lang):
    """Add thematic elements to the prompt."""
    if lang == Language.CHINESE:
        result = "\n故事主题元素:\n"
    elif lang == Language.ENGLISH:
        result = "\nThematic elements for consistency:\n"
    else:  # BILINGUAL
        result = "\nThematic elements for consistency / 故事主题元素:\n"
    
    for key, value in theme_elements.items():
        result += f"- {key}: {value}\n"
    
    return result

def _add_story_elements(elements, lang):
    """Add story elements to the prompt."""
    result = ""
    for key, value in elements.items():
        if key != "cosmic_element":
            if isinstance(value, dict) and "zh" in value and "en" in value:
                if lang == Language.CHINESE:
                    result += f"\n- {key}: {value['zh']}"
                elif lang == Language.ENGLISH:
                    result += f"\n- {key}: {value['en']}"
                else:  # BILINGUAL
                    result += f"\n- {key}: {value['zh']} / {value['en']}"
            else:
                result += f"\n- {key}: {value}"
    
    return result

def _add_style_instructions(lang, current_stage):
    """Add style instructions to the prompt."""
    if lang == Language.CHINESE:
        return f"""
            写作要求:
            - 以汉代民间故事风格写作，融入五行、阴阳等传统宇宙观念
            - 使用古典文化知识，但避免直接引用具体书名以保持阅读流畅
            - 只写纯粹的故事叙述(2-3句)，不要解释或评论
            - 避免在正文中出现《书名》格式的引用

            现在请继续故事:
                """
    elif lang == Language.ENGLISH:
        return f"\n\nWrite in a style authentic to Han dynasty folklore, referencing elements from classical texts like Huainanzi, Records of the Seeking of Spirits, or Records of the Grand Historian. Incorporate the qualities and seasonal aspects of the current cosmic element. Ensure your narrative advances the current story stage ({current_stage}) appropriately. Your style should evoke the mystery, moral dimensions, and cosmological worldview characteristic of Han dynasty stories."
    else:  # BILINGUAL
        return f"\n\nFormat your response with the Chinese paragraph first, followed by its English translation. Write in a style authentic to Han dynasty folklore, referencing elements from classical texts like 《淮南子》(Huainanzi), 《搜神记》(Records of the Seeking of Spirits), or 《史记》(Records of the Grand Historian). Incorporate the qualities of the current cosmic element. Ensure your narrative advances the current story stage ({current_stage}) appropriately.\n\nVERY IMPORTANT: Your response MUST contain BOTH Chinese and English versions. First write in Chinese, then provide the English translation. Make sure both tell the same story but are culturally appropriate in each language."