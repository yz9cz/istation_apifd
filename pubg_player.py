#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra-Fast Local PUBG Player Lookup - Maximum Performance
نظام البحث عن اللاعبين في PUBG Mobile - محلي
- متصفحات متوازية
- معالجة سريعة
- إشعارات فورية
- كوكيز محسنة لموقع MidasBuy
- Local execution without Apify dependencies
"""

import asyncio
import time
import logging
import re
import uuid
from typing import Dict, Optional, List
from enum import Enum
from dataclasses import dataclass
from flask import Flask, jsonify
from flask_cors import CORS

# تعطيل السجلات للحصول على أقصى أداء
logging.disable(logging.CRITICAL)

# التحقق من المكتبات المطلوبة
try:
    from playwright.async_api import async_playwright, Route, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("❌ Playwright not installed. Install with: pip install playwright")
    print("   Then run: playwright install chromium")

# ===== فئات البيانات =====

class BrowserState(Enum):
    """حالات المتصفح"""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    CLOSED = "closed"

@dataclass
class BrowserInstance:
    """معلومات المتصفح"""
    id: str
    browser: Optional[Browser] = None
    page: Optional[Page] = None
    context: Optional[BrowserContext] = None
    state: BrowserState = BrowserState.INITIALIZING
    current_request_id: Optional[str] = None
    error_count: int = 0
    last_used: float = 0

def get_midasbuy_cookies():
    """إرجاع الكوكيز المطلوبة لموقع MidasBuy"""
    return [
        {"name": "select_country", "value": "us", "domain": "www.midasbuy.com", "path": "/"},
        {"name": "_gcl_au", "value": "1.1.1598822159.1751108744", "domain": ".midasbuy.com", "path": "/"},
        {"name": "_gid", "value": "GA1.2.1002167869.1752608763", "domain": ".midasbuy.com", "path": "/"},
        {"name": "country", "value": "ro", "domain": "www.midasbuy.com", "path": "/"},
        {"name": "accumrecharge_activity_landing_pop", "value": "1", "domain": ".www.midasbuy.com", "path": "/"},
        {"name": "cookie_control", "value": "1|1", "domain": "www.midasbuy.com", "path": "/"},
        {"name": "_ga_PNR34BM5B9", "value": "GS2.2.s1752681424$o9$g1$t1752681460$j24$l0$h0", "domain": ".midasbuy.com", "path": "/"},
        {"name": "_ga_NQX2JD8STG", "value": "GS2.1.s1752681417$o10$g1$t1752681459$j18$l0$h0", "domain": ".midasbuy.com", "path": "/"},
        {"name": "_ga", "value": "GA1.1.289487780.1751108741", "domain": ".midasbuy.com", "path": "/"},
        {"name": "midasbuyDeviceId", "value": "0098360757300322231751108577150", "domain": "www.midasbuy.com", "path": "/"},
        {"name": "select_cookie", "value": "1", "domain": "www.midasbuy.com", "path": "/"},
        {"name": "shopcode", "value": "midasbuy", "domain": "www.midasbuy.com", "path": "/"},
        {"name": "tencent_tdrc", "value": "SCDNL5nAbR3DsKQO4lftriQFCetqQTRUNu", "domain": "www.midasbuy.com", "path": "/"},
        {"name": "UUID", "value": "0970548902092409175226337639577889", "domain": "www.midasbuy.com", "path": "/"}
    ]

@dataclass
class PlayerRequest:
    """طلب البحث عن لاعب"""
    id: str
    player_id: str
    timestamp: float
    future: Optional[asyncio.Future] = None
    callback: Optional[callable] = None

# ===== فلتر المحتوى =====

class SuperFastFilter:
    """فلتر محتوى سريع"""

    def __init__(self):
        self.blocked_domains = {
            'google-analytics.com', 'googletagmanager.com', 'doubleclick.net',
            'facebook.com', 'facebook.net', 'connect.facebook.net',
            'twitter.com', 'ads-twitter.com', 'googlesyndication.com',
            'hotjar.com', 'mixpanel.com', 'segment.com'
        }
        
        self.patterns = [
            re.compile(r'.*analytics.*', re.IGNORECASE),
            re.compile(r'.*tracking.*', re.IGNORECASE),
            re.compile(r'.*ads.*', re.IGNORECASE)
        ]
        
        self.blocked_media_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            '.webp', '.svg', '.ico', '.avif', '.heic', '.heif',
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv',
            '.m4v', '.3gp', '.ogv', '.ts', '.m3u8',
            '.mp3', '.wav', '.ogg', '.aac', '.flac', '.wma', '.m4a',
            '.woff', '.woff2', '.ttf', '.otf', '.eot',
            '.pdf', '.zip', '.rar', '.exe', '.dmg', '.pkg'
        }
        
        self.blocked_resource_types = {
            'image', 'media', 'font', 'other'
        }
        
        self.stats = {'blocked': 0, 'allowed': 0, 'blocked_media': 0, 'blocked_tracking': 0}

    def should_block(self, url: str, resource_type: str = None) -> bool:
        """تحديد ما إذا كان يجب حجب الطلب"""
        url_lower = url.lower()
        
        if resource_type in self.blocked_resource_types:
            self.stats['blocked_media'] += 1
            self.stats['blocked'] += 1
            return True
        
        for domain in self.blocked_domains:
            if domain in url_lower:
                self.stats['blocked_tracking'] += 1
                self.stats['blocked'] += 1
                return True
        
        for pattern in self.patterns:
            if pattern.search(url_lower):
                self.stats['blocked_tracking'] += 1
                self.stats['blocked'] += 1
                return True
        
        if '.' in url_lower:
            file_extension = '.' + url_lower.split('.')[-1].split('?')[0]
            if file_extension in self.blocked_media_extensions:
                self.stats['blocked_media'] += 1
                self.stats['blocked'] += 1
                return True
        
        self.stats['allowed'] += 1
        return False

# ===== مدير المتصفحات =====

class BrowserManager:
    """مدير المتصفحات المتوازية - 3 متصفحات مستقلة"""
    
    def __init__(self, browser_count: int = 3, headless: bool = False):
        self.browser_count = browser_count
        self.headless = headless
        self.browsers: List[BrowserInstance] = []
        self.playwright = None
        self.filter = SuperFastFilter()
        self._closed = False
        self._setup_lock = asyncio.Lock()
        
        if headless:
            print("🔧 تشغيل المتصفحات في الوضع الخفي (headless)")
        else:
            print("👁️ تشغيل المتصفحات مع الواجهة المرئية")
        
    async def initialize(self):
        """تهيئة جميع المتصفحات"""
        if self._closed:
            return False
            
        try:
            self.playwright = await async_playwright().start()
            
            for i in range(self.browser_count):
                browser_id = f"browser_{i+1}"
                browser_instance = BrowserInstance(id=browser_id)
                self.browsers.append(browser_instance)
                await self._setup_browser(browser_instance)
                
            return True
            
        except Exception as e:
            print(f"❌ فشل في تهيئة المتصفحات: {e}")
            await self.cleanup()
            return False

    async def _setup_browser(self, browser_instance: BrowserInstance):
        """تهيئة متصفح واحد"""
        try:
            browser_instance.state = BrowserState.INITIALIZING

            # Browser args optimized for both headless and non-headless modes
            # كل متصفح له معرف فريد لضمان الاستقلالية التامة
            browser_args = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-extensions',
                '--disable-plugins',
                '--aggressive-cache-discard',
                '--memory-pressure-off',
                '--max_old_space_size=4096',
                f'--user-data-dir=/tmp/chrome-{browser_instance.id}',  # مجلد منفصل لكل متصفح
                f'--profile-directory=Profile-{browser_instance.id}',   # ملف تعريف منفصل
                '--disable-shared-workers',                             # تعطيل العمال المشتركين
                '--disable-session-crashed-bubble',                     # تعطيل رسائل الأعطال المشتركة
                '--disable-background-mode'                             # تعطيل الوضع الخلفي المشترك
            ]

            # Add headless-specific optimizations only in headless mode
            if self.headless:
                browser_args.extend([
                    '--disable-gpu',
                    '--disable-images',
                    '--disable-javascript-harmony-shipping',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-default-apps',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-sync',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-background-networking'
                ])

            # إنشاء متصفح مستقل تماماً مع معرف فريد
            browser_instance.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=browser_args
            )

            # إنشاء context مستقل لكل متصفح مع إعدادات منفصلة
            browser_instance.context = await browser_instance.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent=f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Browser-{browser_instance.id}',
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True
            )

            # إضافة الكوكيز المطلوبة لموقع MidasBuy
            cookies = get_midasbuy_cookies()
            await browser_instance.context.add_cookies(cookies)

            browser_instance.page = await browser_instance.context.new_page()
            await browser_instance.page.route("**/*", lambda route: self._handle_request(route))

            await browser_instance.page.add_init_script("""
                window.addEventListener('DOMContentLoaded', function() {
                    const style = document.createElement('style');
                    style.textContent = `
                        *, *::before, *::after {
                            animation-duration: 0.01ms !important;
                            transition-duration: 0.01ms !important;
                        }
                        .PopGetPoints_pop_bg__w92N9,
                        .PopGetPoints_getPoints_pop__LVJvS.PopGetPoints_active__xuX7w {
                            display: none !important;
                        }
                    `;
                    document.head.appendChild(style);
                });
            """)

            await self._prepare_browser(browser_instance)

        except Exception as e:
            print(f"❌ فشل في تهيئة المتصفح {browser_instance.id}: {e}")
            browser_instance.state = BrowserState.ERROR
            browser_instance.error_count += 1

    async def _prepare_browser(self, browser_instance: BrowserInstance):
        """تجهيز المتصفح للاستخدام"""
        try:
            # التأكد من وجود الكوكيز المطلوبة
            current_cookies = await browser_instance.context.cookies()
            cookie_names = [cookie['name'] for cookie in current_cookies]

            # إضافة الكوكيز إذا لم تكن موجودة
            if 'select_country' not in cookie_names or 'midasbuyDeviceId' not in cookie_names:
                cookies = get_midasbuy_cookies()
                await browser_instance.context.add_cookies(cookies)
                print(f"🍪 تم إضافة الكوكيز للمتصفح {browser_instance.id}")

            await browser_instance.page.goto(
                "https://www.midasbuy.com/midasbuy/us/redeem/pubgm",
                wait_until="domcontentloaded", timeout=30000
            )

            selectors = [
                ".UserTabBox_use_tab_box__otkPd.UserTabBox_not_logined_box__m0w1t",
                ".UserTabBox_use_tab_box__otkPd",
                "[class*='UserTabBox_use_tab_box']"
            ]

            for selector in selectors:
                try:
                    await browser_instance.page.wait_for_selector(selector, timeout=15000)
                    await browser_instance.page.click(selector)
                    break
                except:
                    continue
            else:
                raise Exception("فشل في اختيار المنطقة")

            browser_instance.state = BrowserState.READY
            browser_instance.last_used = time.time()
            print(f"✅ المتصفح {browser_instance.id} جاهز للاستخدام")

        except Exception as e:
            print(f"❌ فشل في تجهيز المتصفح {browser_instance.id}: {e}")
            browser_instance.state = BrowserState.ERROR
            browser_instance.error_count += 1

    async def _handle_request(self, route: Route):
        """معالج الطلبات مع فلترة المحتوى"""
        if self._closed:
            return

        try:
            request = route.request
            if self.filter.should_block(request.url, request.resource_type):
                await route.abort()
            else:
                await route.continue_()
        except:
            try:
                if not self._closed:
                    await route.continue_()
            except:
                pass

    async def get_available_browser(self) -> Optional[BrowserInstance]:
        """الحصول على متصفح متاح"""
        for browser in self.browsers:
            if browser.state == BrowserState.READY:
                return browser
        return None

    async def wait_for_available_browser(self) -> Optional[BrowserInstance]:
        """انتظار متصفح متاح مع إعادة المحاولة"""
        wait_start = time.time()
        last_status_time = 0

        while not self._closed:
            browser = await self.get_available_browser()
            if browser:
                wait_time = time.time() - wait_start
                if wait_time > 1:
                    print(f"✅ تم العثور على متصفح متاح: {browser.id} (انتظار: {wait_time:.1f}ث)")
                return browser

            current_time = time.time()
            if current_time - last_status_time > 5:
                wait_time = current_time - wait_start
                status = await self.get_status()
                print(f"⏳ انتظار متصفح متاح... ({wait_time:.0f}ث) - جاهز: {status['ready']}, مشغول: {status['busy']}")
                last_status_time = current_time

            await asyncio.sleep(0.1)

        return None

    async def process_request(self, player_id: str, request_id: str = None, callback=None) -> dict:
        """معالجة طلب البحث عن لاعب"""
        if request_id is None:
            request_id = str(uuid.uuid4())

        browser = await self.wait_for_available_browser()
        if not browser:
            return {'success': False, 'error': 'تم إيقاف النظام', 'request_id': request_id, 'player_id': player_id}

        browser.state = BrowserState.BUSY
        browser.current_request_id = request_id
        browser.last_used = time.time()

        try:
            result = await self._perform_lookup(browser, player_id, request_id, callback)
            asyncio.create_task(self._reset_browser_immediate(browser))
            return result

        except Exception as e:
            print(f"❌ خطأ في معالجة الطلب {request_id}: {e}")
            browser.state = BrowserState.ERROR
            browser.error_count += 1
            await self._setup_browser(browser)
            return {'success': False, 'error': str(e), 'request_id': request_id, 'player_id': player_id, 'browser_id': browser.id}

    async def _perform_lookup(self, browser: BrowserInstance, player_id: str, request_id: str, callback=None) -> dict:
        """تنفيذ البحث الفعلي"""
        try:
            # إدخال معرف اللاعب
            input_selectors = [
                ".SelectServerBox_input_wrap_box__qq\\+Iq input",
                "[class*='SelectServerBox_input_wrap_box'] input",
                "input[type='text']"
            ]

            for selector in input_selectors:
                try:
                    await browser.page.wait_for_selector(selector, timeout=15000)
                    await browser.page.fill(selector, player_id)
                    break
                except:
                    continue
            else:
                return {'success': False, 'error': 'لم يتم العثور على حقل الإدخال', 'request_id': request_id, 'player_id': player_id, 'browser_id': browser.id}

            # الضغط على زر التحقق
            verify_selector = "xpath=/html/body/div[2]/div/div[5]/div[2]/div[1]/div[3]"
            await browser.page.wait_for_selector(verify_selector, timeout=15000, state="visible")
            await browser.page.click(verify_selector)

            # استخراج اسم اللاعب
            def instant_callback(data):
                print(f"🚀 إشعار فوري: تم العثور على {data['player_name']} في {data['execution_time']:.2f}ث!")
                if callback:
                    callback(data)

            player_name = await self._extract_player_name_smart(browser, player_id, request_id, instant_callback)

            if player_name:
                return {
                    'success': True, 'player_id': player_id, 'player_name': player_name,
                    'request_id': request_id, 'browser_id': browser.id,
                    'method': 'unified_system_instant',
                    'note': 'النتيجة مرسلة فوراً - إعادة تجهيز المتصفح في الخلفية'
                }
            else:
                return {'success': False, 'player_id': player_id, 'error': 'معرف اللاعب غير صحيح - لم يتم العثور على اللاعب', 'request_id': request_id, 'browser_id': browser.id}

        except Exception as e:
            return {'success': False, 'player_id': player_id, 'error': f'فشل في استخراج الاسم: {e}', 'request_id': request_id, 'browser_id': browser.id}

    async def _extract_player_name_smart(self, browser: BrowserInstance, player_id: str, request_id: str, callback=None) -> Optional[str]:
        """استخراج اسم اللاعب بطريقة ذكية"""

        # XPath المحدد أولاً
        specific_xpath = "/html/body/div[2]/div/div[2]/div[2]/div/div[2]/div[2]/div/div/div[1]/div/span[1]"

        try:
            # محاولة فورية
            element = await browser.page.query_selector(f"xpath={specific_xpath}")
            if element:
                text = await element.text_content()
                if text and len(text.strip()) > 1:
                    execution_time = time.time() - browser.last_used
                    print(f"✅ تم العثور على الاسم: {text.strip()} (XPath مباشر) - وقت التنفيذ: {execution_time:.2f}ث")
                    if callback:
                        callback({'type': 'player_found', 'player_name': text.strip(), 'player_id': player_id, 'request_id': request_id, 'browser_id': browser.id, 'method': 'xpath_direct', 'execution_time': execution_time})
                    return text.strip()

            # polling سريع
            for _ in range(30):
                await asyncio.sleep(0.1)
                element = await browser.page.query_selector(f"xpath={specific_xpath}")
                if element:
                    text = await element.text_content()
                    if text and len(text.strip()) > 1:
                        execution_time = time.time() - browser.last_used
                        print(f"✅ تم العثور على الاسم: {text.strip()} (XPath polling) - وقت التنفيذ: {execution_time:.2f}ث")
                        if callback:
                            callback({'type': 'player_found', 'player_name': text.strip(), 'player_id': player_id, 'request_id': request_id, 'browser_id': browser.id, 'method': 'xpath_polling', 'execution_time': execution_time})
                        return text.strip()

            return None

        except Exception:
            return None

    async def _reset_browser_immediate(self, browser: BrowserInstance):
        """إعادة تجهيز المتصفح فوراً"""
        try:
            print(f"🔄 إعادة تجهيز المتصفح {browser.id} في الخلفية...")
            browser.current_request_id = None
            await browser.context.clear_cookies()

            # إعادة إضافة الكوكيز المطلوبة لموقع MidasBuy
            cookies = get_midasbuy_cookies()
            await browser.context.add_cookies(cookies)

            await browser.page.evaluate("""
                () => {
                    try {
                        localStorage.clear();
                        sessionStorage.clear();
                    } catch (e) {
                        console.log('Storage clear failed:', e);
                    }
                }
            """)

            await browser.page.reload(wait_until="domcontentloaded", timeout=30000)
            await self._prepare_browser(browser)
            print(f"✅ تم إعادة تجهيز المتصفح {browser.id} وهو جاهز للطلب التالي")

        except Exception as e:
            print(f"❌ فشل في إعادة تجهيز المتصفح {browser.id}: {e}")
            browser.state = BrowserState.ERROR
            browser.error_count += 1
            await self._setup_browser(browser)

    async def get_status(self) -> dict:
        """الحصول على حالة جميع المتصفحات"""
        status = {'total_browsers': len(self.browsers), 'ready': 0, 'busy': 0, 'error': 0, 'initializing': 0, 'browsers': []}

        for browser in self.browsers:
            status['browsers'].append({
                'id': browser.id, 'state': browser.state.value,
                'current_request': browser.current_request_id,
                'error_count': browser.error_count, 'last_used': browser.last_used
            })

            if browser.state == BrowserState.READY:
                status['ready'] += 1
            elif browser.state == BrowserState.BUSY:
                status['busy'] += 1
            elif browser.state == BrowserState.ERROR:
                status['error'] += 1
            elif browser.state == BrowserState.INITIALIZING:
                status['initializing'] += 1

        return status

    async def cleanup(self):
        """تنظيف جميع المتصفحات"""
        if self._closed:
            return

        self._closed = True

        for browser in self.browsers:
            try:
                if browser.page and not browser.page.is_closed():
                    await browser.page.unroute("**/*")
                    await browser.page.close()
                if browser.context:
                    await browser.context.close()
                if browser.browser:
                    await browser.browser.close()
            except:
                pass

        try:
            if self.playwright:
                await self.playwright.stop()
        except:
            pass

        self.browsers.clear()

# ===== قائمة الطلبات =====

class RequestQueue:
    """قائمة انتظار الطلبات مع التوزيع التلقائي على المتصفحات"""

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
        self.pending_requests: asyncio.Queue = asyncio.Queue()
        self.active_requests: Dict[str, PlayerRequest] = {}
        self._processor_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """بدء معالج الطلبات"""
        if self._running:
            return

        self._running = True
        self._processor_task = asyncio.create_task(self._process_requests())
        print("✅ معالج الطلبات بدأ العمل")

    async def stop(self):
        """إيقاف معالج الطلبات"""
        self._running = False

        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass

        while not self.pending_requests.empty():
            try:
                request = self.pending_requests.get_nowait()
                if request.future and not request.future.done():
                    request.future.set_exception(Exception("تم إيقاف الخدمة"))
            except asyncio.QueueEmpty:
                break

        for request in self.active_requests.values():
            if request.future and not request.future.done():
                request.future.set_exception(Exception("تم إيقاف الخدمة"))

        self.active_requests.clear()
        print("✅ تم إيقاف معالج الطلبات")

    async def submit_request(self, player_id: str) -> dict:
        """إرسال طلب جديد للبحث عن لاعب مع بدء فوري"""
        if not self._running:
            return {'success': False, 'error': 'الخدمة غير متاحة', 'player_id': player_id}

        request_id = str(uuid.uuid4())
        future = asyncio.Future()

        def instant_notification(data):
            print(f"⚡ إشعار فوري: تم العثور على {data['player_name']} في {data['execution_time']:.2f}ث!")

        request = PlayerRequest(id=request_id, player_id=player_id, timestamp=time.time(), future=future, callback=instant_notification)

        print(f"📝 طلب جديد: {request_id} للاعب: {player_id}")
        print(f"🚀 بدء المعالجة فوراً...")

        await self.pending_requests.put(request)
        self.active_requests[request_id] = request

        queue_size = self.pending_requests.qsize()
        if queue_size > 1:
            print(f"⏳ الطلب في قائمة الانتظار - الموضع: {queue_size}")

        try:
            result = await future
            return result
        except Exception as e:
            return {'success': False, 'error': str(e), 'player_id': player_id, 'request_id': request_id}
        finally:
            self.active_requests.pop(request_id, None)

    async def _process_requests(self):
        """معالج الطلبات الرئيسي"""
        print("🔄 بدء معالجة الطلبات...")

        while self._running:
            try:
                request = await asyncio.wait_for(self.pending_requests.get(), timeout=1.0)
                asyncio.create_task(self._handle_request(request))
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ خطأ في معالج الطلبات: {e}")
                await asyncio.sleep(0.1)

    async def _handle_request(self, request: PlayerRequest):
        """معالجة طلب واحد مع إشعارات فورية"""
        try:
            print(f"🔍 بدء معالجة الطلب: {request.id} للاعب: {request.player_id}")

            result = await self.browser_manager.process_request(request.player_id, request.id, request.callback)

            if request.future and not request.future.done():
                request.future.set_result(result)

            if result.get('success'):
                print(f"✅ تم العثور على اللاعب: {result.get('player_name')} (ID: {request.player_id})")
                print(f"🚀 النتيجة مرسلة فوراً - المتصفح {result.get('browser_id')} يعاد تجهيزه في الخلفية")
            else:
                print(f"❌ فشل البحث عن اللاعب: {request.player_id} - {result.get('error')}")
                print(f"🔄 المتصفح {result.get('browser_id')} يعاد تجهيزه في الخلفية")

        except Exception as e:
            print(f"❌ خطأ في معالجة الطلب {request.id}: {e}")
            if request.future and not request.future.done():
                request.future.set_exception(e)

    def get_queue_status(self) -> dict:
        """الحصول على حالة قائمة الانتظار"""
        return {
            'running': self._running,
            'pending_requests': self.pending_requests.qsize(),
            'active_requests': len(self.active_requests),
            'active_request_ids': list(self.active_requests.keys())
        }

# ===== متغيرات عامة =====
_browser_manager: Optional[BrowserManager] = None
_request_queue: Optional[RequestQueue] = None
_initialized = False

async def initialize_pubg_system():
    """تهيئة نظام PUBG عند بدء تشغيل الـ API"""
    global _browser_manager, _request_queue, _initialized

    if _initialized:
        return True

    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright غير متاح!")
        return False

    try:
        print("🔧 تهيئة مدير المتصفحات للبحث عن لاعبي PUBG...")
        _browser_manager = BrowserManager(browser_count=3, headless=True)

        if not await _browser_manager.initialize():
            print("❌ فشل في تهيئة مدير المتصفحات!")
            return False

        print("📋 تهيئة قائمة الطلبات...")
        _request_queue = RequestQueue(_browser_manager)
        await _request_queue.start()

        _initialized = True
        print("✅ تم تهيئة نظام PUBG بنجاح!")
        return True

    except Exception as e:
        print(f"❌ خطأ في تهيئة نظام PUBG: {e}")
        return False

async def _initialize_system():
    """تهيئة النظام إذا لم يتم تهيئته بعد (للاستخدام الداخلي)"""
    return await initialize_pubg_system()

def get_pubg_player_name(player_id: str) -> Optional[str]:
    """
    البحث عن اسم لاعب PUBG باستخدام معرف اللاعب

    Args:
        player_id (str): معرف اللاعب

    Returns:
        str or None: اسم اللاعب أو None إذا لم يوجد
    """
    if not player_id or not str(player_id).strip():
        return None

    try:
        # التحقق من وجود حلقة أحداث نشطة
        try:
            loop = asyncio.get_running_loop()
            # إذا كانت هناك حلقة نشطة، استخدم asyncio.create_task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_search_in_new_loop, str(player_id).strip())
                return future.result(timeout=30)  # مهلة 30 ثانية
        except RuntimeError:
            # لا توجد حلقة نشطة، يمكن إنشاء واحدة جديدة
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(_search_player_async(str(player_id).strip()))
                return result
            finally:
                loop.close()

    except Exception as e:
        print(f"❌ خطأ في البحث عن لاعب PUBG {player_id}: {e}")
        return None

def _run_search_in_new_loop(player_id: str) -> Optional[str]:
    """تشغيل البحث في حلقة أحداث جديدة"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_search_player_async(player_id))
    finally:
        loop.close()

async def _search_player_async(player_id: str) -> Optional[str]:
    """البحث عن اللاعب بشكل غير متزامن"""
    global _browser_manager, _request_queue

    # تهيئة النظام إذا لم يتم تهيئته
    if not await _initialize_system():
        return None

    try:
        result = await _request_queue.submit_request(player_id)

        if result.get('success') and result.get('player_name'):
            return result['player_name']
        else:
            return None

    except Exception as e:
        print(f"❌ خطأ في البحث الداخلي: {e}")
        return None

# ===== تنظيف الموارد عند الإغلاق =====

async def cleanup_resources():
    """تنظيف الموارد عند إغلاق التطبيق"""
    global _browser_manager, _request_queue, _initialized

    if _request_queue:
        try:
            await _request_queue.stop()
            print("✅ تم إيقاف قائمة طلبات PUBG")
        except Exception as e:
            print(f"❌ خطأ في إيقاف قائمة طلبات PUBG: {e}")

    if _browser_manager:
        try:
            await _browser_manager.cleanup()
            print("✅ تم إيقاف مدير متصفحات PUBG")
        except Exception as e:
            print(f"❌ خطأ في إيقاف مدير متصفحات PUBG: {e}")

    _initialized = False

# ===== Flask Server =====

# Flask app for local server
app = Flask(__name__)
CORS(app)

@app.route('/pubg/player/<player_id>', methods=['GET'])
def get_player_info(player_id):
    """API endpoint for PUBG player lookup"""
    try:
        player_name = get_pubg_player_name(player_id)

        if player_name:
            return jsonify({
                'success': True,
                'player_id': player_id,
                'player_name': player_name,
                'method': 'unified_system_parallel'
            })
        else:
            return jsonify({
                'success': False,
                'player_id': player_id,
                'error': 'Invalid player ID - player not found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'player_id': player_id
        }), 500

@app.route('/pubg/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    global _browser_manager, _request_queue, _initialized

    status = {
        'status': 'healthy',
        'service': 'PUBG Player Lookup - Parallel System',
        'playwright_available': PLAYWRIGHT_AVAILABLE,
        'initialized': _initialized
    }

    if _browser_manager:
        browser_status = asyncio.run(_browser_manager.get_status())
        status['browsers'] = browser_status

    if _request_queue:
        queue_status = _request_queue.get_queue_status()
        status['queue'] = queue_status

    return jsonify(status)

@app.route('/pubg/shutdown', methods=['POST'])
def shutdown_server():
    """Shutdown endpoint to cleanup browsers"""
    try:
        asyncio.run(cleanup_resources())
        return jsonify({'status': 'shutdown', 'message': 'All browsers cleaned up successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def run_server(host='localhost', port=5000):
    """Run the Flask server"""
    import atexit
    atexit.register(lambda: asyncio.run(cleanup_resources()))

    print(f"🚀 Starting PUBG Player Lookup Server (Parallel System) on http://{host}:{port}")
    print("📋 Available endpoints:")
    print(f"   GET http://{host}:{port}/pubg/player/<player_id> - Get player info")
    print(f"   GET http://{host}:{port}/pubg/health - Health check with browser status")
    print(f"   POST http://{host}:{port}/pubg/shutdown - Shutdown and cleanup")
    print()

    try:
        app.run(host=host, port=port, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Server interrupted, cleaning up...")
        asyncio.run(cleanup_resources())
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        asyncio.run(cleanup_resources())

# ===== اختبار الوحدة =====

async def test_parallel_system():
    """Test function for parallel system"""
    print("🎮 اختبار نظام البحث المتوازي عن لاعبي PUBG")
    print("=" * 50)

    test_player_id = input("أدخل معرف لاعب PUBG للاختبار: ").strip()
    if test_player_id:
        print(f"� البحث عن اللاعب: {test_player_id}")

        player_name = get_pubg_player_name(test_player_id)
        if player_name:
            print(f"✅ تم العثور على اللاعب: {player_name}")
        else:
            print("❌ لم يتم العثور على اللاعب أو حدث خطأ")

        # تنظيف الموارد
        await cleanup_resources()
    else:
        print("❌ لم يتم إدخال معرف اللاعب")

def main():
    """Main function with options"""
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'server':
            # Run as server
            host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
            port = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
            run_server(host, port)
        elif sys.argv[1] == 'test':
            # Run test lookup
            asyncio.run(test_parallel_system())
        else:
            print("Usage:")
            print("  python pubg_player.py server [host] [port]  - Run as server")
            print("  python pubg_player.py test                  - Run test lookup")
    else:
        # Default: run test
        asyncio.run(test_parallel_system())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n👋 Interrupted!")
        asyncio.run(cleanup_resources())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        asyncio.run(cleanup_resources())
