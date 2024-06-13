# import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# get input from user for the year range to pull data from.
print("Input start year")
start_year = input('>')
print("Input end year")
end_year = input('>')

# creates a list of years in descending order
years = list(range(int(end_year),int(start_year),-1))

team_matches = []

def pull_table():
    """
    this code iterates over each year in the years list,
    It uses BeautifulSoup to parse the HTML content from 
    the website url and extract a specific tables of teams data.
    """
    site_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    for year in years:
        data = requests.get(site_url)
        soup = BeautifulSoup(data.text,'lxml')
        standing_table = soup.select("table.stats_table")[0]

        links = standing_table.find_all("a")
        links = [l.get("href") for l in links]
        links = [l for l in links if '/squads/' in l]
        team_urls = [f"https://fbref.com{l}" for l in links]

        previous_season = soup.select("a.prev")[0].get("href")
        standing_url = f"https://fbref.com/{previous_season}"

    for team_url in team_urls:
        team_name = team_url.split("/")[-1].replace("-Stats","").replace("-"," ")

        data = requests.get(team_url)
        matches = pd.read_html(data.text, match = "Scores & Fixtures")[0]

        soup = BeautifulSoup(data.text, 'lxml')
        links = soup.find_all("a")
        links = [l.get("href") for l in links]
        links = [l for l in links if l and "all_comps/shooting/" in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        shooting = pd.read_html(data.text, match = "Shooting")[0]
        shooting.columns = shooting.columns.droplevel()

        try:
            team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist","FK", "PK", "PKatt"]], on = "Date")
        except ValueError:
            continue

        team_data = team_data[team_data["Comp"] == "Premier League"]
        #team_data["Season"] = year
        team_data["Team"] = team_name
        all_matches.append(team_data)
           
    match_df = pd.concat(all_matches)
    match_df.columns = [c.lower() for c in match_df.columns]
    match_df.to_csv("pulled_teams_data.csv", index = False)
    print("file saved...done")
    
if __name__ == '__main__':
    pull_table()
    time.sleep(1)