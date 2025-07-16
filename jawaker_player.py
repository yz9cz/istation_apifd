#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jawaker Player Name Lookup - High Performance Version
وحدة البحث عن أسماء لاعبي جواكر - نسخة عالية الأداء
"""

import asyncio
from typing import Optional
from connection_pool import get_connection_pool, GameType

def get_jawaker_player_name(player_id: str) -> Optional[dict]:
    """
    جلب بيانات لاعب جواكر من API jawaker.com - يعيد الاستجابة الخام
    API: https://shop.jawaker.com/en/webshop/verify_user

    Args:
        player_id (str): معرف اللاعب (player_number)

    Returns:
        dict: الاستجابة الخام من الـ API أو رسالة خطأ
    """
    try:
        # تشغيل النسخة غير المتزامنة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(get_jawaker_player_name_async(player_id))
            # إرجاع الاستجابة الخام كما هي
            return result
        finally:
            loop.close()
    except Exception as e:
        return {"error": str(e), "success": False}

async def get_jawaker_player_name_async(player_id: str) -> Optional[dict]:
    """
    جلب بيانات لاعب جواكر من API jawaker.com - نسخة غير متزامنة تعيد الاستجابة الخام
    API: https://shop.jawaker.com/en/webshop/verify_user

    Args:
        player_id (str): معرف اللاعب (player_number)

    Returns:
        dict: الاستجابة الخام من الـ API أو رسالة خطأ
    """
    try:
        pool = await get_connection_pool()

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ar,en;q=0.9',
            'Origin': 'https://shop.jawaker.com',
            'Referer': 'https://shop.jawaker.com/en/webshop/jawaker-coins',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        }

        payload = {
            'player_number': str(player_id).strip()
        }

        result = await pool.make_request(
            game_type=GameType.JAWAKER,
            url="https://shop.jawaker.com/en/webshop/verify_user",
            method='POST',
            data=payload,
            headers=headers
        )

        # إرجاع الاستجابة الخام كما هي
        return result

    except Exception as e:
        return {"error": str(e), "success": False}

if __name__ == "__main__":
    # اختبار الوحدة
    test_player_id = input("أدخل معرف لاعب Jawaker للاختبار: ")
    if test_player_id:
        print(f"البحث عن اللاعب: {test_player_id}")
        player_name = get_jawaker_player_name(test_player_id)
        if player_name:
            print(f"✅ تم العثور على اللاعب: {player_name}")
        else:
            print("❌ لم يتم العثور على اللاعب")
    else:
        print("❌ لم يتم إدخال معرف اللاعب")
