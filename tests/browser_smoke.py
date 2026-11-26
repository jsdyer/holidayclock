"""Exercise comparisons, privacy boundaries and working-day counts at a project subpath."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import tempfile
import threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def main():
    screenshots=ROOT/'browser-checks';screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT/'dist',Path(temporary)/'holidayclock')
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=temporary));threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch();page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];outbound=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.on('request',lambda request:outbound.append(request.url) if 'canada-holidays.ca' in request.url else None)
                page.goto(f'http://127.0.0.1:{server.server_port}/holidayclock/')
                page.locator('#results').wait_for(state='visible')
                page.locator('#year').fill('2026');page.locator('#compare-button').click()
                page.wait_for_function("document.querySelector('#status').textContent.includes('2026 comparison ready')")
                assert int(page.locator('#count-a').inner_text())>int(page.locator('#count-b').inner_text())
                page.locator('#filter').fill('Truth and Reconciliation');assert page.locator('.holiday-row').count()==1
                page.locator('#filter').fill('<img onerror=alert(1)>');assert page.locator('.holiday-row').count()==0;assert page.locator('img').count()==0
                page.locator('#filter').fill('')
                page.locator('#start').fill('2026-09-28');page.locator('#end').fill('2026-10-02');page.locator('#planner-button').click()
                page.locator('#planner-result').wait_for(state='visible');assert page.locator('#working-count').inner_text()=='4'
                with page.expect_download() as info:page.locator('#ics-a').click()
                assert info.value.suggested_filename.endswith('.ics')
                page.locator('#country-b').select_option('US');page.locator('#region-b').select_option('WA');page.locator('#compare-button').click()
                page.wait_for_function("document.querySelector('#table-b').textContent.includes('Washington')")
                assert not outbound,outbound
                before=page.locator('#rows').inner_text();page.route('https://canada-holidays.ca/**',lambda route:route.fulfill(status=503,body='unavailable'))
                page.locator('#year').fill('2024');page.locator('#compare-button').click();page.wait_for_function("document.querySelector('#status').textContent.includes('previous comparison is unchanged')")
                assert page.locator('#rows').inner_text()==before
                page.screenshot(path=str(screenshots/'desktop.png'),full_page=True);page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth');page.screenshot(path=str(screenshots/'mobile.png'),full_page=True)
                assert not errors,errors
                # Exercise the direct search landing page in a fresh browser context.
                case_page = browser.new_page(viewport={'width': 390, 'height': 844})
                case_page.route('https://**/*', lambda route: route.abort())
                case_page.goto(f'http://127.0.0.1:{server.server_port}/holidayclock/bc-business-days.html')
                case_page.wait_for_function("() => {const q=s=>document.querySelector(s);return q('#region-a').value==='BC' && !q('#planner-result').hidden && q('#working-count').textContent.trim()!=='';}")
                assert case_page.locator('link[rel="canonical"]').get_attribute('href') == 'https://coolcode.ca/holidayclock/bc-business-days.html'
                assert case_page.locator('h1').inner_text() in case_page.title()
                assert case_page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                browser.close()
            print('Browser checks passed: Canadian and international calendars, working days, ICS, preserved results, mobile layout')
        finally:server.shutdown()
if __name__=='__main__':main()
