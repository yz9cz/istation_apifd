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
