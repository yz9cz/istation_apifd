#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iStation API Installation Script
سكريبت تثبيت مشروع iStation API
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """تشغيل أمر مع عرض الوصف"""
    print(f"\n🔄 {description}...")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} - تم بنجاح!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - فشل!")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """التحقق من إصدار Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 أو أحدث مطلوب!")
        print(f"الإصدار الحالي: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - متوافق!")
    return True

def install_requirements():
    """تثبيت متطلبات Python"""
    if not os.path.exists("requirements.txt"):
        print("❌ ملف requirements.txt غير موجود!")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "تثبيت متطلبات Python"
    )

def install_playwright():
    """تثبيت متصفحات Playwright"""
    success = run_command(
        f"{sys.executable} -m playwright install chromium",
        "تثبيت متصفح Chromium للـ Playwright"
    )
    
    if success:
        # تثبيت dependencies إضافية للنظام
        system = platform.system().lower()
        if system == "linux":
            run_command(
                f"{sys.executable} -m playwright install-deps chromium",
                "تثبيت dependencies النظام للـ Playwright"
            )
    
    return success

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    directories = ["logs", "temp"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ تم إنشاء مجلد: {directory}")

def test_installation():
    """اختبار التثبيت"""
    print("\n🧪 اختبار التثبيت...")
    
    # اختبار استيراد المكتبات الأساسية
    try:
        import fastapi
        import uvicorn
        import aiohttp
        import playwright
        print("✅ جميع المكتبات الأساسية متوفرة!")
        
        # اختبار Playwright
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        print("✅ Playwright يعمل بشكل صحيح!")
        
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد المكتبة: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار Playwright: {e}")
        return False

def main():
    """الدالة الرئيسية للتثبيت"""
    print("🚀 iStation API - سكريبت التثبيت")
    print("=" * 50)
    
    # التحقق من إصدار Python
    if not check_python_version():
        sys.exit(1)
    
    # إنشاء المجلدات
    create_directories()
    
    # تثبيت متطلبات Python
    if not install_requirements():
        print("❌ فشل في تثبيت متطلبات Python!")
        sys.exit(1)
    
    # تثبيت Playwright
    if not install_playwright():
        print("❌ فشل في تثبيت Playwright!")
        print("⚠️ يمكنك المتابعة، لكن PUBG قد لا يعمل بشكل صحيح")
    
    # اختبار التثبيت
    if test_installation():
        print("\n🎉 تم التثبيت بنجاح!")
        print("\n📋 الخطوات التالية:")
        print("1. تشغيل الخادم: python main.py")
        print("2. فتح المتصفح: http://localhost:8001")
        print("3. الوثائق: http://localhost:8001/docs")
    else:
        print("\n❌ فشل في اختبار التثبيت!")
        print("يرجى التحقق من الأخطاء أعلاه وإعادة المحاولة")
        sys.exit(1)

if __name__ == "__main__":
    main()
