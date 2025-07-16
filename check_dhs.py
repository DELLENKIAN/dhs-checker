from playwright.sync_api import sync_playwright
import time

USERNAME = "NCRDC4429"
PASSWORD = "Odinson1203"

def check_dhs_status(id_number):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        status = "NO DHS"
        dc_name = "NO DHS"

        try:
            print("🔐 Logging into DHS...")
            page.goto("https://www.ncrdebthelp.co.za/")
            page.click("text='System LogIn'")
            page.fill("#cp_pagedata_f_login_username", USERNAME)
            page.fill("#cp_pagedata_f_login_password", PASSWORD)
            page.click("text='Proceed | LogIn'")

            page.wait_for_selector("a[href*='dhs_ManageRequestTransfers.aspx']", timeout=15000)
            page.click("a[href*='dhs_ManageRequestTransfers.aspx']")
            page.wait_for_selector("#cp_pagedata_lb_NewData", timeout=15000)
            page.click("#cp_pagedata_lb_NewData")

            print(f"🔎 Searching ID: {id_number}")
            page.fill("#cp_pagedata_f_RSAIDPass", id_number)
            time.sleep(1)
            page.click("#cp_pagedata_lb_ApplyDataFilter")

            row_selector = f"tr:has(td:text('{id_number}'))"
            try:
                page.wait_for_selector(row_selector, timeout=6000)
                status_selector = f"{row_selector} >> td:nth-child(6) >> div >> span"
                status = page.locator(status_selector).inner_text().strip()
                print(f"✅ Status: {status}")

                modal_trigger_selector = f"{row_selector} >> td:nth-child(8) >> div"
                page.click(modal_trigger_selector)

                page.wait_for_selector("iframe#IframePage", timeout=10000)
                iframe = page.frame(name="IframePage")
                if not iframe:
                    iframe = next(f for f in page.frames if "dhs_ViewDCDetails.aspx" in f.url)

                iframe.wait_for_selector("#f_TradingName", timeout=10000)
                dc_name = iframe.locator("#f_TradingName").inner_text().strip()
                print(f"✅ DC Name: {dc_name}")

                page.click("#cp_pagedata_btnHide")
                time.sleep(1)

            except:
                print(f"❌ No DHS record found for {id_number}")

        except Exception as e:
            print(f"⚠️ Error for ID {id_number}: {e}")

        browser.close()
        return status, dc_name
