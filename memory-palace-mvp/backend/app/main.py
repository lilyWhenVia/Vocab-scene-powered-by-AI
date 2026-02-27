"""FastAPI 主入口 - 记了么"""
import json
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .ai_service import ai_service, ai_config, result_cache
from .analytics import analytics

app = FastAPI(title="记了么 API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 配置 ==========
ADMIN_KEY = os.getenv("ADMIN_KEY", "admin123")  # 开发者仪表盘密钥

# ========== Pydantic 模型 ==========

class WordItem(BaseModel):
    word: str
    pos: Optional[str] = ""
    meaning: Optional[str] = ""

class GenerateRequest(BaseModel):
    name: str
    words: list[WordItem]

class TrackEvent(BaseModel):
    event: str
    data: Optional[dict] = None

# ========== 文件解析路由 ==========

@app.post("/parse-file")
async def parse_file(file: UploadFile = File(...)):
    """解析上传的文件"""
    analytics.track("file_upload", is_guest=True, data={"filename": file.filename})
    
    filename = file.filename.lower()
    content = await file.read()
    
    try:
        if filename.endswith('.txt'):
            text = content.decode('utf-8', errors='ignore')
        elif filename.endswith('.pdf'):
            try:
                import pypdf
                from io import BytesIO
                reader = pypdf.PdfReader(BytesIO(content))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            except ImportError:
                raise HTTPException(status_code=500, detail="服务器未安装 pypdf")
        elif filename.endswith(('.doc', '.docx')):
            try:
                from docx import Document
                from io import BytesIO
                doc = Document(BytesIO(content))
                text = "\n".join(p.text for p in doc.paragraphs)
            except ImportError:
                raise HTTPException(status_code=500, detail="服务器未安装 python-docx")
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式")
        
        return {"text": text, "filename": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")

# ========== AI 生成路由 ==========

@app.post("/generate")
def generate_scenes(req: GenerateRequest):
    """AI 生成记忆宫殿场景（无需登录）"""
    words = [w.model_dump() for w in req.words]
    
    # 日志：前端传入的单词数
    print(f"[Generate] 前端传入单词数: {len(words)}")
    print(f"[Generate] 前10个单词: {[w['word'] for w in words[:10]]}")
    
    # 限制最多 200 词
    MAX_WORDS = 200
    remaining_words = []
    if len(words) > MAX_WORDS:
        remaining_words = words[MAX_WORDS:]
        words = words[:MAX_WORDS]
        print(f"[Generate] 超过200词，截取前200，剩余: {len(remaining_words)}")
    
    print(f"[Generate] 发送给AI的单词数: {len(words)}")
    
    analytics.track("generate_scene", is_guest=True, data={"word_count": len(words)})
    
    try:
        # AI 自动决定场景数量和内容
        result = ai_service.generate_scene(words, provider=ai_config.preferred_provider)
        
        # 处理返回格式，支持单场景和多场景
        if "scenes" in result:
            scenes = result["scenes"]
        else:
            result["id"] = 1
            scenes = [result]
        
        # 日志：统计AI返回的场景信息
        print(f"[Generate] AI返回场景数: {len(scenes)}")
        for i, s in enumerate(scenes):
            zh_content = s.get('zh', {}).get('content', '')
            word_count_in_scene = zh_content.count('word-highlight')
            print(f"[Generate] 场景{i+1} 标题: {s.get('zh', {}).get('title', '?')}, 包含单词数: {word_count_in_scene}")
        
        response = {
            "message": f"成功生成 {len(scenes)} 个记忆场景",
            "scenes": scenes,
            "word_count": len(words)
        }
        
        # 如果有剩余单词，返回给前端缓存
        if remaining_words:
            response["remaining_words"] = remaining_words
            response["message"] += f"（剩余 {len(remaining_words)} 词待生成）"
        
        return response
    except Exception as e:
        import traceback
        print(f"Generate error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")

# ========== 埋点路由 ==========

@app.post("/track")
def track_event(event: TrackEvent):
    """前端埋点"""
    analytics.track(
        event.event,
        is_guest=True,
        data=event.data or {}
    )
    return {"status": "ok"}

# ========== 开发者仪表盘路由 ==========

@app.get("/admin/stats")
def get_admin_stats(key: str):
    """获取统计数据（需要管理员密钥）"""
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="无权访问")
    
    return {
        "analytics": analytics.get_stats(),
        "ai_usage": ai_service.get_usage_stats(),
        "cache": result_cache.get_stats(),
        "available_providers": ai_service.get_available_providers(),
        "ai_config": ai_config.to_dict()
    }

class AIConfigUpdate(BaseModel):
    preferred_provider: Optional[str] = None
    temperature: Optional[float] = None

class APIKeyUpdate(BaseModel):
    provider: str
    api_key: str

@app.post("/admin/config")
def update_ai_config(key: str, config: AIConfigUpdate):
    """更新 AI 配置（需要管理员密钥）"""
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="无权访问")
    
    ai_config.update(config.model_dump(exclude_none=True))
    analytics.track("admin_config_update", data=ai_config.to_dict())
    
    return {
        "message": "配置已更新",
        "config": ai_config.to_dict()
    }

@app.post("/admin/api-key")
def update_api_key(key: str, data: APIKeyUpdate):
    """更新 AI 提供商的 API Key（需要管理员密钥）"""
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="无权访问")
    
    provider = data.provider
    api_key = data.api_key.strip()
    
    valid_providers = ["openai", "anthropic", "zhipu", "deepseek", "qwen", "minimax"]
    if provider not in valid_providers:
        raise HTTPException(status_code=400, detail=f"无效的提供商，支持: {', '.join(valid_providers)}")
    
    # 更新配置
    ai_config.update_api_key(provider, api_key)
    
    # 重新初始化客户端
    ai_service.reinit_client(provider)
    
    analytics.track("admin_api_key_update", data={"provider": provider, "has_key": bool(api_key)})
    
    return {
        "message": f"{provider} API Key 已更新",
        "available_providers": ai_service.get_available_providers(),
        "api_keys_status": ai_config.to_dict()["api_keys_status"]
    }

@app.delete("/admin/api-key")
def delete_api_key(key: str, provider: str):
    """删除 AI 提供商的 API Key（需要管理员密钥）"""
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="无权访问")
    
    ai_config.update_api_key(provider, "")
    ai_service.reinit_client(provider)
    
    return {
        "message": f"{provider} API Key 已删除",
        "available_providers": ai_service.get_available_providers()
    }

# ========== 健康检查 ==========

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "ai_providers": ai_service.get_available_providers()
    }
