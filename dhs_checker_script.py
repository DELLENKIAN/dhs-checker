import csv
import sys
from playwright.sync_api import sync_playwright

def check_dhs_status(id_number):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Go to DHS login
        page.goto("https://www.ncrdebthelp.co.za/")
        page.fill('#cp_pagedata_f_login_username', 'NCRDC4429')
        page.fill('#cp_pagedata_f_login_password', 'Odinson1203')
        page.click('text="Proceed | LogIn"')

        # Navigate to Consumer Transfer
        page.click('text="Request & Manage Consumer Transfer(s)"')
        page.click('#cp_pagedata_lb_NewData')

        # Enter ID and search
        page.fill('#cp_pagedata_f_RSAIDPass', id_number)
        page.click('#cp_pagedata_lb_ApplyDataFilter')
        page.wait_for_timeout(3000)

        # Try to extract status
        try:
            status_selector = '#MMhENTRY_1930641 > td:nth-child(6) > div > span'
            status = page.locator(status_selector).text_content().strip()
        except:
            status = 'Unknown'

        # Try to open modal and extract DC name
        try:
            page.click('tr:has(td:text("{0}")) td:nth-child(1)'.format(id_number))
            page.wait_for_timeout(2000)
            dc_name = page.locator('#f_TradingName').text_content().strip()
        except:
            dc_name = 'Unknown'

        browser.close()
        return status, dc_name

def main(input_csv, output_csv):
    with open(input_csv, newline='') as infile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        writer.writerow(['ID Number', 'Debt Review Status', 'Debt Counsellor'])

        for row in reader:
            id_number = row[0].strip()
            if not id_number or not id_number.isdigit():
                continue
            print(f"Checking ID: {id_number}")
            try:
                status, dc_name = check_id_status(id_number)
            except Exception as e:
                status, dc_name = 'Error', str(e)
            writer.writerow([id_number, status, dc_name])

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python dhs_checker_script.py input.csv output.csv")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_csv = sys.argv[2]
    main(input_csv, output_csv)
