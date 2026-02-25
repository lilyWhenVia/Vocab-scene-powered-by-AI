# -*- coding: utf-8 -*-
"""AI Service - Memory Palace with 50 Predefined Scenes"""
import json, os, re, time, math
from typing import Optional
from dataclasses import dataclass
from openai import OpenAI
from anthropic import Anthropic

@dataclass
class TokenUsage:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    timestamp: float

# 50 Predefined Scenes - scene_id maps to image
SCENES = {
    1: {"title_zh": "晨光图书馆", "title_en": "Morning Library", "url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1920&q=80", "kw": ["book","read","study","library"]},
    2: {"title_zh": "大学礼堂", "title_en": "University Hall", "url": "https://images.unsplash.com/photo-1562774053-701939374585?w=1920&q=80", "kw": ["education","student","academic"]},
    3: {"title_zh": "科学实验室", "title_en": "Science Lab", "url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1920&q=80", "kw": ["science","experiment","research","genetic"]},
    4: {"title_zh": "艺术工作室", "title_en": "Art Studio", "url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1920&q=80", "kw": ["art","paint","creative","design"]},
    5: {"title_zh": "音乐教室", "title_en": "Music Room", "url": "https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=1920&q=80", "kw": ["music","song","instrument"]},
    6: {"title_zh": "现代办公室", "title_en": "Modern Office", "url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80", "kw": ["work","office","business","career"]},
    7: {"title_zh": "会议室", "title_en": "Conference Room", "url": "https://images.unsplash.com/photo-1431540015161-0bf868a2d407?w=1920&q=80", "kw": ["meeting","discuss","negotiate"]},
    8: {"title_zh": "证券交易所", "title_en": "Stock Exchange", "url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1920&q=80", "kw": ["invest","stock","market","trade","finance"]},
    9: {"title_zh": "创业车库", "title_en": "Startup Garage", "url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1920&q=80", "kw": ["startup","innovation","entrepreneur"]},
    10: {"title_zh": "法庭", "title_en": "Law Court", "url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1920&q=80", "kw": ["law","legal","court","judge","justice"]},
    11: {"title_zh": "医院大厅", "title_en": "Hospital Lobby", "url": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=1920&q=80", "kw": ["hospital","health","medical","doctor"]},
    12: {"title_zh": "药房", "title_en": "Pharmacy", "url": "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=1920&q=80", "kw": ["medicine","drug","pharmacy"]},
    13: {"title_zh": "健身房", "title_en": "Fitness Gym", "url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1920&q=80", "kw": ["exercise","fitness","muscle","workout"]},
    14: {"title_zh": "城市公园", "title_en": "City Park", "url": "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=1920&q=80", "kw": ["park","nature","tree","outdoor"]},
    15: {"title_zh": "海滩", "title_en": "Beach", "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1920&q=80", "kw": ["beach","ocean","sea","wave","vacation"]},
    16: {"title_zh": "山顶", "title_en": "Mountain Peak", "url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1920&q=80", "kw": ["mountain","climb","peak","adventure"]},
    17: {"title_zh": "森林小径", "title_en": "Forest Trail", "url": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=1920&q=80", "kw": ["forest","tree","trail","wildlife"]},
    18: {"title_zh": "植物园", "title_en": "Botanical Garden", "url": "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1920&q=80", "kw": ["plant","flower","garden","botanical"]},
    19: {"title_zh": "机场航站楼", "title_en": "Airport Terminal", "url": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1920&q=80", "kw": ["airport","flight","travel","journey"]},
    20: {"title_zh": "火车站", "title_en": "Train Station", "url": "https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=1920&q=80", "kw": ["train","station","railway","commute"]},
    21: {"title_zh": "游轮甲板", "title_en": "Cruise Ship", "url": "https://images.unsplash.com/photo-1548574505-5e239809ee19?w=1920&q=80", "kw": ["cruise","ship","voyage","sail"]},
    22: {"title_zh": "温馨咖啡馆", "title_en": "Cozy Cafe", "url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1920&q=80", "kw": ["coffee","cafe","drink","chat","social"]},
    23: {"title_zh": "高级餐厅", "title_en": "Fine Restaurant", "url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1920&q=80", "kw": ["restaurant","dinner","meal","cuisine"]},
    24: {"title_zh": "农贸市场", "title_en": "Farmers Market", "url": "https://images.unsplash.com/photo-1488459716781-31db52582fe9?w=1920&q=80", "kw": ["market","buy","sell","fresh","trade"]},
    25: {"title_zh": "面包房", "title_en": "Bakery", "url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=1920&q=80", "kw": ["bread","bake","pastry","flour"]},
    26: {"title_zh": "自然博物馆", "title_en": "Natural Museum", "url": "https://images.unsplash.com/photo-1574068468668-a05a11f871da?w=1920&q=80", "kw": ["museum","history","exhibit","ancient"]},
    27: {"title_zh": "剧院", "title_en": "Theater", "url": "https://images.unsplash.com/photo-1503095396549-807759245b35?w=1920&q=80", "kw": ["theater","drama","performance","stage"]},
    28: {"title_zh": "电影院", "title_en": "Cinema", "url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1920&q=80", "kw": ["movie","film","cinema","screen"]},
    29: {"title_zh": "游乐园", "title_en": "Amusement Park", "url": "https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?w=1920&q=80", "kw": ["fun","play","ride","entertainment"]},
    30: {"title_zh": "体育场", "title_en": "Sports Stadium", "url": "https://images.unsplash.com/photo-1459865264687-595d652de67e?w=1920&q=80", "kw": ["sport","game","team","compete","match"]},
    31: {"title_zh": "科技中心", "title_en": "Tech Hub", "url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=80", "kw": ["technology","computer","digital","software"]},
    32: {"title_zh": "服务器机房", "title_en": "Server Room", "url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1920&q=80", "kw": ["server","data","network","internet"]},
    33: {"title_zh": "机器人实验室", "title_en": "Robotics Lab", "url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1920&q=80", "kw": ["robot","AI","machine","automation"]},
    34: {"title_zh": "温馨客厅", "title_en": "Living Room", "url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1920&q=80", "kw": ["home","family","living","comfort"]},
    35: {"title_zh": "厨房", "title_en": "Kitchen", "url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1920&q=80", "kw": ["cook","kitchen","food","recipe"]},
    36: {"title_zh": "卧室", "title_en": "Bedroom", "url": "https://images.unsplash.com/photo-1540518614846-7eded433c457?w=1920&q=80", "kw": ["sleep","rest","dream","bed","night"]},
    37: {"title_zh": "私家花园", "title_en": "Private Garden", "url": "https://images.unsplash.com/photo-1558293842-c0fd3db86157?w=1920&q=80", "kw": ["garden","flower","plant","grow"]},
    38: {"title_zh": "城市街道", "title_en": "City Street", "url": "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=1920&q=80", "kw": ["city","street","urban","traffic"]},
    39: {"title_zh": "购物中心", "title_en": "Shopping Mall", "url": "https://images.unsplash.com/photo-1519567241046-7f570eee3ce6?w=1920&q=80", "kw": ["shop","buy","store","fashion"]},
    40: {"title_zh": "银行大厅", "title_en": "Bank Hall", "url": "https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=1920&q=80", "kw": ["bank","money","account","deposit","loan"]},
    41: {"title_zh": "警察局", "title_en": "Police Station", "url": "https://images.unsplash.com/photo-1453873531674-2151bcd01707?w=1920&q=80", "kw": ["police","crime","security","protect"]},
    42: {"title_zh": "消防站", "title_en": "Fire Station", "url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1920&q=80", "kw": ["fire","emergency","rescue","brave"]},
    43: {"title_zh": "空间站", "title_en": "Space Station", "url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1920&q=80", "kw": ["space","astronaut","universe","planet"]},
    44: {"title_zh": "海底世界", "title_en": "Underwater World", "url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1920&q=80", "kw": ["ocean","fish","dive","marine","coral"]},
    45: {"title_zh": "古老寺庙", "title_en": "Ancient Temple", "url": "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=1920&q=80", "kw": ["temple","ancient","spiritual","tradition"]},
    46: {"title_zh": "中世纪城堡", "title_en": "Medieval Castle", "url": "https://images.unsplash.com/photo-1533154683836-84ea7a0bc310?w=1920&q=80", "kw": ["castle","medieval","knight","kingdom"]},
    47: {"title_zh": "沙漠绿洲", "title_en": "Desert Oasis", "url": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=1920&q=80", "kw": ["desert","oasis","sand","hot","survive"]},
    48: {"title_zh": "北极冰原", "title_en": "Arctic Ice", "url": "https://images.unsplash.com/photo-1517783999520-f068d7431a60?w=1920&q=80", "kw": ["arctic","ice","cold","polar","snow"]},
    49: {"title_zh": "热带雨林", "title_en": "Rainforest", "url": "https://images.unsplash.com/photo-1440342359743-84fcb8c21f21?w=1920&q=80", "kw": ["rainforest","tropical","jungle","wildlife"]},
    50: {"title_zh": "火山口", "title_en": "Volcano", "url": "https://images.unsplash.com/photo-1462332420958-a05d1e002413?w=1920&q=80", "kw": ["volcano","lava","eruption","power"]},
}

SCENE_LIST = "\n".join([f"{k}. {v['title_en']} - {','.join(v['kw'])}" for k,v in SCENES.items()])

PROMPT = """You are a Memory Palace expert. Create scenes for vocabulary learning.

## TASK
1. Analyze {word_count} words
2. Select 1-5 scenes from list (by scene_id 1-50)
3. Distribute ALL words to scenes
4. Generate story paragraphs

## SCENES (select by ID)
{scene_list}

## WORDS ({word_count} total, ALL must be used)
{words}

## OUTPUT JSON
{{"scenes": [{{"scene_id": 1, "words_in_scene": ["word1","word2"], "paragraphs": [{{"zh": "中文[[word]]", "en": "English [[word]]", "zh_pure": "翻译[[词]]"}}]}}]}}

RULES: scene_id must be 1-50. No duplicate scenes. ALL words must appear. Use [[word]] markers. 3-5 paragraphs per scene. Max 5 scenes. JSON only."""

PRICING = {"MiniMax-Text-01": {"input": 0.0001, "output": 0.0011}}
CONFIG_FILE = os.path.join(os.path.dirname(__file__), ".ai_config.json")

class AIConfig:
    def __init__(self):
        self.preferred_provider = os.getenv("AI_PROVIDER", "auto")
        self.api_keys = {"minimax": os.getenv("MINIMAX_API_KEY", ""), "zhipu": os.getenv("ZHIPU_API_KEY", ""), "deepseek": os.getenv("DEEPSEEK_API_KEY", "")}
        self._load()
    def _load(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE) as f:
                    d = json.load(f)
                    self.preferred_provider = d.get("preferred_provider", self.preferred_provider)
                    for k,v in d.get("api_keys",{}).items():
                        if k in self.api_keys and v: self.api_keys[k] = v
        except: pass
    def _save(self):
        try:
            with open(CONFIG_FILE,'w') as f: json.dump({"preferred_provider": self.preferred_provider, "api_keys": self.api_keys}, f)
        except: pass
    def to_dict(self): return {"preferred_provider": self.preferred_provider, "api_keys_status": {k: bool(v) for k,v in self.api_keys.items()}}
    def update(self, d):
        if "preferred_provider" in d: self.preferred_provider = d["preferred_provider"]
        self._save()
    def update_api_key(self, p, k):
        if p in self.api_keys: self.api_keys[p] = k; self._save(); return True
        return False

ai_config = AIConfig()

class AIService:
    def __init__(self, cfg):
        self.cfg = cfg
        self.minimax = self.zhipu = self.deepseek = None
        self.usage = []
        self._init()
    def _init(self):
        k = self.cfg.api_keys
        if k.get("minimax"): self.minimax = Anthropic(api_key=k["minimax"], base_url="https://api.minimaxi.com/anthropic")
        if k.get("zhipu"): self.zhipu = OpenAI(api_key=k["zhipu"], base_url="https://open.bigmodel.cn/api/paas/v4/")
        if k.get("deepseek"): self.deepseek = OpenAI(api_key=k["deepseek"], base_url="https://api.deepseek.com/v1")
    def reinit_client(self, p): self._init()
    def get_available_providers(self):
        r = []
        if self.minimax: r.append("minimax")
        if self.zhipu: r.append("zhipu")
        if self.deepseek: r.append("deepseek")
        return r
    def _record(self, p, m, i, o):
        pr = PRICING.get(m, {"input":0.001,"output":0.002})
        self.usage.append(TokenUsage(p, m, i, o, (i*pr["input"]+o*pr["output"])/1000, time.time()))
    def get_usage_stats(self): return {"calls": len(self.usage), "cost": sum(u.cost for u in self.usage)}

    def generate_scene(self, words, provider="auto"):
        if provider == "auto":
            avail = self.get_available_providers()
            if not avail: raise ValueError("No API Key")
            provider = avail[0]
        print(f"[AI] Words: {len(words)}, Provider: {provider}")
        
        wd = {w['word'].lower(): w for w in words}
        wt = "\n".join([f"- {w['word']}: {w.get('pos','')} {w.get('meaning','')}" for w in words])
        prompt = PROMPT.format(word_count=len(words), scene_list=SCENE_LIST, words=wt)
        print(f"[AI] Prompt: {len(prompt)} chars")
        
        raw = self._call(prompt, provider)
        if not raw: raise ValueError("AI failed")
        
        scenes = self._build(raw, wd)
        print(f"[AI] Scenes: {len(scenes)}, Words: {sum(len(s.get('words_used',[])) for s in scenes)}/{len(words)}")
        return {"scenes": scenes}

    def _build(self, raw, wd):
        result = []
        for i, rs in enumerate(raw.get('scenes', [])):
            sid = rs.get('scene_id', 1)
            info = SCENES.get(sid, SCENES[1])
            ws = rs.get('words_in_scene', [])
            zh, en, tr = [], [], []
            for p in rs.get('paragraphs', []):
                zh.append(f"<p class='mb-3'>{self._mark(p.get('zh',''), wd)}</p>")
                en.append(f"<p class='mb-3'>{self._mark(p.get('en',''), wd)}</p>")
                tr.append(self._mark(p.get('zh_pure',''), wd))
            result.append({
                "id": i+1, "scene_id": sid, "icon": "fa-book", "bgImage": info["url"], "words_used": ws,
                "zh": {"title": info["title_zh"], "anchors": "入口中央角落", "content": "".join(zh), "translationParagraphs": tr},
                "en": {"title": info["title_en"], "anchors": "EntranceCentralCorner", "content": "".join(en)}
            })
            print(f"[AI] Scene {i+1}: {info['title_en']} (id={sid}), words: {len(ws)}")
        return result

    def _mark(self, t, wd):
        def r(m):
            w = m.group(1)
            info = wd.get(w.lower())
            if info:
                tip = f"{info['word']}: {info.get('pos','')} {info.get('meaning','')}".strip()
                return f"<span class='word-highlight'>{w}<span class='tooltip'>{tip}</span></span>"
            return f"<span class='word-highlight'>{w}</span>"
        return re.sub(r'\[\[([^\]]+)\]\]', r, t or '')

    def _call(self, prompt, provider):
        try:
            if provider == "minimax" and self.minimax: return self._minimax(prompt)
            if provider == "zhipu" and self.zhipu: return self._zhipu(prompt)
            if provider == "deepseek" and self.deepseek: return self._deepseek(prompt)
        except Exception as e:
            print(f"[AI] Error: {e}")
            import traceback; traceback.print_exc()
        return None

    def _json(self, c):
        s, e = c.find('{'), c.rfind('}')+1
        if s == -1 or e <= s: raise ValueError("No JSON")
        try: return json.loads(c[s:e])
        except: return json.loads(c[s:e].replace('\\"', "'"))

    def _minimax(self, p):
        m = "MiniMax-Text-01"
        r = self.minimax.messages.create(model=m, max_tokens=8192, system="Memory Palace expert. Output JSON only.", messages=[{"role":"user","content":p}])
        self._record("minimax", m, r.usage.input_tokens, r.usage.output_tokens)
        print(f"[AI] MiniMax: {len(r.content[0].text)} chars")
        return self._json(r.content[0].text)

    def _zhipu(self, p):
        m = "glm-4-flash"
        r = self.zhipu.chat.completions.create(model=m, temperature=0.7, messages=[{"role":"system","content":"JSON only"},{"role":"user","content":p}])
        self._record("zhipu", m, r.usage.prompt_tokens, r.usage.completion_tokens)
        return self._json(r.choices[0].message.content)

    def _deepseek(self, p):
        m = "deepseek-chat"
        r = self.deepseek.chat.completions.create(model=m, temperature=0.7, messages=[{"role":"system","content":"JSON only"},{"role":"user","content":p}])
        self._record("deepseek", m, r.usage.prompt_tokens, r.usage.completion_tokens)
        return self._json(r.choices[0].message.content)

ai_service = AIService(ai_config)
