import json
import pandas as pd
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def parse_item(html_page):
    soup = BeautifulSoup(html_page, "lxml")
    base = 'https://www.oddsportal.com'
    match_links = [base + match.select_one('a')['href'] for match in soup.select('.hover\:bg-\[\#f9e9cc\]')]
    return match_links


def main(country, league):
    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
    main.url = f"https://www.oddsportal.com/football/{country}/{league}"
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(user_agent=agent)

        ###### The below commented out code serves to log into the oddsportal website, some pages don't load unless you're logged in ######

        # page.goto('https://www.oddsportal.com/', wait_until='networkidle')
        # page.get_by_text("Login").first.click()
        # page.get_by_label("Username").fill("your username")
        # page.get_by_label("Password").fill("your password")
        # page.get_by_role("button", name="Login").click()

        ###### The above commented out code serves to log into the oddsportal website, some pages don't load unless you're logged in ######

        page.goto(main.url, wait_until='networkidle')
        last_height = page.evaluate("document.body.scrollHeight")

        while True:
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            page.wait_for_timeout(500)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        parsed_result = parse_item(page.content())
        return parsed_result
    

def run_links(country, league):

    result = main(country=country, league=league)
    json_string = json.dumps(result)

    with open(f'Links\\{league}-current-links.json', 'w') as f:
        f.write(json_string)
    
    print(f'We have processed {len(result)} match IDs from the {league}..')



if __name__ == "__main__":
    
    country = "country you want to scrape"
    league = "league you want to scrape"
    run_links(country=country, league=league)
