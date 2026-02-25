"""简单埋点和数据分析"""
import time
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict

@dataclass
class Event:
    name: str
    user_id: Optional[int]
    is_guest: bool
    data: dict
    timestamp: float = field(default_factory=time.time)

class Analytics:
    def __init__(self):
        self.events: list[Event] = []
        self.page_views: dict[str, int] = defaultdict(int)
        self.user_actions: dict[str, int] = defaultdict(int)
    
    def track(self, event_name: str, user_id: Optional[int] = None, is_guest: bool = False, data: dict = None):
        """记录事件"""
        event = Event(
            name=event_name,
            user_id=user_id,
            is_guest=is_guest,
            data=data or {},
            timestamp=time.time()
        )
        self.events.append(event)
        self.user_actions[event_name] += 1
    
    def track_page_view(self, page: str):
        """记录页面访问"""
        self.page_views[page] += 1
    
    def get_stats(self) -> dict:
        """获取统计数据"""
        # 用户统计
        unique_users = set()
        guest_count = 0
        registered_count = 0
        
        for e in self.events:
            if e.is_guest:
                guest_count += 1
            elif e.user_id:
                unique_users.add(e.user_id)
                registered_count += 1
        
        # 时间分布（最近24小时，按小时）
        now = time.time()
        hourly = defaultdict(int)
        for e in self.events:
            if now - e.timestamp < 86400:  # 24小时
                hour = int((now - e.timestamp) / 3600)
                hourly[f"{hour}h前"] += 1
        
        # 事件类型统计
        event_types = defaultdict(int)
        for e in self.events:
            event_types[e.name] += 1
        
        return {
            "total_events": len(self.events),
            "unique_users": len(unique_users),
            "guest_actions": guest_count,
            "registered_actions": registered_count,
            "page_views": dict(self.page_views),
            "user_actions": dict(self.user_actions),
            "event_types": dict(event_types),
            "hourly_distribution": dict(hourly),
            "recent_events": [
                {
                    "name": e.name,
                    "user_id": e.user_id,
                    "is_guest": e.is_guest,
                    "data": e.data,
                    "time": e.timestamp
                }
                for e in self.events[-50:]
            ]
        }

# 单例
analytics = Analytics()
