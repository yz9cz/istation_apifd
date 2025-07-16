#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BigOLive Player Name Lookup - High Performance Version
وحدة البحث عن أسماء لاعبي BigOLive - نسخة عالية الأداء
"""

import asyncio
from typing import Optional
from connection_pool import get_connection_pool, GameType

def get_bigolive_player_name(player_id: str) -> Optional[dict]:
    """
    جلب بيانات لاعب BigOLive من API livesbuy.com - يعيد الاستجابة الخام
    API: https://www.livesbuy.com/account/match/ajax/info

    Args:
        player_id (str): معرف اللاعب (account)

    Returns:
        dict: الاستجابة الخام من الـ API أو رسالة خطأ
    """
    try:
        # تشغيل النسخة غير المتزامنة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(get_bigolive_player_name_async(player_id))
            # إرجاع الاستجابة الخام كما هي
            return result
        finally:
            loop.close()
    except Exception as e:
        return {"error": str(e), "success": False}

def get_bigolive_player_info(player_id: str) -> Optional[dict]:
    """
    جلب معلومات كاملة عن لاعب BigOLive (اسم، صورة، إلخ)
    
    Args:
        player_id (str): معرف اللاعب
    
    Returns:
        dict or None: معلومات اللاعب الكاملة أو None إذا لم يوجد
    """
    try:
        url = "https://www.livesbuy.com/account/match/ajax/info"
        
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ar,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.livesbuy.com',
            'Referer': 'https://www.livesbuy.com/?-affi-80966',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        cookies = {
            '_fbp': 'fb.1.1751407227617.74407595214113550',
            '_ga': 'GA1.1.2107163118.1751407228',
            'g_state': '{"i_l":0}',
            'unique-code': 'CIEbdL7p5LhNO6wWOLdcMixHPOC98mqj',
            'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE': 'en-US',
            'SESSION': 'MzY1OGNkZWMtMzkxNy00MzRiLWFmMzMtNGNmN2FhM2Q3NzVj',
            '_ga_WDZLJ8TZBT': 'GS2.1.s1752525915$o2$g1$t1752526377$j52$l0$h0'
        }
        
        payload = {
            'productId': '9796',
            'account': str(player_id).strip()
        }
        
        response = requests.post(url, headers=headers, cookies=cookies, data=payload, timeout=15)
        
        if response.status_code != 200:
            return None
        
        result = response.json()
        
        if not result.get('success', False):
            return None
        
        data = result.get('data', {})
        if not data.get('matched', False) or not data.get('exists', False):
            return None
        
        return {
            'account': data.get('account'),
            'nickname': data.get('nickname'),
            'avatar': data.get('avatar'),
            'matched': data.get('matched'),
            'exists': data.get('exists')
        }
    
    except Exception as e:
        print(f"Error in get_bigolive_player_info for player {player_id}: {e}")
        return None

async def get_bigolive_player_name_async(player_id: str) -> Optional[dict]:
    """
    جلب بيانات لاعب BigOLive من API livesbuy.com - نسخة غير متزامنة تعيد الاستجابة الخام
    API: https://www.livesbuy.com/account/match/ajax/info

    Args:
        player_id (str): معرف اللاعب (account)

    Returns:
        dict: الاستجابة الخام من الـ API أو رسالة خطأ
    """
    try:
        pool = await get_connection_pool()

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ar,en;q=0.9',
            'Origin': 'https://www.livesbuy.com',
            'Referer': 'https://www.livesbuy.com/?-affi-80966',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'priority': 'u=1, i'
        }

        cookies = {
            '_fbp': 'fb.1.1751407227617.74407595214113550',
            '_ga': 'GA1.1.2107163118.1751407228',
            'g_state': '{"i_l":0}',
            'unique-code': 'CIEbdL7p5LhNO6wWOLdcMixHPOC98mqj',
            'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE': 'en-US',
            'SESSION': 'MzY1OGNkZWMtMzkxNy00MzRiLWFmMzMtNGNmN2FhM2Q3NzVj',
            '_ga_WDZLJ8TZBT': 'GS2.1.s1752525915$o2$g1$t1752526377$j52$l0$h0'
        }

        payload = {
            'productId': '9796',
            'account': str(player_id).strip()
        }

        result = await pool.make_request(
            game_type=GameType.BIGOLIVE,
            url="https://www.livesbuy.com/account/match/ajax/info",
            method='POST',
            data=payload,
            headers=headers,
            cookies=cookies
        )

        # إرجاع الرد الكامل بدلاً من معالجته
        return result

    except Exception as e:
        return {"error": str(e), "success": False}

if __name__ == "__main__":
    # اختبار الوحدة
    print("🎮 اختبار وحدة البحث عن لاعبي BigOLive")
    print("=" * 50)
    
    test_player_id = input("أدخل معرف لاعب BigOLive للاختبار: ").strip()
    if test_player_id:
        print(f"🔍 البحث عن اللاعب: {test_player_id}")
        
        # الحصول على الرد الكامل من API
        import json
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(get_bigolive_player_name_async(test_player_id))
            # طباعة الرد الكامل بصيغة JSON
            print(json.dumps(result, ensure_ascii=False, indent=2))
        finally:
            loop.close()
    else:
        print("❌ لم يتم إدخال معرف اللاعب")
