#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iStation API - خادم محلي للبحث عن أسماء اللاعبين
API للبحث عن اللاعبين في الألعاب المختلفة (PUBG, Free Fire, Jawaker, BigOLive)
يرجع أسماء اللاعبين فقط بدون معلومات إضافية
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import asyncio
import atexit
from typing import Optional
from contextlib import asynccontextmanager
import aiohttp
from asyncio import Semaphore

# استيراد وحدات البحث عن اللاعبين
from pubg_player import get_pubg_player_name, cleanup_resources as cleanup_pubg_resources, _search_player_async, initialize_pubg_system
from freefire_player import get_freefire_player_name, get_freefire_player_name_async
from jawaker_player import get_jawaker_player_name, get_jawaker_player_name_async
from bigolive_player import get_bigolive_player_name, get_bigolive_player_name_async
from poppolive_player import get_poppolive_player_name, get_poppolive_player_name_async
from connection_pool import cleanup_connection_pool

# إعدادات الأداء العالي
MAX_CONCURRENT_REQUESTS = 50  # الحد الأقصى للطلبات المتزامنة
HTTP_POOL_SIZE = 100  # حجم Connection Pool
REQUEST_TIMEOUT = 30  # مهلة الطلب بالثواني

# متغيرات عامة للموارد المشتركة
_http_session: Optional[aiohttp.ClientSession] = None
_request_semaphore: Optional[Semaphore] = None

# إدارة دورة حياة التطبيق
@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق - تهيئة وتنظيف الموارد"""
    global _http_session, _request_semaphore

    print("🚀 بدء تشغيل iStation API...")

    # إعداد Connection Pool للطلبات HTTP
    print("🌐 إعداد Connection Pool...")
    connector = aiohttp.TCPConnector(
        limit=HTTP_POOL_SIZE,  # إجمالي الاتصالات
        limit_per_host=50,     # اتصالات لكل host
        ttl_dns_cache=300,     # DNS cache
        use_dns_cache=True,
        keepalive_timeout=30,
        enable_cleanup_closed=True
    )

    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    _http_session = aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={
            'User-Agent': 'iStation-API/2.0.0'
        }
    )

    # إعداد Semaphore للتحكم في عدد الطلبات المتزامنة
    _request_semaphore = Semaphore(MAX_CONCURRENT_REQUESTS)
    print(f"⚡ تم إعداد Connection Pool - الحد الأقصى: {MAX_CONCURRENT_REQUESTS} طلب متزامن")

    # تهيئة نظام PUBG مع 3 متصفحات مستقلة
    print("🎮 تهيئة نظام البحث عن لاعبي PUBG...")
    try:
        success = await initialize_pubg_system()
        if success:
            print("✅ تم تهيئة نظام PUBG بنجاح!")
        else:
            print("⚠️ فشل في تهيئة نظام PUBG - سيعمل النظام بدون المتصفحات الثلاثة")
    except Exception as e:
        print(f"❌ خطأ في تهيئة نظام PUBG: {e}")

    yield

    print("🧹 تنظيف موارد التطبيق...")

    # تنظيف HTTP Session
    if _http_session:
        await _http_session.close()
        print("✅ تم إغلاق HTTP Session")

    # تنظيف موارد PUBG
    try:
        await cleanup_pubg_resources()
    except Exception as e:
        print(f"❌ خطأ في تنظيف موارد PUBG: {e}")

    print("✅ تم تنظيف جميع الموارد")

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="iStation Player API",
    description="API للبحث عن أسماء اللاعبين في الألعاب المختلفة",
    version="2.0.0",
    lifespan=lifespan
)

# نموذج البيانات للطلب
class PlayerRequest(BaseModel):
    player_id: str
    game_type: str = "pubg"  # افتراضي: pubg (pubg, freefire, jawaker, bigolive, poppolive)

# نموذج البيانات للاستجابة
class PlayerResponse(BaseModel):
    player_name: Optional[str] = None

async def get_player_name_async(player_id: str, game_type: str = "pubg") -> Optional[str]:
    """
    جلب اسم اللاعب حسب نوع اللعبة (نسخة غير متزامنة عالية الأداء)
    يحصل على الاستجابة الخام من ملفات الألعاب ويعالجها لاستخراج اسم اللاعب

    Args:
        player_id (str): معرف اللاعب
        game_type (str): نوع اللعبة (pubg, freefire, jawaker, bigolive, poppolive)

    Returns:
        str or None: اسم اللاعب أو None إذا لم يوجد
    """
    game_type = game_type.lower()

    try:
        # الحصول على الاستجابة الخام من ملفات الألعاب
        raw_response = None

        if game_type == "pubg":
            raw_response = await _search_player_async(player_id)
            # PUBG يرجع اسم اللاعب مباشرة (لم يتم تعديله بعد)
            print(f"🎮 PUBG Response for {player_id}: {raw_response}")
            return raw_response

        elif game_type in ["freefire", "ff"]:
            raw_response = await get_freefire_player_name_async(player_id)
            print(f"🔥 Free Fire Response for {player_id}: {raw_response}")

            # معالجة استجابة Free Fire - تحديث المعالجة
            if raw_response and isinstance(raw_response, dict):
                # التحقق من نجاح الطلب من connection_pool
                if raw_response.get('success'):
                    data = raw_response.get('data', {})
                    # التحقق من بنية الاستجابة الصحيحة
                    if data.get('status') == 200 and data.get('msg') == 'id_found':
                        player_data = data.get('data', {})
                        player_name = player_data.get('nickname')
                        print(f"✅ Free Fire Player Found: {player_name}")
                        return player_name
                    else:
                        print(f"❌ Free Fire Player Not Found - Status: {data.get('status')}, Msg: {data.get('msg')}")
                else:
                    print(f"❌ Free Fire Request Failed: {raw_response}")
            else:
                print(f"❌ Free Fire Invalid Response: {raw_response}")
            return None

        elif game_type in ["jawaker", "jw"]:
            raw_response = await get_jawaker_player_name_async(player_id)
            print(f"🎯 Jawaker Response for {player_id}: {raw_response}")

            # معالجة استجابة Jawaker - إصلاح بنية الاستجابة
            if raw_response and isinstance(raw_response, dict):
                if raw_response.get('success'):
                    data = raw_response.get('data', {})
                    # بنية Jawaker مختلفة - البيانات في user.login
                    user_data = data.get('user', {})
                    if user_data:
                        player_name = user_data.get('login')  # اسم اللاعب في login
                        print(f"✅ Jawaker Player Found: {player_name}")
                        return player_name
                    else:
                        print(f"❌ Jawaker No User Data: {data}")
                else:
                    print(f"❌ Jawaker Request Failed: {raw_response}")
            else:
                print(f"❌ Jawaker Invalid Response: {raw_response}")
            return None

        elif game_type in ["bigolive", "bigo"]:
            raw_response = await get_bigolive_player_name_async(player_id)
            print(f"🎪 BigOLive Response for {player_id}: {raw_response}")

            # معالجة استجابة BigOLive - إصلاح بنية الاستجابة
            if raw_response and isinstance(raw_response, dict):
                if raw_response.get('success'):
                    outer_data = raw_response.get('data', {})
                    if outer_data.get('success'):
                        inner_data = outer_data.get('data', {})
                        if inner_data.get('matched') and inner_data.get('exists'):
                            player_name = inner_data.get('nickname')
                            print(f"✅ BigOLive Player Found: {player_name}")
                            return player_name
                        else:
                            print(f"❌ BigOLive Player Not Found - Matched: {inner_data.get('matched')}, Exists: {inner_data.get('exists')}")
                    else:
                        print(f"❌ BigOLive Inner Request Failed: {outer_data}")
                else:
                    print(f"❌ BigOLive Request Failed: {raw_response}")
            else:
                print(f"❌ BigOLive Invalid Response: {raw_response}")
            return None

        elif game_type in ["poppolive", "poppo"]:
            raw_response = await get_poppolive_player_name_async(player_id)
            print(f"🎭 Poppo Live Response for {player_id}: {raw_response}")

            # معالجة استجابة Poppo Live - إصلاح بنية الاستجابة
            if raw_response and isinstance(raw_response, dict):
                if raw_response.get('success'):
                    outer_data = raw_response.get('data', {})
                    if outer_data.get('success'):
                        inner_data = outer_data.get('data', {})
                        if inner_data.get('matched') and inner_data.get('exists'):
                            player_name = inner_data.get('nickname')
                            print(f"✅ Poppo Live Player Found: {player_name}")
                            return player_name
                        else:
                            print(f"❌ Poppo Live Player Not Found - Matched: {inner_data.get('matched')}, Exists: {inner_data.get('exists')}")
                    else:
                        print(f"❌ Poppo Live Inner Request Failed: {outer_data}")
                else:
                    print(f"❌ Poppo Live Request Failed: {raw_response}")
            else:
                print(f"❌ Poppo Live Invalid Response: {raw_response}")
            return None

        else:
            return None

    except Exception as e:
        print(f"❌ خطأ في معالجة استجابة {game_type}: {e}")
        print(f"📋 Raw response: {raw_response}")
        print(f"🔍 Exception details: {type(e).__name__}: {str(e)}")
        return None

def get_player_name(player_id: str, game_type: str = "pubg") -> Optional[str]:
    """
    جلب اسم اللاعب حسب نوع اللعبة (نسخة متزامنة للاختبار)
    يحصل على الاستجابة الخام من ملفات الألعاب ويعالجها لاستخراج اسم اللاعب

    Args:
        player_id (str): معرف اللاعب
        game_type (str): نوع اللعبة (pubg, freefire, jawaker, bigolive, poppolive)

    Returns:
        str or None: اسم اللاعب أو None إذا لم يوجد
    """
    game_type = game_type.lower()

    try:
        # الحصول على الاستجابة الخام من ملفات الألعاب
        raw_response = None

        if game_type == "pubg":
            raw_response = get_pubg_player_name(player_id)
            # PUBG يرجع اسم اللاعب مباشرة (لم يتم تعديله بعد)
            return raw_response

        elif game_type in ["freefire", "ff"]:
            raw_response = get_freefire_player_name(player_id)
            # معالجة استجابة Free Fire - إصلاح بنية الاستجابة
            if raw_response and isinstance(raw_response, dict):
                if raw_response.get('success'):
                    data = raw_response.get('data', {})
                    if data.get('status') == 200 and data.get('msg') == 'id_found':
                        player_data = data.get('data', {})
                        player_name = player_data.get('nickname')
                        return player_name
            return None

        elif game_type in ["jawaker", "jw"]:
            raw_response = get_jawaker_player_name(player_id)
            # معالجة استجابة Jawaker - إصلاح بنية الاستجابة
            if raw_response and isinstance(raw_response, dict):
                if raw_response.get('success'):
                    data = raw_response.get('data', {})
                    # بنية Jawaker مختلفة - البيانات في user.login
                    user_data = data.get('user', {})
                    if user_data:
                        return user_data.get('login')  # اسم اللاعب في login
            return None

        elif game_type in ["bigolive", "bigo"]:
            raw_response = get_bigolive_player_name(player_id)
            # معالجة استجابة BigOLive - إصلاح بنية الاستجابة
            if raw_response and isinstance(raw_response, dict):
                if raw_response.get('success'):
                    outer_data = raw_response.get('data', {})
                    if outer_data.get('success'):
                        inner_data = outer_data.get('data', {})
                        if inner_data.get('matched') and inner_data.get('exists'):
                            return inner_data.get('nickname')
            return None

        elif game_type in ["poppolive", "poppo"]:
            raw_response = get_poppolive_player_name(player_id)
            # معالجة استجابة Poppo Live - إصلاح بنية الاستجابة
            if raw_response and isinstance(raw_response, dict):
                if raw_response.get('success'):
                    outer_data = raw_response.get('data', {})
                    if outer_data.get('success'):
                        inner_data = outer_data.get('data', {})
                        if inner_data.get('matched') and inner_data.get('exists'):
                            return inner_data.get('nickname')
            return None

        else:
            return None

    except Exception as e:
        print(f"خطأ في معالجة استجابة {game_type}: {e}")
        return None

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "iStation Player API",
        "version": "2.0.0",
        "description": "API للبحث عن أسماء اللاعبين",
        "supported_games": ["PUBG", "Free Fire", "Jawaker", "BigOLive", "Poppo Live"],
        "endpoint": "/get_player_name"
    }

@app.post("/get_player_name", response_model=PlayerResponse)
async def get_player_name_endpoint(request: PlayerRequest):
    """
    جلب اسم اللاعب باستخدام معرف اللاعب ونوع اللعبة

    Body:
        {
            "player_id": "معرف_اللاعب",
            "game_type": "نوع_اللعبة" (pubg, freefire, jawaker, bigolive, poppolive)
        }

    Returns:
        {"player_name": "اسم_اللاعب"} أو {"player_name": null}
    """
    try:
        # التحقق من صحة معرف اللاعب
        if not str(request.player_id).strip():
            return PlayerResponse(player_name=None)
        
        # التحقق من نوع اللعبة المدعوم
        supported_games = ["pubg", "freefire", "ff", "jawaker", "jw", "bigolive", "bigo", "poppolive", "poppo"]
        if request.game_type.lower() not in supported_games:
            return PlayerResponse(player_name=None)
        
        # جلب اسم اللاعب
        print(f"🔍 Processing request - Player ID: {request.player_id.strip()}, Game: {request.game_type}")
        player_name = await get_player_name_async(request.player_id.strip(), request.game_type)
        print(f"📤 Returning response - Player Name: {player_name}")

        return PlayerResponse(player_name=player_name)
    
    except Exception as e:
        print(f"❌ Error in endpoint: {e}")
        return PlayerResponse(player_name=None)

@app.get("/health")
async def health_check():
    """فحص صحة الخادم"""
    return {
        "status": "healthy",
        "message": "iStation API is running",
        "supported_games": ["PUBG", "Free Fire", "Jawaker", "BigOLive", "Poppo Live"]
    }

@app.get("/stats")
async def get_performance_stats():
    """الحصول على إحصائيات الأداء"""
    try:
        from connection_pool import get_connection_pool
        pool = await get_connection_pool()
        stats = pool.get_stats()

        return {
            "status": "success",
            "connection_pool_stats": stats,
            "max_concurrent_requests": MAX_CONCURRENT_REQUESTS,
            "pubg_browsers": 3,
            "other_games_concurrent_limit": 10
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    print("🚀 iStation Player API Server")
    print("=" * 50)
    print("🎮 خادم محلي للبحث عن أسماء اللاعبين")
    print("🌐 الخادم: http://localhost:8001")
    print("📚 الوثائق: http://localhost:8001/docs")
    print("🎯 الألعاب المدعومة: PUBG, Free Fire, Jawaker, BigOLive, Poppo Live")
    print("=" * 50)
    print("\n📋 أمثلة الاستخدام:")
    print('  PUBG: {"player_id": "5443564406", "game_type": "pubg"}')
    print('  Free Fire: {"player_id": "11442289597", "game_type": "freefire"}')
    print('  Jawaker: {"player_id": "1230574182", "game_type": "jawaker"}')
    print('  BigOLive: {"player_id": "988621429", "game_type": "bigolive"}')
    print('  Poppo Live: {"player_id": "8218218", "game_type": "poppolive"}')
    print("\n✅ الخادم يرجع أسماء اللاعبين فقط")
    print("🔧 يستخدم 3 متصفحات مستقلة للبحث عن لاعبي PUBG")

    # إعدادات Uvicorn محسنة للأداء العالي
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        workers=1,  # عامل واحد لتجنب تعارض الموارد المشتركة
        loop="asyncio",  # استخدام asyncio loop
        http="httptools",  # HTTP parser محسن
        ws="websockets",  # WebSocket implementation محسن
        lifespan="on",  # تفعيل lifespan events
        access_log=False,  # إيقاف access logs لتحسين الأداء
        server_header=False,  # إيقاف server header
        date_header=False,  # إيقاف date header
        limit_concurrency=MAX_CONCURRENT_REQUESTS,  # حد الطلبات المتزامنة
        limit_max_requests=10000,  # حد الطلبات الإجمالية قبل إعادة التشغيل
        timeout_keep_alive=5,  # مهلة keep-alive
        timeout_graceful_shutdown=30  # مهلة الإغلاق الآمن
    )
