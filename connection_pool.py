#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
High-Performance Connection Pool Manager
مدير Connection Pool عالي الأداء للألعاب المختلفة
"""

import asyncio
import aiohttp
import time
from typing import Dict, Optional, Any
from asyncio import Semaphore
from dataclasses import dataclass
from enum import Enum

class GameType(Enum):
    FREEFIRE = "freefire"
    JAWAKER = "jawaker"
    BIGOLIVE = "bigolive"
    POPPOLIVE = "poppolive"

@dataclass
class ConnectionPoolConfig:
    """إعدادات Connection Pool"""
    max_connections: int = 100
    max_connections_per_host: int = 50
    concurrent_requests_per_game: int = 10
    request_timeout: int = 30
    connection_timeout: int = 10
    read_timeout: int = 25
    dns_cache_ttl: int = 300
    keepalive_timeout: int = 30

class HighPerformanceConnectionPool:
    """Connection Pool عالي الأداء مع دعم المعالجة المتوازية"""
    
    def __init__(self, config: ConnectionPoolConfig = None):
        self.config = config or ConnectionPoolConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphores: Dict[GameType, Semaphore] = {}
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "requests_per_game": {game.value: 0 for game in GameType}
        }
        self._initialized = False
    
    async def initialize(self):
        """تهيئة Connection Pool"""
        if self._initialized:
            return
        
        # إعداد TCP Connector محسن
        connector = aiohttp.TCPConnector(
            limit=self.config.max_connections,
            limit_per_host=self.config.max_connections_per_host,
            ttl_dns_cache=self.config.dns_cache_ttl,
            use_dns_cache=True,
            keepalive_timeout=self.config.keepalive_timeout,
            enable_cleanup_closed=True,
            force_close=False
        )
        
        # إعداد Timeout محسن
        timeout = aiohttp.ClientTimeout(
            total=self.config.request_timeout,
            connect=self.config.connection_timeout,
            sock_read=self.config.read_timeout
        )
        
        # إنشاء Session مع إعدادات محسنة
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'iStation-HighPerf-API/2.0.0',
                'Accept': 'application/json, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            },
            cookie_jar=aiohttp.CookieJar(unsafe=True)
        )
        
        # إنشاء Semaphores لكل لعبة
        for game_type in GameType:
            self.semaphores[game_type] = Semaphore(self.config.concurrent_requests_per_game)
        
        self._initialized = True
        print(f"✅ تم تهيئة Connection Pool - {self.config.max_connections} اتصال، {self.config.concurrent_requests_per_game} طلب/لعبة")
    
    async def make_request(self, game_type: GameType, url: str, method: str = "POST",
                          data: Dict = None, json_data: Dict = None, headers: Dict = None, cookies: Dict = None) -> Optional[Dict]:
        """إرسال طلب محسن مع إدارة الموارد"""
        if not self._initialized:
            await self.initialize()
        
        semaphore = self.semaphores.get(game_type)
        if not semaphore:
            return None
        
        async with semaphore:  # التحكم في عدد الطلبات المتزامنة
            start_time = time.perf_counter()
            
            try:
                # دمج Headers
                request_headers = {
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                if headers:
                    request_headers.update(headers)
                
                # إرسال الطلب
                request_kwargs = {
                    "method": method,
                    "url": url,
                    "headers": request_headers,
                    "cookies": cookies
                }

                # إضافة البيانات حسب النوع
                if json_data:
                    request_kwargs["json"] = json_data
                elif data:
                    request_kwargs["data"] = data

                async with self.session.request(**request_kwargs) as response:
                    
                    response_time = time.perf_counter() - start_time
                    
                    # تحديث الإحصائيات
                    self.stats["total_requests"] += 1
                    self.stats["requests_per_game"][game_type.value] += 1
                    
                    if response.status == 200:
                        result = await response.json()
                        self.stats["successful_requests"] += 1
                        
                        # تحديث متوسط وقت الاستجابة
                        total_time = self.stats["avg_response_time"] * (self.stats["successful_requests"] - 1)
                        self.stats["avg_response_time"] = (total_time + response_time) / self.stats["successful_requests"]
                        
                        return {
                            "success": True,
                            "data": result,
                            "response_time": response_time,
                            "status_code": response.status
                        }
                    else:
                        self.stats["failed_requests"] += 1
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "response_time": response_time,
                            "status_code": response.status
                        }
            
            except asyncio.TimeoutError:
                self.stats["failed_requests"] += 1
                return {
                    "success": False,
                    "error": "Request timeout",
                    "response_time": time.perf_counter() - start_time
                }
            except Exception as e:
                self.stats["failed_requests"] += 1
                return {
                    "success": False,
                    "error": str(e),
                    "response_time": time.perf_counter() - start_time
                }
    
    async def batch_request(self, requests: list) -> list:
        """معالجة دفعة من الطلبات بشكل متوازي"""
        if not self._initialized:
            await self.initialize()
        
        tasks = []
        for req in requests:
            task = self.make_request(
                game_type=req.get("game_type"),
                url=req.get("url"),
                method=req.get("method", "POST"),
                data=req.get("data"),
                json_data=req.get("json_data"),
                headers=req.get("headers"),
                cookies=req.get("cookies")
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_stats(self) -> Dict:
        """الحصول على إحصائيات الأداء"""
        success_rate = 0
        if self.stats["total_requests"] > 0:
            success_rate = (self.stats["successful_requests"] / self.stats["total_requests"]) * 100
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "active_connections": len(self.session.connector._conns) if self.session else 0,
            "semaphore_status": {
                game.value: {
                    "available": sem._value,
                    "max": self.config.concurrent_requests_per_game
                }
                for game, sem in self.semaphores.items()
            }
        }
    
    async def cleanup(self):
        """تنظيف الموارد"""
        if self.session:
            await self.session.close()
            print("✅ تم إغلاق Connection Pool")

# مثيل عام للاستخدام
_connection_pool: Optional[HighPerformanceConnectionPool] = None

async def get_connection_pool() -> HighPerformanceConnectionPool:
    """الحصول على مثيل Connection Pool"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = HighPerformanceConnectionPool()
        await _connection_pool.initialize()
    return _connection_pool

async def cleanup_connection_pool():
    """تنظيف Connection Pool"""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.cleanup()
        _connection_pool = None
