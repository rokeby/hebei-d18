"""Stage guidance for different narrative arcs."""

from utils.language import Language

# Dictionary of narrative guidance for each stage of each story arc

STAGE_GUIDANCE = {
    # Friendship Journey arc stages
    "meeting": {
        "en": "Two characters meet for the first time in a beautiful setting like a blooming garden or festival.",
        "zh": "两个角色在美丽的环境中第一次相遇，比如盛开的花园或节日庆典。"
    },
    "misunderstanding": {
        "en": "A small confusion arises between the friends, perhaps due to different customs or shy feelings.",
        "zh": "朋友之间出现小小的误会，可能是因为不同的习俗或害羞的心情。"
    },
    "adventure": {
        "en": "The characters embark on a fun journey together, exploring markets, temples, or natural wonders.",
        "zh": "角色们一起踏上有趣的旅程，探索集市、庙宇或自然奇观。"
    },
    "understanding": {
        "en": "Through shared experiences, the friends learn about each other's hearts and become closer.",
        "zh": "通过共同的经历，朋友们了解彼此的心意，变得更加亲密。"
    },
    "celebration": {
        "en": "The friends celebrate their strong bond with a joyful festival or special meal together.",
        "zh": "朋友们用欢乐的节日或特别的聚餐来庆祝他们深厚的友谊。"
    },
    
    # Kind Deed Reward arc stages
    "daily_life": {
        "en": "Show the peaceful daily life of a child in ancient China, with family activities and simple pleasures.",
        "zh": "展现古代中国孩子的平静日常生活，有家庭活动和简单的快乐。"
    },
    "kind_action": {
        "en": "The child performs a small act of kindness, like helping an elder or caring for an animal.",
        "zh": "孩子做出小小的善举，比如帮助长者或照顾动物。"
    },
    "unexpected_result": {
        "en": "The kind deed leads to an unexpected positive outcome that surprises everyone.",
        "zh": "善举带来意想不到的积极结果，让每个人都感到惊喜。"
    },
    "magical_help": {
        "en": "Gentle spirits or magical creatures appear to reward the child's good heart.",
        "zh": "温和的精灵或神奇的生物出现，奖励孩子的善良之心。"
    },
    "happy_ending": {
        "en": "The story ends with everyone happy and the child learning about the joy of helping others.",
        "zh": "故事以皆大欢喜结束，孩子学会了帮助他人的快乐。"
    },
    
    # Festival Adventure arc stages
    "preparation": {
        "en": "Everyone in the village prepares excitedly for a traditional Chinese festival with decorations and food.",
        "zh": "村里的每个人都兴奋地为传统中国节日准备装饰和食物。"
    },
    "problem": {
        "en": "A small problem threatens the festival - perhaps missing ingredients or broken decorations.",
        "zh": "一个小问题威胁着节日——也许是缺少食材或装饰品损坏。"
    },
    "creative_solution": {
        "en": "Children use their creativity and cultural knowledge to find a clever solution.",
        "zh": "孩子们运用创造力和文化知识找到巧妙的解决方案。"
    },
    "community_help": {
        "en": "The whole community comes together to help, showing the strength of working as one.",
        "zh": "整个社区团结起来互相帮助，展现了团结一心的力量。"
    },
    "joyful_festival": {
        "en": "The festival is celebrated with great joy, featuring traditional music, dance, and delicious food.",
        "zh": "节日在极大的欢乐中庆祝，有传统音乐、舞蹈和美味食物。"
    },
    
    # Learning Wisdom arc stages
    "curiosity": {
        "en": "A child becomes curious about Chinese traditions, characters, or cultural practices.",
        "zh": "孩子对中国传统、文字或文化习俗产生好奇心。"
    },
    "seeking_teacher": {
        "en": "The child seeks out a wise teacher - perhaps a grandparent, scholar, or friendly spirit.",
        "zh": "孩子寻找智慧的老师——也许是祖父母、学者或友善的精灵。"
    },
    "funny_lessons": {
        "en": "The child learns through entertaining stories, games, or humorous situations.",
        "zh": "孩子通过有趣的故事、游戏或幽默的情况来学习。"
    },
    "practice": {
        "en": "The child practices what they've learned, perhaps through writing, crafts, or helping others.",
        "zh": "孩子练习他们学到的知识，也许通过写字、手工或帮助他人。"
    },
    "sharing_knowledge": {
        "en": "The child shares their new knowledge with friends and family, becoming a little teacher themselves.",
        "zh": "孩子与朋友和家人分享新知识，自己也成为小老师。"
    },
    
    # Nature Harmony arc stages
    "discovery": {
        "en": "A child discovers the beautiful relationship between seasons, animals, and plants in China.",
        "zh": "孩子发现了中国季节、动物和植物之间的美丽关系。"
    },
    "imbalance": {
        "en": "Something small disturbs the natural harmony - pollution, loneliness, or neglect.",
        "zh": "一些小事打扰了自然和谐——污染、孤独或忽视。"
    },
    "understanding": {
        "en": "The child learns about the importance of caring for nature and all living things.",
        "zh": "孩子了解到爱护自然和所有生物的重要性。"
    },
    "cooperation": {
        "en": "Children work together with nature spirits to restore balance through gentle actions.",
        "zh": "孩子们与自然精灵合作，通过温和的行动恢复平衡。"
    },
    "restoration": {
        "en": "Nature returns to harmony, and everyone celebrates the beauty of the natural world.",
        "zh": "自然恢复和谐，每个人都庆祝自然世界的美丽。"
    },
    
    # Brave Little Hero arc stages
    "ordinary_day": {
        "en": "A shy or cautious child goes about their normal day in ancient Chinese life.",
        "zh": "一个害羞或谨慎的孩子过着古代中国生活中平常的一天。"
    },
    "small_challenge": {
        "en": "A gentle challenge appears that requires the child to be a little bit brave.",
        "zh": "出现一个温和的挑战，需要孩子稍微勇敢一些。"
    },
    "finding_courage": {
        "en": "With encouragement from family or friends, the child discovers inner strength and courage.",
        "zh": "在家人或朋友的鼓励下，孩子发现了内在的力量和勇气。"
    },
    "clever_solution": {
        "en": "The child uses intelligence, kindness, or cultural wisdom to solve the problem creatively.",
        "zh": "孩子运用智慧、善良或文化智慧创造性地解决问题。"
    },
    "growing_up": {
        "en": "The child feels more confident and ready for life's adventures, having grown wiser.",
        "zh": "孩子感到更加自信，为人生的冒险做好准备，变得更加明智。"
    }
}

# STAGE_GUIDANCE = {
#     # Quest arc stage guidance
#     "departure": {
#         "en": "The protagonist leaves their familiar surroundings, possibly reluctantly or due to necessity.",
#         "zh": "主角离开熟悉的环境，可能是不情愿的，或是出于必要。"
#     },
#     "challenge": {
#         "en": "The protagonist faces obstacles that test their resolve and abilities.",
#         "zh": "主角面临考验他们决心和能力的障碍。"
#     },
#     "revelation": {
#         "en": "The protagonist discovers something that changes their understanding or gives them what they seek.",
#         "zh": "主角发现改变他们理解的事物，或找到他们所寻求的东西。"
#     },
#     "return": {
#         "en": "The protagonist begins the journey back, either physically or metaphorically.",
#         "zh": "主角开始返回的旅程，无论是身体上还是象征性的。"
#     },
#     "transformation": {
#         "en": "The protagonist is changed by their experiences, gaining wisdom or new abilities.",
#         "zh": "主角因经历而改变，获得智慧或新能力。"
#     },
    
#     # Moral lesson arc stage guidance
#     "harmony": {
#         "en": "Present a state of balance and order that will soon be disrupted.",
#         "zh": "呈现一种即将被打破的平衡与秩序状态。"
#     },
#     "transgression": {
#         "en": "A character makes a moral error, often due to a character flaw.",
#         "zh": "角色因性格缺陷犯下道德错误。"
#     },
#     "consequence": {
#         "en": "The moral failing leads to negative outcomes, often affecting others.",
#         "zh": "道德失误导致负面后果，通常影响他人。"
#     },
#     "realization": {
#         "en": "The character recognizes their error and understands the moral principle.",
#         "zh": "角色认识到错误并理解道德原则。"
#     },
#     "atonement": {
#         "en": "The character corrects their behavior through self-cultivation and proper action.",
#         "zh": "角色通过自我修养和正确行动纠正自己的行为。"
#     },
    
#     # Cosmic balance arc stage guidance
#     "order": {
#         "en": "Present the natural order of things before disruption.",
#         "zh": "呈现被打破前的自然秩序。"
#     },
#     "disruption": {
#         "en": "Cosmic balance is upset by some action or event.",
#         "zh": "宇宙平衡被某些行动或事件打破。"
#     },
#     "chaos": {
#         "en": "The imbalance creates widening ripples of disorder.",
#         "zh": "失衡创造越来越大的混乱涟漪。"
#     },
#     "intervention": {
#         "en": "Cosmic forces or their agents act to address the imbalance.",
#         "zh": "宇宙力量或其代理人采取行动解决失衡。"
#     },
#     "new_order": {
#         "en": "A new equilibrium is established, often different from the original.",
#         "zh": "建立新的平衡，通常与原来不同。"
#     },
    
#     # Transformation arc stage guidance
#     "ordinary": {
#         "en": "Establish the protagonist's normal existence before transformation.",
#         "zh": "确立主角变化前的普通生活。"
#     },
#     "encounter": {
#         "en": "The protagonist encounters something extraordinary that catalyzes change.",
#         "zh": "主角遇到催化变化的非凡事物。"
#     },
#     "change": {
#         "en": "The transformation begins, often creating confusion or wonder.",
#         "zh": "变化开始，常常引起困惑或惊奇。"
#     },
#     "challenge": {
#         "en": "The transformation is tested or threatened in some way.",
#         "zh": "变化以某种方式被考验或威胁。"
#     },
#     "transcendence": {
#         "en": "The transformation is complete, elevating the protagonist to a new state of being.",
#         "zh": "变化完成，将主角提升到新的存在状态。"
#     },
    
#     # Origin myth arc stage guidance
#     "void": {
#         "en": "Describe the world before the existence of the phenomenon to be explained.",
#         "zh": "描述解释现象存在之前的世界。"
#     },
#     "creation": {
#         "en": "Powerful forces or beings initiate the creation process.",
#         "zh": "强大力量或存在启动创造过程。"
#     },
#     "conflict": {
#         "en": "Opposing forces struggle, shaping the outcome of creation.",
#         "zh": "对立力量斗争，塑造创造的结果。"
#     },
#     "resolution": {
#         "en": "The conflict is resolved, establishing the phenomenon's form.",
#         "zh": "冲突解决，确立现象的形式。"
#     },
#     "explanation": {
#         "en": "Connect the mythic events to the present reality, explaining why things are as they are.",
#         "zh": "将神话事件与现实联系，解释事物为何如此。"
#     },
    
#     # Ancestral vengeance arc stage guidance
#     "injustice": {
#         "en": "A grave wrong is committed against someone who dies unjustly.",
#         "zh": "有人遭受严重不公而冤死。"
#     },
#     "suffering": {
#         "en": "The living experience unexplained misfortune connected to the injustice.",
#         "zh": "生者经历与冤情相关的不明灾祸。"
#     },
#     "divine_sign": {
#         "en": "Supernatural signs reveal the connection between past injustice and current suffering.",
#         "zh": "超自然迹象揭示过去冤情与当前苦难的联系。"
#     },
#     "retribution": {
#         "en": "The spirit's vengeance is enacted, often through mortal instruments.",
#         "zh": "亡灵的复仇得以实现，通常通过人间媒介。"
#     },
#     "ancestral_peace": {
#         "en": "Justice restores balance and allows the spirit to rest.",
#         "zh": "正义恢复平衡，亡灵得以安息。"
#     },
    
#     # Bureaucratic trial arc stage guidance
#     "mortal_case": {
#         "en": "An earthly conflict or transgression occurs that will be judged by higher powers.",
#         "zh": "发生将受高等力量审判的人间冲突或过错。"
#     },
#     "underworld_appeal": {
#         "en": "The case is brought to the attention of the underworld bureaucracy.",
#         "zh": "案件被带到阴间官僚机构的注意中。"
#     },
#     "divine_judgment": {
#         "en": "Supernatural forces pass judgment after reviewing evidence across realms.",
#         "zh": "超自然力量在审查跨界证据后作出判决。"
#     },
#     "cosmic_record": {
#         "en": "The judgment is recorded in the celestial ledgers, influencing karmic patterns.",
#         "zh": "判决被记录在天书中，影响业力模式。"
#     },
#     "karmic_resolution": {
#         "en": "The consequences of the judgment manifest in the mortal world as fate.",
#         "zh": "判决的后果以命运形式在人间显现。"
#     }
# }

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