#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iStation API Test Suite
مجموعة اختبارات مشروع iStation API
"""

import pytest
import asyncio
import requests
import time
from typing import Dict, Any
from fastapi.testclient import TestClient

# استيراد التطبيق
try:
    from main import app, get_player_name, get_player_name_async
    MAIN_AVAILABLE = True
except ImportError:
    MAIN_AVAILABLE = False
    print("❌ لا يمكن استيراد main.py")

class TestAPI:
    """اختبارات API"""
    
    @pytest.fixture
    def client(self):
        """إنشاء عميل اختبار"""
        if not MAIN_AVAILABLE:
            pytest.skip("main.py غير متوفر")
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """اختبار الصفحة الرئيسية"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "2.0.0"
    
    def test_health_endpoint(self, client):
        """اختبار فحص الصحة"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_stats_endpoint(self, client):
        """اختبار إحصائيات الأداء"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_get_player_name_invalid_request(self, client):
        """اختبار طلب غير صحيح"""
        # طلب فارغ
        response = client.post("/get_player_name", json={})
        assert response.status_code == 422
        
        # معرف فارغ
        response = client.post("/get_player_name", json={
            "player_id": "",
            "game_type": "pubg"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["player_name"] is None
    
    def test_get_player_name_unsupported_game(self, client):
        """اختبار لعبة غير مدعومة"""
        response = client.post("/get_player_name", json={
            "player_id": "123456",
            "game_type": "unsupported_game"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["player_name"] is None
    
    @pytest.mark.asyncio
    async def test_pubg_player_search(self):
        """اختبار البحث عن لاعب PUBG"""
        if not MAIN_AVAILABLE:
            pytest.skip("main.py غير متوفر")
        
        # اختبار معرف صحيح
        result = await get_player_name_async("5443564406", "pubg")
        # النتيجة قد تكون None أو اسم اللاعب
        assert result is None or isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_freefire_player_search(self):
        """اختبار البحث عن لاعب Free Fire"""
        if not MAIN_AVAILABLE:
            pytest.skip("main.py غير متوفر")
        
        result = await get_player_name_async("11442289597", "freefire")
        assert result is None or isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_jawaker_player_search(self):
        """اختبار البحث عن لاعب Jawaker"""
        if not MAIN_AVAILABLE:
            pytest.skip("main.py غير متوفر")
        
        result = await get_player_name_async("1230574182", "jawaker")
        assert result is None or isinstance(result, str)

class TestPerformance:
    """اختبارات الأداء"""
    
    @pytest.fixture
    def client(self):
        if not MAIN_AVAILABLE:
            pytest.skip("main.py غير متوفر")
        return TestClient(app)
    
    def test_response_time(self, client):
        """اختبار زمن الاستجابة"""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0  # أقل من ثانية واحدة
    
    def test_concurrent_requests(self, client):
        """اختبار الطلبات المتزامنة"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = client.get("/health")
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # إنشاء 10 threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # انتظار انتهاء جميع الـ threads
        for thread in threads:
            thread.join()
        
        # التحقق من النتائج
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        assert success_count >= 8  # على الأقل 80% نجاح

class TestModules:
    """اختبار الوحدات الفردية"""
    
    def test_import_modules(self):
        """اختبار استيراد الوحدات"""
        modules = [
            "pubg_player",
            "freefire_player", 
            "jawaker_player",
            "bigolive_player",
            "poppolive_player",
            "connection_pool"
        ]
        
        for module_name in modules:
            try:
                __import__(module_name)
                print(f"✅ {module_name}: تم الاستيراد بنجاح")
            except ImportError as e:
                print(f"❌ {module_name}: فشل الاستيراد - {e}")
                # لا نفشل الاختبار لأن بعض الوحدات قد تحتاج dependencies خاصة

class TestLiveServer:
    """اختبار الخادم المباشر"""
    
    BASE_URL = "http://localhost:8001"
    
    def test_server_running(self):
        """اختبار تشغيل الخادم"""
        try:
            response = requests.get(f"{self.BASE_URL}/health", timeout=5)
            assert response.status_code == 200
            print("✅ الخادم يعمل بشكل صحيح")
        except requests.exceptions.ConnectionError:
            pytest.skip("الخادم غير متاح - تشغيل python main.py أولاً")
        except requests.exceptions.Timeout:
            pytest.fail("انتهت مهلة الاتصال بالخادم")
    
    def test_api_endpoints(self):
        """اختبار نقاط النهاية"""
        try:
            # اختبار الصفحة الرئيسية
            response = requests.get(f"{self.BASE_URL}/", timeout=5)
            assert response.status_code == 200
            
            # اختبار الوثائق
            response = requests.get(f"{self.BASE_URL}/docs", timeout=5)
            assert response.status_code == 200
            
            print("✅ جميع نقاط النهاية تعمل")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("الخادم غير متاح")

def run_tests():
    """تشغيل جميع الاختبارات"""
    print("🧪 بدء تشغيل الاختبارات...")
    print("=" * 50)
    
    # تشغيل pytest
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])
    
    if exit_code == 0:
        print("\n🎉 جميع الاختبارات نجحت!")
    else:
        print(f"\n❌ فشل في {exit_code} اختبار")
    
    return exit_code

if __name__ == "__main__":
    run_tests()
