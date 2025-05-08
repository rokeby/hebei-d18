"""Theme and motif management for Han dynasty folktales."""

from typing import List, Dict

from utils.language import Language

# Motif translations from English to Chinese
MOTIF_TRANSLATIONS = {
    # Common quest motifs
    "jade talisman": "玉符",
    "guardian spirit": "守护神灵",
    "celestial guidance": "天界指引",
    "divine test": "神圣考验",
    
    # Common moral lesson motifs
    "filial piety": "孝道",
    "social hierarchy": "社会等级",
    "ritual propriety": "礼仪规范",
    "moral cultivation": "道德修养",
    
    # Common cosmic balance motifs
    "five elements": "五行",
    "yin-yang imbalance": "阴阳失衡",
    "celestial omens": "天象征兆",
    "natural disasters": "自然灾害",
    
    # Common transformation motifs
    "jade artifacts": "玉器",
    "immortal peaches": "仙桃",
    "animal spirits": "动物精灵",
    "cinnabar elixir": "丹药",
    
    # Common origin myth motifs
    "primordial chaos": "混沌",
    "divine siblings": "神兄妹",
    "cosmic eggs": "宇宙卵",
    "celestial separation": "天地分离",
    
    # Common ancestral vengeance motifs
    "vengeful ghost": "复仇鬼魂",
    "dream warning": "梦中警示",
    "ancestral tablet": "祖先牌位",
    "blood oath": "血誓",
    
    # Common bureaucratic trial motifs
    "ledger of life and death": "生死簿",
    "underworld court": "阴间法庭",
    "Judge Bao": "包青天",
    "karmic retribution": "因果报应",
    
    # Other common motifs
    "divine text": "神圣经文",
    "celestial herb": "天界灵草",
    "magical artifact": "法宝",
    "lost knowledge": "失落知识",
    "unusual weather": "异常天气",
    "astronomical event": "天文现象",
    "animal behavior": "动物异常行为",
    "plant anomaly": "植物异象",
    "human to animal": "人变动物",
    "mortal to immortal": "凡人成仙",
    "living to spirit": "生者化灵",
    "animal to human": "动物成人",
    "inner cultivation": "内修",
    "cosmic alignment": "天体对齐",
    "memories": "记忆",
    "human connection": "人间联系",
    "physical form": "肉身",
    "mortal desires": "凡人欲望",
    "natural feature": "自然景观",
    "animal trait": "动物特性",
    "human custom": "人类习俗",
    "celestial event": "天象",
    "seasonal change": "季节变化",
    "creator deity": "创世神",
    "culture hero": "人文始祖",
    "first ancestor": "始祖",
    "elemental force": "元素力量",
    "cosmic animal": "宇宙神兽",
    "water": "水",
    "fire": "火",
    "wood": "木",
    "earth": "土",
    "metal": "金",
    "void": "虚空",
    "murder": "谋杀",
    "false accusation": "冤枉",
    "betrayal": "背叛",
    "stolen identity": "身份被盗",
    "broken oath": "违背誓言",
    "dreams": "梦境",
    "illness": "疾病",
    "possession": "附身",
    "apparition": "鬼影",
    "animal messenger": "动物使者",
    "ritual specialist": "法事专家",
    "descendant": "后人",
    "official": "官员",
    "innocent bystander": "无辜旁观者",
    "corruption": "腐败",
    "ritual impropriety": "礼仪不当",
    "moral failing": "道德失败",
    "cosmic disruption": "宇宙混乱",
    "accidental transgression": "意外过错",
    "Judge of the Dead": "阎罗王",
    "City God": "城隍爷",
    "Celestial Emperor": "玉皇大帝",
    "Karma Official": "司命神",
    "Moon Goddess": "嫦娥",
    "soul records": "魂魄记录",
    "magic mirror": "照妖镜",
    "otherworld witness": "幽冥证人",
    "karmic ledger": "因果账簿",
    "spirit testimony": "灵魂证词"
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