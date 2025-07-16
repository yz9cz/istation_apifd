#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poppo Live Player Name Lookup - High Performance Version
وحدة البحث عن أسماء لاعبي Poppo Live - نسخة عالية الأداء
"""

import asyncio
from typing import Optional
from connection_pool import get_connection_pool, GameType

def get_poppolive_player_name(player_id: str) -> Optional[dict]:
    """
    جلب بيانات لاعب Poppo Live من API livesbuy.com - يعيد الاستجابة الخام
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
            result = loop.run_until_complete(get_poppolive_player_name_async(player_id))
            # إرجاع الاستجابة الخام كما هي
            return result
        finally:
            loop.close()
    except Exception as e:
        return {"error": str(e), "success": False}


def get_poppolive_player_info(player_id: str) -> Optional[dict]:
    """
    جلب معلومات لاعب Poppo Live الكاملة من API livesbuy.com
    
    Args:
        player_id (str): معرف اللاعب (account)
    
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
            'Priority': 'u=1, i',
            'Referer': 'https://www.livesbuy.com/poppo?-affi-80967',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        # إعداد Cookies الأساسية
        cookies = {
            '_fbp': 'fb.1.1751407227617.74407595214113550',
            '_ga': 'GA1.1.2107163118.1751407228',
            'g_state': '{"i_l":0}',
            'unique-code': 'CIEbdL7p5LhNO6wWOLdcMixHPOC98mqj',
            'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE': 'en-US',
            'SESSION': 'MzY1OGNkZWMtMzkxNy00MzRiLWFmMzMtNGNmN2FhM2Q3NzVj',
            '_ga_WDZLJ8TZBT': 'GS2.1.s1752525915$o2$g1$t1752526943$j52$l0$h0'
        }
        
        # إعداد البيانات - productId=11454 هو معرف Poppo Live
        payload = {
            'productId': '11454',
            'account': str(player_id).strip()
        }
        
        # إرسال الطلب POST
        response = requests.post(
            url, 
            headers=headers, 
            cookies=cookies,
            data=payload, 
            timeout=15
        )
        
        if response.status_code != 200:
            return None
        
        # تحليل الاستجابة JSON
        data = response.json()
        
        # التحقق من نجاح الطلب
        if not data.get('success', False):
            return None
        
        # إرجاع بيانات اللاعب الكاملة
        return data.get('data')
        
    except Exception as e:
        print(f"Error in get_poppolive_player_info: {e}")
        return None


async def get_poppolive_player_name_async(player_id: str) -> Optional[dict]:
    """
    جلب بيانات لاعب Poppo Live من API livesbuy.com - نسخة غير متزامنة تعيد الاستجابة الخام
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
            'Priority': 'u=1, i',
            'Referer': 'https://www.livesbuy.com/poppo?-affi-80967',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        }

        cookies = {
            '_fbp': 'fb.1.1751407227617.74407595214113550',
            '_ga': 'GA1.1.2107163118.1751407228',
            'g_state': '{"i_l":0}',
            'unique-code': 'CIEbdL7p5LhNO6wWOLdcMixHPOC98mqj',
            'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE': 'en-US',
            'SESSION': 'MzY1OGNkZWMtMzkxNy00MzRiLWFmMzMtNGNmN2FhM2Q3NzVj',
            '_ga_WDZLJ8TZBT': 'GS2.1.s1752525915$o2$g1$t1752526943$j52$l0$h0'
        }

        payload = {
            'productId': '11454',
            'account': str(player_id).strip()
        }

        result = await pool.make_request(
            game_type=GameType.POPPOLIVE,
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
    test_player_id = input("أدخل معرف لاعب Poppo Live للاختبار: ")
    if test_player_id:
        print(f"البحث عن اللاعب: {test_player_id}")
        
        # البحث عن اللاعب
        player_name = get_poppolive_player_name(test_player_id)
        if player_name:
            print(f"✅ تم العثور على اللاعب: {player_name}")
            
            # جلب المعلومات الكاملة
            player_info = get_poppolive_player_info(test_player_id)
            if player_info:
                print(f"📋 معلومات اللاعب الكاملة:")
                print(f"   - الاسم: {player_info.get('nickname')}")
                print(f"   - المعرف: {player_info.get('account')}")
                print(f"   - الصورة الرمزية: {player_info.get('avatar')}")
                print(f"   - موجود: {player_info.get('exists')}")
                print(f"   - مطابق: {player_info.get('matched')}")
        else:
            print("❌ لم يتم العثور على اللاعب")
    else:
        print("❌ لم يتم إدخال معرف اللاعب")
