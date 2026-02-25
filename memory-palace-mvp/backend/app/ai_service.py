# -*- coding: utf-8 -*-
"""AI Service - Memory Palace Scene Generator"""
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
    {"theme": "library", "url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1920&q=80", "title_zh": "Morning Library", "title_en": "Morning Library"},
    {"theme": "museum", "url": "https://images.unsplash.com/photo-1574068468668-a05a11f871da?w=1920&q=80", "title_zh": "Natural Museum", "title_en": "Natural History Museum"},
    {"theme": "hospital", "url": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=1920&q=80", "title_zh": "Medical Center", "title_en": "Medical Center"},
    {"theme": "office", "url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80", "title_zh": "Modern Office", "title_en": "Modern Office"},
    {"theme": "park", "url": "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=1920&q=80", "title_zh": "City Park", "title_en": "City Park"},
]

SCENE_PROMPT = """You are a Memory Palace scene generator. Generate an immersive scene for vocabulary learning.

## Scene Info
- Scene ID: {scene_id}
- Theme: {scene_title_zh} ({scene_title_en})
- Background: {bg_image}
- Anchors: {anchors}

## Words to include (Total: {word_count}, ALL must appear!)
{words}

## CRITICAL: Word Highlight Format
CORRECT: <span class='word-highlight'>library<span class='tooltip'>library: n. library</span></span>
WRONG: librarylibrary: n. xxx OR library: n. xxx (exposed)

## JSON Output
{{
    "id": {scene_id},
    "icon": "fa-book",
    "bgImage": "{bg_image}",
    "zh": {{"title": "{scene_title_zh}", "anchors": "{anchors}", "content": "<p class='mb-3'>...</p>", "translationParagraphs": ["..."]}},
    "en": {{"title": "{scene_title_en}", "anchors": "{anchors_en}", "content": "<p class='mb-3'>...</p>"}}
}}

Output JSON only."""


PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "MiniMax-Text-01": {"input": 0.0001, "output": 0.0011},
}

CONFIG_FILE = os.path.join(os.path.dirname(__file__), ".ai_config.json")

class AIConfig:
    def __init__(self):
        self.preferred_provider = os.getenv("AI_PROVIDER", "auto")
        self.enabled_providers = []
        self.temperature = 0.7
        self.api_keys = {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "zhipu": os.getenv("ZHIPU_API_KEY", ""),
            "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
            "qwen": os.getenv("DASHSCOPE_API_KEY", ""),
            "minimax": os.getenv("MINIMAX_API_KEY", ""),
        }
        self._load_from_file()

    def _load_from_file(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.preferred_provider = data.get("preferred_provider", self.preferred_provider)
                    self.temperature = data.get("temperature", self.temperature)
                    for k, v in data.get("api_keys", {}).items():
                        if k in self.api_keys and v:
                            self.api_keys[k] = v
        except Exception as e:
            print(f"Config load error: {e}")

    def _save_to_file(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"preferred_provider": self.preferred_provider, "temperature": self.temperature, "api_keys": self.api_keys}, f)
        except Exception as e:
            print(f"Config save error: {e}")

    def to_dict(self) -> dict:
        return {
            "preferred_provider": self.preferred_provider,
            "enabled_providers": self.enabled_providers,
            "temperature": self.temperature,
            "api_keys_status": {k: bool(v) and len(v) > 5 for k, v in self.api_keys.items()},
            "api_keys_masked": {k: f"{v[:4]}...{v[-4:]}" if v and len(v) >= 10 else "" for k, v in self.api_keys.items()}
        }

    def update(self, data: dict):
        if "preferred_provider" in data:
            self.preferred_provider = data["preferred_provider"]
        if "temperature" in data:
            self.temperature = max(0, min(1, float(data["temperature"])))
        self._save_to_file()

    def update_api_key(self, provider: str, key: str):
        if provider in self.api_keys:
            self.api_keys[provider] = key
            self._save_to_file()
            return True
        return False


ai_config = AIConfig()

class AIService:
    def __init__(self, config: AIConfig):
        self.config = config
        self.openai_client: Optional[OpenAI] = None
        self.anthropic_client: Optional[Anthropic] = None
        self.zhipu_client: Optional[OpenAI] = None
        self.deepseek_client: Optional[OpenAI] = None
        self.qwen_client: Optional[OpenAI] = None
        self.minimax_client: Optional[Anthropic] = None
        self.usage_history: list[TokenUsage] = []
        self._init_clients()

    def _init_clients(self):
        keys = self.config.api_keys
        self.openai_client = OpenAI(api_key=keys.get("openai")) if keys.get("openai") else None
        self.anthropic_client = Anthropic(api_key=keys.get("anthropic")) if keys.get("anthropic") else None
        self.zhipu_client = OpenAI(api_key=keys.get("zhipu"), base_url="https://open.bigmodel.cn/api/paas/v4/") if keys.get("zhipu") else None
        self.deepseek_client = OpenAI(api_key=keys.get("deepseek"), base_url="https://api.deepseek.com/v1") if keys.get("deepseek") else None
        self.qwen_client = OpenAI(api_key=keys.get("qwen"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1") if keys.get("qwen") else None
        self.minimax_client = Anthropic(api_key=keys.get("minimax"), base_url="https://api.minimaxi.com/anthropic") if keys.get("minimax") else None

    def reinit_client(self, provider: str):
        self._init_clients()

    def get_available_providers(self) -> list[str]:
        providers = []
        if self.openai_client: providers.append("openai")
        if self.anthropic_client: providers.append("anthropic")
        if self.zhipu_client: providers.append("zhipu")
        if self.deepseek_client: providers.append("deepseek")
        if self.qwen_client: providers.append("qwen")
        if self.minimax_client: providers.append("minimax")
        return providers

    def _record_usage(self, provider: str, model: str, input_tokens: int, output_tokens: int):
        pricing = PRICING.get(model, {"input": 0.001, "output": 0.002})
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000
        self.usage_history.append(TokenUsage(provider, model, input_tokens, output_tokens, cost, time.time()))

    def get_usage_stats(self) -> dict:
        total_input = sum(u.input_tokens for u in self.usage_history)
        total_output = sum(u.output_tokens for u in self.usage_history)
        total_cost = sum(u.cost for u in self.usage_history)
        by_provider = {}
        for u in self.usage_history:
            if u.provider not in by_provider:
                by_provider[u.provider] = {"input": 0, "output": 0, "cost": 0, "calls": 0}
            by_provider[u.provider]["input"] += u.input_tokens
            by_provider[u.provider]["output"] += u.output_tokens
            by_provider[u.provider]["cost"] += u.cost
            by_provider[u.provider]["calls"] += 1
        return {"total_input_tokens": total_input, "total_output_tokens": total_output, "total_cost_usd": round(total_cost, 4), "total_calls": len(self.usage_history), "by_provider": by_provider}

    def generate_scene(self, words: list[dict], provider: str = "auto") -> dict:
        if provider == "auto":
            available = self.get_available_providers()
            if not available:
                raise ValueError("No AI API Key configured")
            for p in ["minimax", "zhipu", "deepseek", "qwen", "openai", "anthropic"]:
                if p in available:
                    provider = p
                    break

        print(f"[AI Service] Words: {len(words)}, Provider: {provider}")

        words_per_scene = 40
        num_scenes = min(5, math.ceil(len(words) / words_per_scene))

        scenes = []
        for i in range(num_scenes):
            start_idx = i * words_per_scene
            end_idx = min((i + 1) * words_per_scene, len(words))
            scene_words = words[start_idx:end_idx]

            if not scene_words:
                continue

            bg = BG_IMAGES[i % len(BG_IMAGES)]

            print(f"[AI Service] Scene {i+1}/{num_scenes}, words: {len(scene_words)}")
            scene = self._generate_single_scene(i + 1, scene_words, bg["url"], bg["title_zh"], bg["title_en"], provider)

            if scene:
                scenes.append(scene)

        return {"scenes": scenes}

    def _generate_single_scene(self, scene_id: int, scene_words: list[dict], bg_image: str, scene_title_zh: str, scene_title_en: str, provider: str) -> dict:
        words_text = "\n".join([f"- {w['word']}: {w.get('pos', '')} {w.get('meaning', '')}" for w in scene_words])
        anchors = "Entrance -> Central -> Corner"
        anchors_en = "Entrance -> Central Area -> Corner"

        prompt = SCENE_PROMPT.format(
            scene_id=scene_id, scene_title_zh=scene_title_zh, scene_title_en=scene_title_en,
            bg_image=bg_image, anchors=anchors, anchors_en=anchors_en,
            word_count=len(scene_words), words=words_text
        )

        print(f"[AI Service] Prompt length: {len(prompt)}")

        try:
            if provider == "minimax" and self.minimax_client:
                return self._call_minimax(prompt)
            elif provider == "zhipu" and self.zhipu_client:
                return self._call_zhipu(prompt)
            elif provider == "deepseek" and self.deepseek_client:
                return self._call_deepseek(prompt)
            elif provider == "qwen" and self.qwen_client:
                return self._call_qwen(prompt)
            elif provider == "openai" and self.openai_client:
                return self._call_openai(prompt)
            elif provider == "anthropic" and self.anthropic_client:
                return self._call_anthropic(prompt)
        except Exception as e:
            print(f"[AI Service] Error: {e}")
            return None
        return None

    def _parse_and_clean(self, content: str) -> dict:
        start = content.find('{')
        end = content.rfind('}') + 1
        if start == -1 or end <= start:
            raise ValueError("No JSON found")

        json_str = content[start:end]
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"[AI Service] JSON error: {e}")
            json_str = json_str.replace('\\"', "'")
            result = json.loads(json_str)

        return self._clean_scene_html(result)

    def _clean_scene_html(self, scene: dict) -> dict:
        if "zh" in scene and "content" in scene["zh"]:
            scene["zh"]["content"] = self._fix_word_highlight(scene["zh"]["content"])
        if "en" in scene and "content" in scene["en"]:
            scene["en"]["content"] = self._fix_word_highlight(scene["en"]["content"])
        if "zh" in scene and "translationParagraphs" in scene["zh"]:
            scene["zh"]["translationParagraphs"] = [self._fix_word_highlight(p) for p in scene["zh"]["translationParagraphs"]]
        return scene

    def _fix_word_highlight(self, html: str) -> str:
        if not html:
            return html

        # Fix: wordword: pos. meaning
        pattern1 = r"<span class='word-highlight'>([a-zA-Z-]+)\1:\s*([^<]+)</span>"
        html = re.sub(pattern1, r"<span class='word-highlight'>\1<span class='tooltip'>\1: \2</span></span>", html)

        # Fix: <span>wordword: meaning</span>
        pattern2 = r"<span class='word-highlight'>([a-zA-Z-]+)([a-zA-Z-]+):\s*([^<]+)</span>"
        def fix_dup(m):
            w1, w2, meaning = m.groups()
            if w1.lower() == w2.lower():
                return f"<span class='word-highlight'>{w1}<span class='tooltip'>{w1}: {meaning}</span></span>"
            return m.group(0)
        html = re.sub(pattern2, fix_dup, html)

        # Fix: word</span>word: meaning
        pattern3 = r"<span class='word-highlight'>([a-zA-Z-]+)</span>\s*\1:\s*([^<\n]+)"
        html = re.sub(pattern3, r"<span class='word-highlight'>\1<span class='tooltip'>\1: \2</span></span>", html)

        # Fix: word</span><span class='tooltip'>
        pattern4 = r"<span class='word-highlight'>([^<]+)</span>\s*<span class='tooltip'>([^<]+)</span>"
        html = re.sub(pattern4, r"<span class='word-highlight'>\1<span class='tooltip'>\2</span></span>", html)

        # Fix naked: word: n. meaning
        pattern5 = r"(?<!</span>)(?<!['\">])([a-zA-Z]{3,}):\s*(n\.|v\.|adj\.|adv\.)\s*([^<\n,.]{2,20})"
        def wrap_naked(m):
            word, pos, meaning = m.groups()
            return f"<span class='word-highlight'>{word}<span class='tooltip'>{word}: {pos} {meaning}</span></span>"
        html = re.sub(pattern5, wrap_naked, html)

        return html

    def _call_minimax(self, prompt: str) -> dict:
        model = "MiniMax-Text-01"
        response = self.minimax_client.messages.create(
            model=model, max_tokens=8192,
            system="You are a Memory Palace scene generator. Output JSON only. Use single quotes for HTML attributes.",
            messages=[{"role": "user", "content": prompt}]
        )
        self._record_usage("minimax", model, response.usage.input_tokens, response.usage.output_tokens)
        print(f"[AI Service] MiniMax response: {len(response.content[0].text)} chars")
        return self._parse_and_clean(response.content[0].text)

    def _call_zhipu(self, prompt: str) -> dict:
        model = "glm-4-flash"
        response = self.zhipu_client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "Output JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.7
        )
        self._record_usage("zhipu", model, response.usage.prompt_tokens, response.usage.completion_tokens)
        return self._parse_and_clean(response.choices[0].message.content)

    def _call_deepseek(self, prompt: str) -> dict:
        model = "deepseek-chat"
        response = self.deepseek_client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "Output JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.7
        )
        self._record_usage("deepseek", model, response.usage.prompt_tokens, response.usage.completion_tokens)
        return self._parse_and_clean(response.choices[0].message.content)

    def _call_qwen(self, prompt: str) -> dict:
        model = "qwen-turbo"
        response = self.qwen_client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "Output JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.7
        )
        self._record_usage("qwen", model, response.usage.prompt_tokens, response.usage.completion_tokens)
        return self._parse_and_clean(response.choices[0].message.content)

    def _call_openai(self, prompt: str) -> dict:
        model = "gpt-4o-mini"
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "Output JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.7, response_format={"type": "json_object"}
        )
        self._record_usage("openai", model, response.usage.prompt_tokens, response.usage.completion_tokens)
        result = json.loads(response.choices[0].message.content)
        return self._clean_scene_html(result)

    def _call_anthropic(self, prompt: str) -> dict:
        model = "claude-3-haiku-20240307"
        response = self.anthropic_client.messages.create(model=model, max_tokens=4096, messages=[{"role": "user", "content": prompt}])
        self._record_usage("anthropic", model, response.usage.input_tokens, response.usage.output_tokens)
        return self._parse_and_clean(response.content[0].text)


ai_service = AIService(ai_config)
