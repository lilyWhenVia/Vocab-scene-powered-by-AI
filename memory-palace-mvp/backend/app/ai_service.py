"""AI 场景生成服务 - 支持多种 AI 提供商"""
import json
import os
import time
from typing import Optional
from dataclasses import dataclass
from openai import OpenAI
from anthropic import Anthropic

# Token 使用记录
@dataclass
class TokenUsage:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float  # 美元
    timestamp: float

# 场景生成 Prompt
SCENE_GENERATION_PROMPT = """你是一个记忆宫殿场景生成专家。请根据以下单词列表生成沉浸式记忆场景。

## 输入单词（共 {word_count} 个，必须全部包含）
{words}

## 核心要求
1. **必须包含所有单词**：每一个输入的单词都必须出现在场景中，不能遗漏任何一个
2. **每个场景包含约50个单词**，场景数量 = 单词总数 ÷ 50（向上取整，最多5个场景）
   - 1-50词：1个场景
   - 51-100词：2个场景
   - 101-150词：3个场景
   - 151-200词：4个场景
3. 每个场景有独立的主题、背景图、3个空间锚点
4. 中英双语叙事，单词自然嵌入故事
5. **每个场景的故事要足够长**，确保能容纳约50个单词，分5-7个段落叙述

## 输出格式（严格JSON）
{{
    "scenes": [
        {{
            "id": 1,
            "icon": "fa-tree",
            "bgImage": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1920&q=80",
            "zh": {{
                "title": "森林探险",
                "anchors": "入口→小径→湖边",
                "content": "<p class='mb-3'>第一段叙事，包含<span class='word-highlight'>单词<span class='tooltip'>单词: 词性. 释义</span></span>...</p><p class='mb-3'>第二段...</p>"
            }},
            "en": {{
                "title": "Forest Adventure",
                "anchors": "Entrance → Trail → Lakeside",
                "content": "<p class='mb-3'>First paragraph with <span class='word-highlight'>word<span class='tooltip'>word: pos. meaning</span></span>...</p>"
            }}
        }}
    ]
}}

## 写作规范
1. 使用第二人称"你"增强代入感
2. 单词嵌入要自然流畅，构成完整故事
3. 每个单词都必须用 word-highlight 和 tooltip 标记
4. bgImage 使用 Unsplash 高质量图片 URL（1920宽度）
5. **再次强调：所有 {word_count} 个单词必须全部出现在场景中**

请只输出JSON，不要有其他内容。"""


# 价格配置（每1K tokens，美元）
PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    "glm-4-flash": {"input": 0.0001, "output": 0.0001},  # 智谱 GLM-4-Flash 免费
    "glm-4": {"input": 0.014, "output": 0.014},  # 智谱 GLM-4
    "glm-4-plus": {"input": 0.007, "output": 0.007},  # 智谱 GLM-4-Plus
    "deepseek-chat": {"input": 0.00014, "output": 0.00028},  # DeepSeek
    "qwen-turbo": {"input": 0.0003, "output": 0.0006},  # 通义千问
    "MiniMax-Text-01": {"input": 0.0001, "output": 0.0011},  # MiniMax 性价比最高
}


# 运行时配置（带持久化）
CONFIG_FILE = os.path.join(os.path.dirname(__file__), ".ai_config.json")

class AIConfig:
    def __init__(self):
        self.preferred_provider = os.getenv("AI_PROVIDER", "auto")
        self.enabled_providers = []  # 空表示全部启用
        self.temperature = 0.7
        
        # API Keys（运行时可修改）
        self.api_keys = {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "zhipu": os.getenv("ZHIPU_API_KEY", ""),
            "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
            "qwen": os.getenv("DASHSCOPE_API_KEY", ""),
            "minimax": os.getenv("MINIMAX_API_KEY", ""),
        }
        
        # 从文件加载持久化配置
        self._load_from_file()
    
    def _load_from_file(self):
        """从文件加载配置"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    if "preferred_provider" in data:
                        self.preferred_provider = data["preferred_provider"]
                    if "temperature" in data:
                        self.temperature = data["temperature"]
                    if "api_keys" in data:
                        for k, v in data["api_keys"].items():
                            if k in self.api_keys and v:
                                self.api_keys[k] = v
        except Exception as e:
            print(f"Failed to load config: {e}")
    
    def _save_to_file(self):
        """保存配置到文件"""
        try:
            data = {
                "preferred_provider": self.preferred_provider,
                "temperature": self.temperature,
                "api_keys": self.api_keys
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def to_dict(self) -> dict:
        # 返回配置，API Key 只显示是否已配置（不暴露完整密钥）
        return {
            "preferred_provider": self.preferred_provider,
            "enabled_providers": self.enabled_providers,
            "temperature": self.temperature,
            "api_keys_status": {
                k: bool(v) and len(v) > 5 for k, v in self.api_keys.items()
            },
            "api_keys_masked": {
                k: self._mask_key(v) for k, v in self.api_keys.items()
            }
        }
    
    def _mask_key(self, key: str) -> str:
        """遮蔽 API Key，只显示前4位和后4位"""
        if not key or len(key) < 10:
            return ""
        return f"{key[:4]}...{key[-4:]}"
    
    def update(self, data: dict):
        if "preferred_provider" in data:
            self.preferred_provider = data["preferred_provider"]
        if "enabled_providers" in data:
            self.enabled_providers = data["enabled_providers"]
        if "temperature" in data:
            self.temperature = max(0, min(1, float(data["temperature"])))
        self._save_to_file()
    
    def update_api_key(self, provider: str, key: str):
        """更新 API Key"""
        if provider in self.api_keys:
            self.api_keys[provider] = key
            self._save_to_file()
            return True
        return False


# 先创建配置单例
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
        
        # Token 使用历史
        self.usage_history: list[TokenUsage] = []
        
        # 初始化客户端
        self._init_clients()
    
    def _init_clients(self):
        """根据配置初始化客户端"""
        keys = self.config.api_keys
        
        # OpenAI
        openai_key = keys.get("openai") or os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
        else:
            self.openai_client = None
        
        # Anthropic
        anthropic_key = keys.get("anthropic") or os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.anthropic_client = Anthropic(api_key=anthropic_key)
        else:
            self.anthropic_client = None
        
        # 智谱 GLM
        zhipu_key = keys.get("zhipu") or os.getenv("ZHIPU_API_KEY")
        if zhipu_key:
            self.zhipu_client = OpenAI(
                api_key=zhipu_key,
                base_url="https://open.bigmodel.cn/api/paas/v4/"
            )
        else:
            self.zhipu_client = None
        
        # DeepSeek
        deepseek_key = keys.get("deepseek") or os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            self.deepseek_client = OpenAI(
                api_key=deepseek_key,
                base_url="https://api.deepseek.com/v1"
            )
        else:
            self.deepseek_client = None
        
        # 通义千问
        qwen_key = keys.get("qwen") or os.getenv("DASHSCOPE_API_KEY")
        if qwen_key:
            self.qwen_client = OpenAI(
                api_key=qwen_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        else:
            self.qwen_client = None
        
        # MiniMax (使用 Anthropic 兼容 API)
        minimax_key = keys.get("minimax") or os.getenv("MINIMAX_API_KEY")
        if minimax_key:
            self.minimax_client = Anthropic(
                api_key=minimax_key,
                base_url="https://api.minimaxi.com/anthropic"
            )
        else:
            self.minimax_client = None
    
    def reinit_client(self, provider: str):
        """重新初始化指定提供商的客户端"""
        self._init_clients()
    
    def get_available_providers(self) -> list[str]:
        """获取可用的 AI 提供商"""
        providers = []
        if self.openai_client:
            providers.append("openai")
        if self.anthropic_client:
            providers.append("anthropic")
        if self.zhipu_client:
            providers.append("zhipu")
        if self.deepseek_client:
            providers.append("deepseek")
        if self.qwen_client:
            providers.append("qwen")
        if self.minimax_client:
            providers.append("minimax")
        return providers
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """计算成本"""
        pricing = PRICING.get(model, {"input": 0.001, "output": 0.002})
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000
    
    def _record_usage(self, provider: str, model: str, input_tokens: int, output_tokens: int):
        """记录 Token 使用"""
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        usage = TokenUsage(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            timestamp=time.time()
        )
        self.usage_history.append(usage)
        return usage
    
    def get_usage_stats(self) -> dict:
        """获取使用统计"""
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
        
        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cost_usd": round(total_cost, 4),
            "total_calls": len(self.usage_history),
            "by_provider": by_provider,
            "recent": [
                {
                    "provider": u.provider,
                    "model": u.model,
                    "input": u.input_tokens,
                    "output": u.output_tokens,
                    "cost": round(u.cost, 6),
                    "time": u.timestamp
                }
                for u in self.usage_history[-20:]
            ]
        }
    
    def generate_scene(self, words: list[dict], provider: str = "auto") -> dict:
        """
        生成记忆宫殿场景
        
        Args:
            words: [{"word": "apple", "pos": "n.", "meaning": "苹果"}, ...]
            provider: "openai", "anthropic", "zhipu", "deepseek", "qwen", "auto"
        
        Returns:
            场景数据字典
        """
        # 自动选择提供商
        if provider == "auto":
            available = self.get_available_providers()
            if not available:
                raise ValueError("未配置任何 AI API Key")
            # 优先使用国产（便宜）
            for p in ["zhipu", "deepseek", "minimax", "qwen", "openai", "anthropic"]:
                if p in available:
                    provider = p
                    break
        
        # 格式化单词列表
        words_text = "\n".join([
            f"- {w['word']}: {w.get('pos', '')} {w.get('meaning', '')}"
            for w in words
        ])
        
        print(f"[AI Service] 收到单词数: {len(words)}")
        
        prompt = SCENE_GENERATION_PROMPT.format(words=words_text, word_count=len(words))
        
        print(f"[AI Service] Prompt 长度: {len(prompt)} 字符")
        
        if provider == "anthropic" and self.anthropic_client:
            return self._generate_with_anthropic(prompt)
        elif provider == "zhipu" and self.zhipu_client:
            return self._generate_with_zhipu(prompt)
        elif provider == "deepseek" and self.deepseek_client:
            return self._generate_with_deepseek(prompt)
        elif provider == "qwen" and self.qwen_client:
            return self._generate_with_qwen(prompt)
        elif provider == "minimax" and self.minimax_client:
            return self._generate_with_minimax(prompt)
        elif provider == "openai" and self.openai_client:
            return self._generate_with_openai(prompt)
        else:
            raise ValueError(f"提供商 {provider} 不可用，请检查 API Key 配置")
    
    def _generate_with_openai(self, prompt: str) -> dict:
        model = "gpt-4o-mini"
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是记忆宫殿场景生成专家，只输出JSON格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # 记录使用
        self._record_usage(
            "openai", model,
            response.usage.prompt_tokens,
            response.usage.completion_tokens
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _generate_with_anthropic(self, prompt: str) -> dict:
        model = "claude-3-haiku-20240307"
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # 记录使用
        self._record_usage(
            "anthropic", model,
            response.usage.input_tokens,
            response.usage.output_tokens
        )
        
        content = response.content[0].text
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(content[start:end])
        raise ValueError("AI返回格式错误")
    
    def _generate_with_zhipu(self, prompt: str) -> dict:
        model = "glm-4-flash"  # 免费模型
        response = self.zhipu_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是记忆宫殿场景生成专家，只输出JSON格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # 记录使用
        self._record_usage(
            "zhipu", model,
            response.usage.prompt_tokens,
            response.usage.completion_tokens
        )
        
        content = response.choices[0].message.content
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(content[start:end])
        raise ValueError("AI返回格式错误")
    
    def _generate_with_deepseek(self, prompt: str) -> dict:
        model = "deepseek-chat"
        response = self.deepseek_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是记忆宫殿场景生成专家，只输出JSON格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # 记录使用
        self._record_usage(
            "deepseek", model,
            response.usage.prompt_tokens,
            response.usage.completion_tokens
        )
        
        content = response.choices[0].message.content
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(content[start:end])
        raise ValueError("AI返回格式错误")
    
    def _generate_with_qwen(self, prompt: str) -> dict:
        model = "qwen-turbo"
        response = self.qwen_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是记忆宫殿场景生成专家，只输出JSON格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # 记录使用
        self._record_usage(
            "qwen", model,
            response.usage.prompt_tokens,
            response.usage.completion_tokens
        )
        
        content = response.choices[0].message.content
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(content[start:end])
        raise ValueError("AI返回格式错误")
    
    def _generate_with_minimax(self, prompt: str) -> dict:
        model = "MiniMax-Text-01"  # 性价比最高的模型
        response = self.minimax_client.messages.create(
            model=model,
            max_tokens=8192,
            system="你是记忆宫殿场景生成专家，只输出JSON格式。注意：JSON中的HTML内容里的引号必须用单引号，不能用双引号。",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # 记录使用
        self._record_usage(
            "minimax", model,
            response.usage.input_tokens,
            response.usage.output_tokens
        )
        
        content = response.content[0].text
        print(f"[AI Service] MiniMax 返回长度: {len(content)} 字符")
        
        # 提取 JSON
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            json_str = content[start:end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"[AI Service] JSON解析失败: {e}")
                # 尝试修复常见问题：双引号转单引号
                json_str_fixed = json_str.replace('\\"', "'").replace('""', '"')
                try:
                    return json.loads(json_str_fixed)
                except:
                    # 打印部分内容帮助调试
                    print(f"[AI Service] JSON片段: {json_str[:500]}...")
                    raise ValueError(f"AI返回JSON格式错误: {e}")
        raise ValueError("AI返回格式错误")


# 单例
ai_service = AIService(ai_config)
