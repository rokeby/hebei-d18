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

    # SPECIAL EMPHASIS FOR OBJECTS - Add this new section:
    if action_type == "object_appearance" and "object" in elements:
        prompt_base += _add_object_emphasis(elements["object"], lang)
    
    # Add style instructions with Han dynasty specific guidance
    prompt_base += _add_style_instructions(lang, current_stage)
    
    return prompt_base


def _add_object_emphasis(object_item, lang):
    """Add special emphasis for when objects appear to make them central to the story."""
    if lang == Language.CHINESE:
        return f"""

        重要提示：这个物品应该是故事的核心元素！
    - 让这个{object_item}成为推动情节发展的关键
    - 赋予它特殊的魔法或意义，比如：
      * 铜镜可以显现神奇的景象
      * 玉佩能发出保护的光芒
      * 铜钟会奏出美妙的音乐
      * 陶俑可能会变成小朋友的朋友
    - 让角色与这个物品产生深刻的联系
    - 这个物品应该帮助解决问题或带来重要发现
        """
    elif lang == Language.ENGLISH:
        return f"""
        
    IMPORTANT: Make this object the central focus of the story segment!
    - Let this {object_item} be the key that drives the plot forward
    - Give it special magical properties or significance, such as:
      * Bronze mirrors showing magical reflections
      * Jade pendants glowing with protective power
      * Bronze bells playing enchanted melodies
      * Pottery figurines coming to life as helpful friends
    - Create a meaningful connection between characters and this object
    - This object should help solve problems or lead to important discoveries
        """
    else:  # BILINGUAL
        return f"""
        
        IMPORTANT / 重要提示: Make this object the central focus! / 让这个物品成为故事核心！
        - This {object_item} should drive the plot forward / 这个物品应该推动情节发展
        - Give it child-friendly magical properties while respecting its cultural significance
        - 让角色与物品产生深刻联系 / Create meaningful character-object connections
        - Use it to solve problems or make discoveries / 用它来解决问题或发现秘密
        """

def _create_chinese_prompt(state, element_name, element_props, action_type_text, 
                          current_stage, stage_guidance, related_texts, motifs):
    """Create the base prompt in Chinese."""
    return f"""
        你是一位善于为孩子们讲述温暖故事的故事老师。
        请继续以下儿童故事，添加新的有趣情节。不要重复前面的内容，只需继续故事。

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

def _add_style_instructions(lang, current_stage, action_type=None):
    """Add style instructions to the prompt with object emphasis when relevant."""
    base_instructions = {
        Language.CHINESE: """
            写作要求:
            - 以适合儿童的古代中国故事风格写作，融入五行等传统元素
            - 使用温暖、有趣的语言，让孩子们容易理解和喜爱
            - 只写纯粹的故事叙述(2-3句)，充满想象力和温馨感
            - 确保内容积极向上，适合儿童阅读""",
        
        Language.ENGLISH: f"""Write in a gentle, child-friendly style that captures the wonder and magic of ancient China. Use simple, beautiful language that children can understand and enjoy. Incorporate traditional elements like the five elements naturally into the story. Ensure your narrative advances the current story stage ({current_stage}) in a way that brings joy and teaches positive values.""",
        
        Language.BILINGUAL: f"""Format your response with the Chinese paragraph first, followed by its English translation. Write in a gentle, child-friendly style that captures the wonder and magic of ancient China. Use language that children can understand and enjoy in both languages."""
    }
    
    # Add object-specific instructions if this is an object appearance
    if action_type == "object_appearance":
        if lang == Language.CHINESE:
            base_instructions[Language.CHINESE] += """
            - 特别注意：让出现的汉代文物成为故事的魔法核心
            - 用儿童能理解的方式解释文物的特殊力量
            - 让物品帮助角色学习或成长"""
        elif lang == Language.ENGLISH:
            base_instructions[Language.ENGLISH] += """ When a Han dynasty artifact appears, make it magically significant in a child-appropriate way. Let the object teach lessons or help characters grow."""
        else:  # BILINGUAL
            base_instructions[Language.BILINGUAL] += """ Make any Han dynasty artifacts magically significant and educational for children in both language versions."""
    
    if lang == Language.CHINESE:
        return f"""
            {base_instructions[Language.CHINESE]}

            现在请继续故事:
                """
    elif lang == Language.ENGLISH:
        return f"\n\n{base_instructions[Language.ENGLISH]} Your style should evoke wonder, kindness, and the timeless wisdom of Chinese culture presented in an age-appropriate way."
    else:  # BILINGUAL
        return f"\n\n{base_instructions[Language.BILINGUAL]}\n\nVERY IMPORTANT: Your response MUST contain BOTH Chinese and English versions. First write in Chinese using child-friendly language, then provide the English translation that maintains the same gentle, wonder-filled tone."
