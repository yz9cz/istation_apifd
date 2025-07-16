#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Free Fire Player Name Lookup - High Performance Version (New API)
وحدة البحث عن أسماء لاعبي Free Fire - نسخة عالية الأداء (API جديد)
Uses: https://api-check-ban.vercel.app/check_ban/
"""

import asyncio
from typing import Optional
from connection_pool import get_connection_pool, GameType

async def get_freefire_player_name_async(player_id: str) -> Optional[str]:
    """
    جلب اسم لاعب Free Fire من API الجديد - نسخة غير متزامنة عالية الأداء

    Args:
        player_id (str): معرف اللاعب

    Returns:
        dict: الرد الكامل من الـ API أو رسالة خطأ
    """
    try:
        pool = await get_connection_pool()

        # إرسال الطلب باستخدام Connection Pool إلى الـ API الجديد
        result = await pool.make_request(
            game_type=GameType.FREEFIRE,
            url=f'https://api-check-ban.vercel.app/check_ban/{player_id}',
            method='GET'
        )

        # إرجاع الرد الكامل بدلاً من معالجته
        return result

    except Exception as e:
        return {"error": str(e), "success": False}

def get_freefire_player_name(player_id: str) -> Optional[dict]:
    """
    جلب بيانات لاعب Free Fire - نسخة متزامنة تعيد الاستجابة الخام

    Args:
        player_id (str): معرف اللاعب

    Returns:
        dict: الاستجابة الخام من الـ API أو رسالة خطأ
    """
    try:
        # تشغيل النسخة غير المتزامنة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(get_freefire_player_name_async(player_id))
            # إرجاع الاستجابة الخام كما هي
            return result
        finally:
            loop.close()
    except Exception as e:
        return {"error": str(e), "success": False}



if __name__ == "__main__":
    import json

    # اختبار الوحدة
    test_player_id = input("أدخل معرف لاعب Free Fire للاختبار: ")
    if test_player_id:
        print(f"البحث عن اللاعب: {test_player_id}")

        # البحث عن اللاعب والحصول على الرد الكامل
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(get_freefire_player_name_async(test_player_id))
            # طباعة الرد الكامل بصيغة JSON
            print(json.dumps(result, ensure_ascii=False, indent=2))
        finally:
            loop.close()
    else:
        print("❌ لم يتم إدخال معرف اللاعب")
