#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iStation API Runner Script
سكريبت تشغيل مشروع iStation API
"""

import sys
import os
import argparse
import subprocess
import signal
import time
from pathlib import Path

def check_requirements():
    """التحقق من وجود المتطلبات"""
    try:
        import fastapi
        import uvicorn
        import aiohttp
        return True
    except ImportError as e:
        print(f"❌ مكتبة مفقودة: {e}")
        print("يرجى تشغيل: python install.py")
        return False

def check_playwright():
    """التحقق من Playwright"""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        print("⚠️ Playwright غير مثبت - PUBG قد لا يعمل")
        return False

def run_server(host="0.0.0.0", port=8001, workers=1, reload=False):
    """تشغيل الخادم"""
    print("🚀 بدء تشغيل iStation API Server...")
    print("=" * 50)
    
    # التحقق من المتطلبات
    if not check_requirements():
        sys.exit(1)
    
    # التحقق من Playwright
    check_playwright()
    
    # إعداد الأوامر
    cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", host,
        "--port", str(port),
        "--workers", str(workers),
        "--loop", "asyncio",
        "--http", "httptools",
        "--ws", "websockets",
        "--lifespan", "on",
        "--no-access-log",
        "--no-server-header",
        "--no-date-header",
        "--limit-concurrency", "50",
        "--limit-max-requests", "10000",
        "--timeout-keep-alive", "5",
        "--timeout-graceful-shutdown", "30"
    ]
    
    if reload:
        cmd.append("--reload")
    
    print(f"🌐 الخادم: http://{host}:{port}")
    print(f"📚 الوثائق: http://{host}:{port}/docs")
    print(f"🔧 العمال: {workers}")
    print(f"🔄 إعادة التحميل: {'مفعل' if reload else 'معطل'}")
    print("=" * 50)
    
    try:
        # تشغيل الخادم
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف الخادم بواسطة المستخدم")
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تشغيل الخادم: {e}")
        sys.exit(1)

def run_tests():
    """تشغيل الاختبارات"""
    print("🧪 تشغيل الاختبارات...")
    
    try:
        import pytest
        result = subprocess.run([sys.executable, "-m", "pytest", "-v"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except ImportError:
        print("❌ pytest غير مثبت")
        return False

def show_status():
    """عرض حالة النظام"""
    print("📊 حالة النظام:")
    print("=" * 30)
    
    # Python version
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # المكتبات المطلوبة
    libraries = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("aiohttp", "aiohttp"),
        ("Playwright", "playwright"),
        ("Pydantic", "pydantic"),
        ("Flask", "flask")
    ]
    
    for name, module in libraries:
        try:
            __import__(module)
            print(f"✅ {name}: مثبت")
        except ImportError:
            print(f"❌ {name}: غير مثبت")
    
    # ملفات المشروع
    files = ["main.py", "requirements.txt", "pubg_player.py", 
             "freefire_player.py", "jawaker_player.py"]
    
    print("\n📁 ملفات المشروع:")
    for file in files:
        if os.path.exists(file):
            print(f"✅ {file}: موجود")
        else:
            print(f"❌ {file}: مفقود")

def main():
    """الدالة الرئيسية"""
    parser = argparse.ArgumentParser(description="iStation API Runner")
    
    subparsers = parser.add_subparsers(dest="command", help="الأوامر المتاحة")
    
    # أمر التشغيل
    run_parser = subparsers.add_parser("run", help="تشغيل الخادم")
    run_parser.add_argument("--host", default="0.0.0.0", help="عنوان الخادم")
    run_parser.add_argument("--port", type=int, default=8001, help="منفذ الخادم")
    run_parser.add_argument("--workers", type=int, default=1, help="عدد العمال")
    run_parser.add_argument("--reload", action="store_true", help="إعادة التحميل التلقائي")
    
    # أمر الاختبار
    subparsers.add_parser("test", help="تشغيل الاختبارات")
    
    # أمر الحالة
    subparsers.add_parser("status", help="عرض حالة النظام")
    
    # أمر التثبيت
    subparsers.add_parser("install", help="تثبيت المتطلبات")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_server(args.host, args.port, args.workers, args.reload)
    elif args.command == "test":
        success = run_tests()
        sys.exit(0 if success else 1)
    elif args.command == "status":
        show_status()
    elif args.command == "install":
        subprocess.run([sys.executable, "install.py"])
    else:
        # تشغيل افتراضي
        run_server()

if __name__ == "__main__":
    main()
