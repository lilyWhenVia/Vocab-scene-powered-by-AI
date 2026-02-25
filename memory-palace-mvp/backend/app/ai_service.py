# -*- coding: utf-8 -*-
"""AI Service - Structured Data Generation"""
import json
import os
import re
import time
import math
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


BG_IMAGES = [
    {"url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1920&q=80", "title_zh": "晨光图书馆", "title_en": "Morning Library"},
    {"url": "https://images.unsplash.com/photo-1574068468668-a05a11f871da?w=1920&q=80", "title_zh": "自然博物馆", "title_en": "Natural Museum"},
    {"url": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=1920&q=80", "title_zh": "医学中心", "title_en": "Medical Center"},
    {"url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80", "title_zh": "现代办公室", "title_en": "Modern Office"},
    {"url": "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=1920&q=80", "title_zh": "城市公园", "title_en": "City Park"},
]

SCENE_PROMPT = """Generate a memory palace scene for vocabulary learning.

## Words (Total: {word_count}, ALL must appear)
{words}

## Output JSON (use [[word]] markers, NO HTML)
{{
    "title_zh": "场景中文标题",
    "title_en": "Scene English Title", 
    "paragraphs": [
        {{"zh": "中文段落用[[word]]标记", "en": "English with [[word]]", "zh_pure": "纯中文[[关键词]]"}}
    ]
}}

Rules: Use [[word]] markers. 5-7 paragraphs. ALL {word_count} words must appear. JSON only."""


PRICING = {"MiniMax-Text-01": {"input": 0.0001, "output": 0.0011}}
CONFIG_FILE = os.path.join(os.path.dirname(__file__), ".ai_config.json")


class AIConfig:
    def __init__(self):
        self.preferred_provider = os.getenv("AI_PROVIDER", "auto")
        self.enabled_providers = []
        self.temperature = 0.7
        self.api_keys = {"openai": os.getenv("OPENAI_API_KEY", ""), "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "zhipu": os.getenv("ZHIPU_API_KEY", ""), "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
            "qwen": os.getenv("DASHSCOPE_API_KEY", ""), "minimax": os.getenv("MINIMAX_API_KEY", "")}
        self._load_from_file()

    def _load_from_file(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.preferred_provider = data.get("preferred_provider", self.preferred_provider)
                    for k, v in data.get("api_keys", {}).items():
                        if k in self.api_keys and v: self.api_keys[k] = v
        except: pass

    def _save_to_file(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"preferred_provider": self.preferred_provider, "api_keys": self.api_keys}, f)
        except: pass

    def to_dict(self):
        return {"preferred_provider": self.preferred_provider, "api_keys_status": {k: bool(v) for k, v in self.api_keys.items()}}

    def update(self, data):
        if "preferred_provider" in data: self.preferred_provider = data["preferred_provider"]
        self._save_to_file()

    def update_api_key(self, provider, key):
        if provider in self.api_keys: self.api_keys[provider] = key; self._save_to_file(); return True
        return False


ai_config = AIConfig()


class AIService:
    def __init__(self, config):
        self.config = config
        self.minimax_client = None
        self.zhipu_client = None
        self.deepseek_client = None
        self.usage_history = []
        self._init_clients()

    def _init_clients(self):
        keys = self.config.api_keys
        if keys.get("minimax"): self.minimax_client = Anthropic(api_key=keys["minimax"], base_url="https://api.minimaxi.com/anthropic")
        if keys.get("zhipu"): self.zhipu_client = OpenAI(api_key=keys["zhipu"], base_url="https://open.bigmodel.cn/api/paas/v4/")
        if keys.get("deepseek"): self.deepseek_client = OpenAI(api_key=keys["deepseek"], base_url="https://api.deepseek.com/v1")

    def reinit_client(self, provider): self._init_clients()

    def get_available_providers(self):
        p = []
        if self.minimax_client: p.append("minimax")
        if self.zhipu_client: p.append("zhipu")
        if self.deepseek_client: p.append("deepseek")
        return p

    def _record_usage(self, provider, model, inp, out):
        pricing = PRICING.get(model, {"input": 0.001, "output": 0.002})
        cost = (inp * pricing["input"] + out * pricing["output"]) / 1000
        self.usage_history.append(TokenUsage(provider, model, inp, out, cost, time.time()))

    def get_usage_stats(self):
        return {"total_calls": len(self.usage_history), "total_cost": sum(u.cost for u in self.usage_history)}

    def generate_scene(self, words, provider="auto"):
        if provider == "auto":
            available = self.get_available_providers()
            if not available: raise ValueError("No API Key")
            provider = available[0]

        print(f"[AI] Words: {len(words)}, Provider: {provider}")

        word_dict = {w['word'].lower(): w for w in words}
        words_per_scene = 40
        num_scenes = min(5, math.ceil(len(words) / words_per_scene))

        scenes = []
        for i in range(num_scenes):
            scene_words = words[i*words_per_scene : min((i+1)*words_per_scene, len(words))]
            if not scene_words: continue

            bg = BG_IMAGES[i % len(BG_IMAGES)]
            print(f"[AI] Scene {i+1}/{num_scenes}, words: {len(scene_words)}")

            raw = self._generate_raw(scene_words, provider)
            if raw:
                scene = self._build_html(raw, scene_words, bg, i+1)
                scenes.append(scene)

        return {"scenes": scenes}

    def _generate_raw(self, scene_words, provider):
        words_text = "\n".join([f"- {w['word']}: {w.get('pos','')} {w.get('meaning','')}" for w in scene_words])
        prompt = SCENE_PROMPT.format(word_count=len(scene_words), words=words_text)
        print(f"[AI] Prompt: {len(prompt)} chars")

        try:
            if provider == "minimax" and self.minimax_client:
                return self._call_minimax(prompt)
            elif provider == "zhipu" and self.zhipu_client:
                return self._call_zhipu(prompt)
            elif provider == "deepseek" and self.deepseek_client:
                return self._call_deepseek(prompt)
        except Exception as e:
            print(f"[AI] Error: {e}")
        return None

    def _build_html(self, raw, scene_words, bg, scene_id):
        word_dict = {w['word'].lower(): w for w in scene_words}

        def replace_markers(text):
            def repl(m):
                word = m.group(1)
                info = word_dict.get(word.lower())
                if info:
                    tip = f"{info['word']}: {info.get('pos','')} {info.get('meaning','')}".strip()
                    return f"<span class='word-highlight'>{word}<span class='tooltip'>{tip}</span></span>"
                return f"<span class='word-highlight'>{word}</span>"
            return re.sub(r'\[\[([^\]]+)\]\]', repl, text or '')

        paragraphs = raw.get('paragraphs', [])
        zh_parts, en_parts, trans = [], [], []

        for p in paragraphs:
            zh_parts.append(f"<p class='mb-3'>{replace_markers(p.get('zh',''))}</p>")
            en_parts.append(f"<p class='mb-3'>{replace_markers(p.get('en',''))}</p>")
            trans.append(replace_markers(p.get('zh_pure','')))

        return {
            "id": scene_id, "icon": "fa-book", "bgImage": bg["url"],
            "zh": {"title": raw.get('title_zh', bg['title_zh']), "anchors": "入口中央角落",
                   "content": "".join(zh_parts), "translationParagraphs": trans},
            "en": {"title": raw.get('title_en', bg['title_en']), "anchors": "EntranceCentralCorner",
                   "content": "".join(en_parts)}
        }

    def _parse_json(self, content):
        start, end = content.find('{'), content.rfind('}')+1
        if start == -1 or end <= start: raise ValueError("No JSON")
        try: return json.loads(content[start:end])
        except: return json.loads(content[start:end].replace('\\"', "'"))

    def _call_minimax(self, prompt):
        model = "MiniMax-Text-01"
        resp = self.minimax_client.messages.create(model=model, max_tokens=4096,
            system="Generate JSON with [[word]] markers. Output JSON only.",
            messages=[{"role": "user", "content": prompt}])
        self._record_usage("minimax", model, resp.usage.input_tokens, resp.usage.output_tokens)
        print(f"[AI] MiniMax: {len(resp.content[0].text)} chars")
        return self._parse_json(resp.content[0].text)

    def _call_zhipu(self, prompt):
        model = "glm-4-flash"
        resp = self.zhipu_client.chat.completions.create(model=model, temperature=0.7,
            messages=[{"role": "system", "content": "JSON only"}, {"role": "user", "content": prompt}])
        self._record_usage("zhipu", model, resp.usage.prompt_tokens, resp.usage.completion_tokens)
        return self._parse_json(resp.choices[0].message.content)

    def _call_deepseek(self, prompt):
        model = "deepseek-chat"
        resp = self.deepseek_client.chat.completions.create(model=model, temperature=0.7,
            messages=[{"role": "system", "content": "JSON only"}, {"role": "user", "content": prompt}])
        self._record_usage("deepseek", model, resp.usage.prompt_tokens, resp.usage.completion_tokens)
        return self._parse_json(resp.choices[0].message.content)


ai_service = AIService(ai_config)
