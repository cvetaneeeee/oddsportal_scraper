from playwright.sync_api import sync_playwright
from datetime import datetime
from google.oauth2 import service_account
from current_links import run_links
import re
import os
import json
import pandas as pd
import gspread


def test_json(response, results):
    try:
        results.append(
            {
                'url': response.url,
                'data': response.json(),
            }
        )
    except:
        pass


def run(playwright, url):
    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
    results = []
    browser = playwright.chromium.launch()
    context = browser.new_context(user_agent=agent)
    page = context.new_page()
    page.on("response", lambda response: test_json(response, results)),
    page.goto(url, wait_until="networkidle")
    page.close()
    context.close()
    browser.close()
    print(f'Loaded {url}')
    return results


def push_to_gsheets(key_path: str, spreadsheet: str, sheet: str, df: pd.DataFrame) -> None:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    credentials = service_account.Credentials.from_service_account_file(key_path, scopes=scope)
    client = gspread.authorize(credentials)
    sh = client.open_by_key(spreadsheet)
    sh.values_clear(f"{sheet}!A:P")
    sh.worksheet(sheet).resize(rows=2)
    sh.worksheet(sheet).resize(cols=18)
    sh.worksheet(sheet).update([df.columns.values.tolist()] + df.values.tolist())

country = 'italy' #change if you want to scrape a different country
league = 'serie-a' #change if you want to scrape a different league
run_links(country=country, league=league)

with open(f'Links\\{league}-current-links.json', 'r') as f:
    urls = json.load(f)

with sync_playwright() as playwright:
        try:
            for url in urls[:9]:
                    
                    season = '2023-2024' #change when new season starts
                    bookie_id = 16 #bet365, change for different bookie
                    bookie_name = 'bet365'

                    id = url.split('/')[-2]
                    odds_data = run(playwright, url)
                    odds_data = [x for x in odds_data if x['url'].endswith('.dat')]
                    odds_data = odds_data[0]
                    
                    list_lenght = len(url.split('/', 6)[-1].split('-'))
                    id = url.split('/', 6)[-1].split('-')[-1].split('/')[0]
                    home_team = url.split('/', 6)[-1].split('-')[0].capitalize()
                    away_team = url.split('/', 6)[-1].split('-')[1].capitalize()
                    third_team = url.split('/', 6)[-1].split('-')[2].capitalize() if url.split('/', 6)[-1].split('-')[2][-1] != '/' else ""
                    try:
                        forth_team = url.split('/', 6)[-1].split('-')[3].capitalize() if url.split('/', 6)[-1].split('-')[3][
                                                                                            -1] != '/' else ""
                    except:
                        pass


                    ###### NEEDS TO BE REWORKED FOR OTHER LEAGUES ######

                    if home_team == 'As':
                        home_team = 'Roma'
                        away_team = third_team
                    if away_team == 'As':
                        away_team = 'Roma'
                    if third_team == 'As':
                        away_team = 'Roma'
                    if home_team == 'Ac':
                        home_team = 'Milan'
                        away_team = third_team
                    if away_team == 'Ac':
                        away_team = 'Milan'
                    if third_team == 'Ac':
                        away_team = 'Milan'

                    ###### NEEDS TO BE REWORKED FOR OTHER LEAGUES ######



                    indices = [s.start() for s in re.finditer('/', url)]
                    competition = url[indices[4]:indices[5]].split('/')[1]

                    try:
                        closing_odds = odds_data['data']['d']['oddsdata']['back']['E-1-2-0-0-0']['odds'][f'{bookie_id}']
                        opening_odds = odds_data['data']['d']['oddsdata']['back']['E-1-2-0-0-0']['openingOdd'][f'{bookie_id}']
                        closing_time = odds_data['data']['d']['oddsdata']['back']['E-1-2-0-0-0']['changeTime'][f'{bookie_id}']
                        opening_time = odds_data['data']['d']['oddsdata']['back']['E-1-2-0-0-0']['openingChangeTime'][f'{bookie_id}']
                    except TypeError:
                        print(f'No more odds @ {bookie_name}')

                    home_score = None
                    away_score = None

                    try:
                        open_time = list(opening_time.values())[1]
                        close_time = list(closing_time.values())[1]

                        home_win_opening = opening_odds["0"]
                        draw_opening = opening_odds["1"]
                        away_win_opening = opening_odds["2"]

                        home_win_closing = closing_odds["0"]
                        draw_closing = closing_odds["1"]
                        away_win_closing = closing_odds["2"]

                    except:
                        open_time = opening_time[1]
                        close_time = opening_time[1]

                        home_win_opening = opening_odds[0]
                        draw_opening = opening_odds[1]
                        away_win_opening = opening_odds[2]

                        home_win_closing = closing_odds[0]
                        draw_closing = closing_odds[1]
                        away_win_closing = closing_odds[2]


                    odds = list()

                    if list_lenght == 5:
                        odds_movement = {
                            'id': id,
                            'bookie': bookie_name,
                            'competition': competition,
                            'season': season,
                            'home_team': home_team,
                            'away_team': away_team,
                            'opening_time': datetime.fromtimestamp(open_time) if open_time is not None else datetime.strptime('1899-01-01 00:00:00', r'%Y-%m-%d %H:%M:%S'),
                            'closing_time': datetime.fromtimestamp(close_time) if close_time is not None else datetime.strptime('1899-01-01 00:00:00', r'%Y-%m-%d %H:%M:%S'),
                            'home_win_opening': home_win_opening,
                            'draw_opening': draw_opening,
                            'away_win_opening': away_win_opening,
                            'home_win_closing': home_win_closing,
                            'draw_closing': draw_closing,
                            'away_win_closing': away_win_closing,
                            'home_score': home_score,
                            'away_score': away_score
                        }
                    else:
                        odds_movement = {
                            'id': id,
                            'bookie': bookie_name,
                            'competition': competition,
                            'season': season,
                            'home_team': home_team,
                            'away_team': away_team,
                            'opening_time': datetime.fromtimestamp(open_time) if open_time is not None else datetime.strptime('1899-01-01 00:00:00', r'%Y-%m-%d %H:%M:%S'),
                            'closing_time': datetime.fromtimestamp(close_time) if close_time is not None else datetime.strptime('1899-01-01 00:00:00', r'%Y-%m-%d %H:%M:%S'),
                            'home_win_opening': home_win_opening,
                            'draw_opening': draw_opening,
                            'away_win_opening': away_win_opening,
                            'home_win_closing': home_win_closing,
                            'draw_closing': draw_closing,
                            'away_win_closing': away_win_closing,
                            'home_score': home_score,
                            'away_score': away_score
                        }

                    odds.append(odds_movement)
                    df = pd.DataFrame(odds)
                    df_path = 'current_odds.csv'
                    df.to_csv(df_path, mode='a', header=not os.path.exists(df_path), index=False)

        except KeyError:
            print(f'No more odds @ bet365')


if __name__ == "__main__":

    path = "keys.json" #the location of your service account keys file
    spreadsheetId = "your spreadsheet"
    sheetName = "your sheet name"

    with open(df_path, 'r') as f:
        df = pd.read_csv(f, index_col=False)
        df = df.fillna('')

    push_to_gsheets(path, spreadsheetId, sheetName, df)
    
    if os.path.isfile(df_path):
        os.remove(df_path)