"""数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    word_lists = relationship("WordList", back_populates="owner")

class WordList(Base):
    """单词列表"""
    __tablename__ = "word_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))
    words_json = Column(Text)  # JSON格式存储单词
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="word_lists")
    scenes = relationship("Scene", back_populates="word_list")

class Scene(Base):
    """AI生成的场景"""
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    word_list_id = Column(Integer, ForeignKey("word_lists.id"))
    scene_order = Column(Integer)  # 场景顺序
    scene_data_json = Column(Text)  # 完整场景数据JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    word_list = relationship("WordList", back_populates="scenes")
