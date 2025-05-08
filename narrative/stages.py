"""Stage guidance for different narrative arcs."""

from utils.language import Language

# Dictionary of narrative guidance for each stage of each story arc
STAGE_GUIDANCE = {
    # Quest arc stage guidance
    "departure": {
        "en": "The protagonist leaves their familiar surroundings, possibly reluctantly or due to necessity.",
        "zh": "主角离开熟悉的环境，可能是不情愿的，或是出于必要。"
    },
    "challenge": {
        "en": "The protagonist faces obstacles that test their resolve and abilities.",
        "zh": "主角面临考验他们决心和能力的障碍。"
    },
    "revelation": {
        "en": "The protagonist discovers something that changes their understanding or gives them what they seek.",
        "zh": "主角发现改变他们理解的事物，或找到他们所寻求的东西。"
    },
    "return": {
        "en": "The protagonist begins the journey back, either physically or metaphorically.",
        "zh": "主角开始返回的旅程，无论是身体上还是象征性的。"
    },
    "transformation": {
        "en": "The protagonist is changed by their experiences, gaining wisdom or new abilities.",
        "zh": "主角因经历而改变，获得智慧或新能力。"
    },
    
    # Moral lesson arc stage guidance
    "harmony": {
        "en": "Present a state of balance and order that will soon be disrupted.",
        "zh": "呈现一种即将被打破的平衡与秩序状态。"
    },
    "transgression": {
        "en": "A character makes a moral error, often due to a character flaw.",
        "zh": "角色因性格缺陷犯下道德错误。"
    },
    "consequence": {
        "en": "The moral failing leads to negative outcomes, often affecting others.",
        "zh": "道德失误导致负面后果，通常影响他人。"
    },
    "realization": {
        "en": "The character recognizes their error and understands the moral principle.",
        "zh": "角色认识到错误并理解道德原则。"
    },
    "atonement": {
        "en": "The character corrects their behavior through self-cultivation and proper action.",
        "zh": "角色通过自我修养和正确行动纠正自己的行为。"
    },
    
    # Cosmic balance arc stage guidance
    "order": {
        "en": "Present the natural order of things before disruption.",
        "zh": "呈现被打破前的自然秩序。"
    },
    "disruption": {
        "en": "Cosmic balance is upset by some action or event.",
        "zh": "宇宙平衡被某些行动或事件打破。"
    },
    "chaos": {
        "en": "The imbalance creates widening ripples of disorder.",
        "zh": "失衡创造越来越大的混乱涟漪。"
    },
    "intervention": {
        "en": "Cosmic forces or their agents act to address the imbalance.",
        "zh": "宇宙力量或其代理人采取行动解决失衡。"
    },
    "new_order": {
        "en": "A new equilibrium is established, often different from the original.",
        "zh": "建立新的平衡，通常与原来不同。"
    },
    
    # Transformation arc stage guidance
    "ordinary": {
        "en": "Establish the protagonist's normal existence before transformation.",
        "zh": "确立主角变化前的普通生活。"
    },
    "encounter": {
        "en": "The protagonist encounters something extraordinary that catalyzes change.",
        "zh": "主角遇到催化变化的非凡事物。"
    },
    "change": {
        "en": "The transformation begins, often creating confusion or wonder.",
        "zh": "变化开始，常常引起困惑或惊奇。"
    },
    "challenge": {
        "en": "The transformation is tested or threatened in some way.",
        "zh": "变化以某种方式被考验或威胁。"
    },
    "transcendence": {
        "en": "The transformation is complete, elevating the protagonist to a new state of being.",
        "zh": "变化完成，将主角提升到新的存在状态。"
    },
    
    # Origin myth arc stage guidance
    "void": {
        "en": "Describe the world before the existence of the phenomenon to be explained.",
        "zh": "描述解释现象存在之前的世界。"
    },
    "creation": {
        "en": "Powerful forces or beings initiate the creation process.",
        "zh": "强大力量或存在启动创造过程。"
    },
    "conflict": {
        "en": "Opposing forces struggle, shaping the outcome of creation.",
        "zh": "对立力量斗争，塑造创造的结果。"
    },
    "resolution": {
        "en": "The conflict is resolved, establishing the phenomenon's form.",
        "zh": "冲突解决，确立现象的形式。"
    },
    "explanation": {
        "en": "Connect the mythic events to the present reality, explaining why things are as they are.",
        "zh": "将神话事件与现实联系，解释事物为何如此。"
    },
    
    # Ancestral vengeance arc stage guidance
    "injustice": {
        "en": "A grave wrong is committed against someone who dies unjustly.",
        "zh": "有人遭受严重不公而冤死。"
    },
    "suffering": {
        "en": "The living experience unexplained misfortune connected to the injustice.",
        "zh": "生者经历与冤情相关的不明灾祸。"
    },
    "divine_sign": {
        "en": "Supernatural signs reveal the connection between past injustice and current suffering.",
        "zh": "超自然迹象揭示过去冤情与当前苦难的联系。"
    },
    "retribution": {
        "en": "The spirit's vengeance is enacted, often through mortal instruments.",
        "zh": "亡灵的复仇得以实现，通常通过人间媒介。"
    },
    "ancestral_peace": {
        "en": "Justice restores balance and allows the spirit to rest.",
        "zh": "正义恢复平衡，亡灵得以安息。"
    },
    
    # Bureaucratic trial arc stage guidance
    "mortal_case": {
        "en": "An earthly conflict or transgression occurs that will be judged by higher powers.",
        "zh": "发生将受高等力量审判的人间冲突或过错。"
    },
    "underworld_appeal": {
        "en": "The case is brought to the attention of the underworld bureaucracy.",
        "zh": "案件被带到阴间官僚机构的注意中。"
    },
    "divine_judgment": {
        "en": "Supernatural forces pass judgment after reviewing evidence across realms.",
        "zh": "超自然力量在审查跨界证据后作出判决。"
    },
    "cosmic_record": {
        "en": "The judgment is recorded in the celestial ledgers, influencing karmic patterns.",
        "zh": "判决被记录在天书中，影响业力模式。"
    },
    "karmic_resolution": {
        "en": "The consequences of the judgment manifest in the mortal world as fate.",
        "zh": "判决的后果以命运形式在人间显现。"
    }
}

def get_stage_guidance(stage: str, language=Language.ENGLISH):
    """Get guidance for a specific narrative stage.
    
    Args:
        stage: The stage name to get guidance for.
        language: The language to return the guidance in.
        
    Returns:
        Guidance text for the specified stage in the requested language.
    """
    guidance = STAGE_GUIDANCE.get(stage, {})
    
    if language == Language.CHINESE:
        return guidance.get("zh", "")
    elif language == Language.ENGLISH:
        return guidance.get("en", "")
    else:  # BILINGUAL
        return {
            "zh": guidance.get("zh", ""),
            "en": guidance.get("en", "")
        }