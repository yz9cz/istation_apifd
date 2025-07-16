#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للمتصفحات
"""

import asyncio
import sys

async def test_browser_initialization():
    """اختبار تهيئة المتصفحات"""
    try:
        from pubg_player import initialize_pubg_system
        
        print("🧪 اختبار تهيئة نظام PUBG...")
        print("=" * 50)
        
        success = await initialize_pubg_system()
        
        if success:
            print("\n✅ تم تهيئة نظام PUBG بنجاح!")
            print("🎮 المتصفحات الثلاثة جاهزة للاستخدام")
        else:
            print("\n❌ فشل في تهيئة نظام PUBG")
            
        return success
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

async def test_pubg_search():
    """اختبار البحث عن لاعب PUBG"""
    try:
        from pubg_player import _search_player_async
        
        print("\n🔍 اختبار البحث عن لاعب PUBG...")
        print("=" * 50)
        
        # اختبار معرف لاعب
        player_id = "5443564406"
        print(f"البحث عن اللاعب: {player_id}")
        
        result = await _search_player_async(player_id)
        
        if result:
            print(f"✅ تم العثور على اللاعب: {result}")
        else:
            print("❌ لم يتم العثور على اللاعب")
            
        return result is not None
        
    except Exception as e:
        print(f"❌ خطأ في البحث: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار نظام المتصفحات")
    print("=" * 50)
    
    # اختبار تهيئة المتصفحات
    init_success = await test_browser_initialization()
    
    if init_success:
        # اختبار البحث
        search_success = await test_pubg_search()
        
        if search_success:
            print("\n🎉 جميع الاختبارات نجحت!")
        else:
            print("\n⚠️ فشل اختبار البحث")
    else:
        print("\n❌ فشل اختبار التهيئة")
    
    # تنظيف الموارد
    try:
        from pubg_player import cleanup_resources
        await cleanup_resources()
        print("\n🧹 تم تنظيف الموارد")
    except Exception as e:
        print(f"\n❌ خطأ في تنظيف الموارد: {e}")

if __name__ == "__main__":
    asyncio.run(main())
