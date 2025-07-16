from playwright.sync_api import sync_playwright
import csv
import os
import time

USERNAME = "NCRDC4429"
PASSWORD = "Odinson1203"

def read_id_numbers():
    if os.path.exists("id_numbers.csv"):
        with open("id_numbers.csv", newline='') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header
            return [row[0].strip() for row in reader if row and row[0].strip()]
    elif os.path.exists("id_numbers.txt"):
        with open("id_numbers.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    else:
        print("⚠️ File not found: Create 'id_numbers.csv' or 'id_numbers.txt'")
        return []

def save_results(results):
    with open("dhs_results.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID Number", "Status", "Debt Counsellor Name"])
        writer.writerows(results)

def check_multiple_ids(id_list):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("🔐 Logging into NCR Debt Help...")
        page.goto("https://www.ncrdebthelp.co.za/")
        page.click("text='System LogIn'")
        page.fill("#cp_pagedata_f_login_username", USERNAME)
        page.fill("#cp_pagedata_f_login_password", PASSWORD)
        page.click("text='Proceed | LogIn'")

        page.wait_for_selector("a[href*='dhs_ManageRequestTransfers.aspx']", timeout=15000)
        page.click("a[href*='dhs_ManageRequestTransfers.aspx']")
        page.wait_for_selector("#cp_pagedata_lb_NewData", timeout=15000)
        page.click("#cp_pagedata_lb_NewData")

        for id_number in id_list:
            print(f"\n🔎 Searching ID: {id_number}")
            status = "NO DHS"
            dc_name = "NO DHS"

            try:
                page.fill("#cp_pagedata_f_RSAIDPass", id_number)
                time.sleep(1)
                page.click("#cp_pagedata_lb_ApplyDataFilter")

                row_selector = f"tr:has(td:text('{id_number}'))"

                # ⏳ Check if row appears or not
                try:
                    page.wait_for_selector(row_selector, timeout=6000)

                    # ✅ Data found – extract status
                    status_selector = f"{row_selector} >> td:nth-child(6) >> div >> span"
                    status = page.locator(status_selector).inner_text().strip()
                    print(f"✅ Status: {status}")

                    # 🔍 Open modal and extract DC name
                    modal_trigger_selector = f"{row_selector} >> td:nth-child(8) >> div"
                    page.click(modal_trigger_selector)

                    page.wait_for_selector("iframe#IframePage", timeout=10000)
                    iframe = page.frame(name="IframePage")
                    if not iframe:
                        iframe = next(f for f in page.frames if "dhs_ViewDCDetails.aspx" in f.url)

                    iframe.wait_for_selector("#f_TradingName", timeout=10000)
                    dc_name = iframe.locator("#f_TradingName").inner_text().strip()
                    print(f"✅ DC Name: {dc_name}")

                    # ✅ Close modal
                    page.click("#cp_pagedata_btnHide")
                    time.sleep(1)

                except:
                    print(f"❌ No DHS record found for {id_number}")

            except Exception as e:
                print(f"⚠️ Error for ID {id_number}: {e}")

            results.append([id_number, status, dc_name])

        browser.close()
    return results

# 🚀 Main Run
if __name__ == "__main__":
    ids = read_id_numbers()
    if ids:
        output = check_multiple_ids(ids)
        save_results(output)
        print("\n✅ All done! Check 'dhs_results.csv'")
    else:
        print("🚫 No ID numbers to process.")
