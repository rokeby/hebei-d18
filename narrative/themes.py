"""Theme and motif management for Han dynasty folktales."""

from typing import List, Dict

from utils.language import Language

# Motif translations from English to Chinese
# MOTIF_TRANSLATIONS = {
#     # Common quest motifs
#     "jade talisman": "玉符",
#     "guardian spirit": "守护神灵",
#     "celestial guidance": "天界指引",
#     "divine test": "神圣考验",
    
#     # Common moral lesson motifs
#     "filial piety": "孝道",
#     "social hierarchy": "社会等级",
#     "ritual propriety": "礼仪规范",
#     "moral cultivation": "道德修养",
    
#     # Common cosmic balance motifs
#     "five elements": "五行",
#     "yin-yang imbalance": "阴阳失衡",
#     "celestial omens": "天象征兆",
#     "natural disasters": "自然灾害",
    
#     # Common transformation motifs
#     "jade artifacts": "玉器",
#     "immortal peaches": "仙桃",
#     "animal spirits": "动物精灵",
#     "cinnabar elixir": "丹药",
    
#     # Common origin myth motifs
#     "primordial chaos": "混沌",
#     "divine siblings": "神兄妹",
#     "cosmic eggs": "宇宙卵",
#     "celestial separation": "天地分离",
    
#     # Common ancestral vengeance motifs
#     "vengeful ghost": "复仇鬼魂",
#     "dream warning": "梦中警示",
#     "ancestral tablet": "祖先牌位",
#     "blood oath": "血誓",
    
#     # Common bureaucratic trial motifs
#     "ledger of life and death": "生死簿",
#     "underworld court": "阴间法庭",
#     "Judge Bao": "包青天",
#     "karmic retribution": "因果报应",
    
#     # Other common motifs
#     "divine text": "神圣经文",
#     "celestial herb": "天界灵草",
#     "magical artifact": "法宝",
#     "lost knowledge": "失落知识",
#     "unusual weather": "异常天气",
#     "astronomical event": "天文现象",
#     "animal behavior": "动物异常行为",
#     "plant anomaly": "植物异象",
#     "human to animal": "人变动物",
#     "mortal to immortal": "凡人成仙",
#     "living to spirit": "生者化灵",
#     "animal to human": "动物成人",
#     "inner cultivation": "内修",
#     "cosmic alignment": "天体对齐",
#     "memories": "记忆",
#     "human connection": "人间联系",
#     "physical form": "肉身",
#     "mortal desires": "凡人欲望",
#     "natural feature": "自然景观",
#     "animal trait": "动物特性",
#     "human custom": "人类习俗",
#     "celestial event": "天象",
#     "seasonal change": "季节变化",
#     "creator deity": "创世神",
#     "culture hero": "人文始祖",
#     "first ancestor": "始祖",
#     "elemental force": "元素力量",
#     "cosmic animal": "宇宙神兽",
#     "water": "水",
#     "fire": "火",
#     "wood": "木",
#     "earth": "土",
#     "metal": "金",
#     "void": "虚空",
#     "murder": "谋杀",
#     "false accusation": "冤枉",
#     "betrayal": "背叛",
#     "stolen identity": "身份被盗",
#     "broken oath": "违背誓言",
#     "dreams": "梦境",
#     "illness": "疾病",
#     "possession": "附身",
#     "apparition": "鬼影",
#     "animal messenger": "动物使者",
#     "ritual specialist": "法事专家",
#     "descendant": "后人",
#     "official": "官员",
#     "innocent bystander": "无辜旁观者",
#     "corruption": "腐败",
#     "ritual impropriety": "礼仪不当",
#     "moral failing": "道德失败",
#     "cosmic disruption": "宇宙混乱",
#     "accidental transgression": "意外过错",
#     "Judge of the Dead": "阎罗王",
#     "City God": "城隍爷",
#     "Celestial Emperor": "玉皇大帝",
#     "Karma Official": "司命神",
#     "Moon Goddess": "嫦娥",
#     "soul records": "魂魄记录",
#     "magic mirror": "照妖镜",
#     "otherworld witness": "幽冥证人",
#     "karmic ledger": "因果账簿",
#     "spirit testimony": "灵魂证词"
# }


MOTIF_TRANSLATIONS = {
    # Friendship journey motifs
    "magical animal friend": "神奇动物朋友",
    "helping others": "帮助他人",
    "teamwork": "团队合作",
    "festival celebration": "节日庆祝",
    
    # Kind deed reward motifs
    "talking animals": "会说话的动物",
    "magical objects": "神奇物品",
    "helping elders": "帮助长者",
    "nature spirits": "自然精灵",
    
    # Festival adventure motifs
    "lantern festival": "灯笼节",
    "dragon dance": "舞龙",
    "moon cakes": "月饼",
    "spring festival": "春节",
    
    # Learning wisdom motifs
    "wise panda": "智慧熊猫",
    "magic paintbrush": "神奇画笔",
    "flying kite": "飞翔的风筝",
    "ancient library": "古老图书馆",
    
    # Nature harmony motifs
    "guardian animals": "守护动物",
    "seasonal changes": "季节变化",
    "magical plants": "神奇植物",
    "rainbow bridge": "彩虹桥",
    
    # Brave little hero motifs
    "helpful dragon": "善良的龙",
    "magic jade pendant": "神奇玉佩",
    "wise grandfather": "智慧的爷爷",
    "bamboo forest": "竹林",
    
    # Additional child-friendly motifs
    "friendly spirits": "友善的精灵",
    "singing birds": "歌唱的鸟儿",
    "glowing fireflies": "发光的萤火虫",
    "dancing butterflies": "舞蹈的蝴蝶",
    "wise tortoise": "智慧的乌龟",
    "playful monkeys": "顽皮的猴子",
    "gentle wind": "温柔的风",
    "smiling sun": "微笑的太阳",
    "kind moon": "慈祥的月亮",
    "sparkling stars": "闪烁的星星",
    
    # Festival and celebration motifs
    "red lanterns": "红灯笼",
    "golden dragons": "金龙",
    "paper flowers": "纸花",
    "silk ribbons": "丝带",
    "temple bells": "寺庙钟声",
    "incense sticks": "香棒",
    "lucky coins": "幸运硬币",
    "fortune cookies": "幸运饼干",
    
    # Learning and wisdom motifs
    "ancient scrolls": "古老卷轴",
    "wise sayings": "智慧格言",
    "calligraphy brush": "毛笔",
    "ink stone": "砚台",
    "bamboo books": "竹简",
    "poetry verses": "诗句",
    "storytelling circle": "讲故事的圈子",
    "memory games": "记忆游戏",
    
    # Nature and garden motifs
    "blooming flowers": "盛开的花朵",
    "flowing streams": "流动的小溪",
    "whispering trees": "低语的树木",
    "singing rivers": "歌唱的河流",
    "dancing leaves": "舞动的叶子",
    "peaceful gardens": "宁静的花园",
    "mountain paths": "山间小径",
    "forest clearings": "森林空地",
    
    # Family and community motifs
    "loving family": "慈爱的家庭",
    "village elders": "村里的长者",
    "children's laughter": "孩子们的笑声",
    "shared meals": "共同的餐食",
    "helping neighbors": "帮助邻居",
    "community garden": "社区花园",
    "village square": "村庄广场",
    "market day": "集市日",
    
    # Magical helper motifs
    "fairy godmother": "仙女教母",
    "guardian angel": "守护天使",
    "talking fish": "会说话的鱼",
    "magic seeds": "神奇种子",
    "enchanted mirrors": "魔法镜子",
    "singing crystals": "歌唱的水晶",
    "dancing shadows": "舞蹈的影子",
    "helpful clouds": "有用的云朵",
    
    # Adventure and exploration motifs
    "hidden treasures": "隐藏的宝藏",
    "secret passages": "秘密通道",
    "magical doorways": "神奇的门",
    "flying carpets": "飞毯",
    "sailing boats": "帆船",
    "mountain climbing": "爬山",
    "river crossing": "过河",
    "bridge building": "建桥",
    
    # Traditional Chinese elements (child-friendly)
    "paper lanterns": "纸灯笼",
    "silk fans": "丝绸扇子",
    "jade ornaments": "玉饰品",
    "tea ceremonies": "茶道仪式",
    "chopstick games": "筷子游戏",
    "origami animals": "折纸动物",
    "shadow puppets": "皮影戏",
    "lion masks": "狮子面具",
    
    # Virtues and values motifs
    "kindness": "善良",
    "courage": "勇气",
    "honesty": "诚实",
    "patience": "耐心",
    "respect": "尊重",
    "sharing": "分享",
    "forgiveness": "宽恕",
    "gratitude": "感恩",
    "friendship": "友谊",
    "love": "爱",
    
    # Problem-solving motifs
    "clever solutions": "聪明的解决方案",
    "creative thinking": "创造性思维",
    "working together": "一起工作",
    "asking for help": "寻求帮助",
    "trying again": "再次尝试",
    "learning from mistakes": "从错误中学习",
    "practice makes perfect": "熟能生巧",
    "never giving up": "永不放弃"
}

def get_motifs_text(motifs: List[str], language=Language.ENGLISH) -> str:
    """Format story motifs for inclusion in prompts.
    
    Args:
        motifs: List of motif strings.
        language: The language to format the motifs in.
        
    Returns:
        A formatted string of motifs in the requested language.
    """
    if not motifs:
        return ""
        
    if language == Language.CHINESE:
        translated_motifs = [MOTIF_TRANSLATIONS.get(motif, motif) for motif in motifs]
        return f"故事主题: {', '.join(translated_motifs)}"
    elif language == Language.ENGLISH:
        return f"Story motifs: {', '.join(motifs)}"
    else:  # BILINGUAL
        bilingual_motifs = []
        for motif in motifs:
            translation = MOTIF_TRANSLATIONS.get(motif, motif)
            bilingual_motifs.append(f"{motif} ({translation})")
            
        return f"Story motifs / 故事主题: {', '.join(bilingual_motifs)}"