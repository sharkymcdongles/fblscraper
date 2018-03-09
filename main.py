#! /usr/bin/env python3
import bs4
import csv
import requests

main_url = 'http://fbl.statsroom.de'
team = 'Berliner SC'


def get_game_urls(url):

    res = requests.get(url)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, "html.parser")

    games_urls = []

    for game in soup.select('#scores > tbody > tr'):
        if team in (str(game.find_all('td')[5])+str(game.find_all('td')[4])):
            try:
                games_urls.append(game.a.get('href'))

            except AttributeError:
                pass

    return games_urls


def get_game_logs(url_list):

    game_logs_raw = []

    for i in url_list:
        game_logs_raw.append(requests.get('http://fbl.statsroom.de/' + i))

    return game_logs_raw


def create_stats(game_logs_list):

    stats_dict = {}

    for req in game_logs_list:

        soup = bs4.BeautifulSoup(req.text, "lxml")

        team_letter = ((soup.find_all("h2")[0].string == team) * 'A') + \
                      ((soup.find_all("h2")[1].string == team) * 'B')

        tbody = soup.find("table", attrs={'id': 'team_' + team_letter}).tbody

        for tr in tbody:
            if len(tr) > 1:
                td = tr.find_all('td')
                player = td[0].text
                if player in stats_dict:

                    if len(td[2].text) >= 3:

                        stats_dict[player][1] = int(stats_dict[player][1]) + int(td[2].text.split('-')[0])
                        stats_dict[player][2] = int(stats_dict[player][2]) + int(td[2].text.split('-')[1])
                        stats_dict[player][3] = int(stats_dict[player][3]) + int(td[4].text)
                        stats_dict[player][4] = int(stats_dict[player][4]) + int(td[5].text)
                        stats_dict[player][5] = int(stats_dict[player][5]) + int(td[6].text)
                        stats_dict[player][6] += 1

                    else:

                        stats_dict[player][3] = int(stats_dict[player][3]) + int(td[4].text)
                        stats_dict[player][4] = int(stats_dict[player][4]) + int(td[5].text)
                        stats_dict[player][5] = int(stats_dict[player][5]) + int(td[6].text)
                        stats_dict[player][6] += 1

                else:

                    if len(td[2].text) >= 3:

                        stats_dict[player] = [td[1].text,                     # jersey number | index 0
                                              int(td[2].text.split('-')[0]),  # ftm           | index 1
                                              int(td[2].text.split('-')[1]),  # fta           | index 2
                                              td[4].text,                     # twos          | index 3
                                              td[5].text,                     # threes        | index 4
                                              td[6].text,                     # points        | index 5
                                              1]                              # games played  | index 6
                    else:

                        stats_dict[player] = [td[1].text,  # jersey number | index 0
                                              0,           # ftm           | index 1
                                              0,           # fta           | index 2
                                              td[4].text,  # twos          | index 3
                                              td[5].text,  # threes        | index 4
                                              td[6].text,  # points        | index 5
                                              1]           # games played  | index 6

    return stats_dict


def create_csv(stats_dict):

    csv_file = "D:\stats.csv"
    csv_header = ['Player', 'Number', 'GP', 'FTM', 'FTA', 'FT%', 'FGM', '3PM', 'PTS', '3PG', '2PG', 'PPG']

    with open(csv_file, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)

        for player, values in stats_dict.items():
            if int(values[6]) == 0:
                points_per_game = 0
            else:
                points_per_game = int(values[5])/int(values[6])

            if int(values[2]) == 0:
                free_throw_percentage = 0
            else:
                free_throw_percentage = int(values[1])/int(values[2])

            row = [player,
                   values[0],               # Jersey Number
                   values[6],               # Games Played
                   values[1],               # FTM
                   values[2],               # FTA
                   "{:.2%}".format(free_throw_percentage),   # FT%
                   values[3],               # 2PM
                   values[4],               # 3PM
                   values[5],               # Points
                   round(int(values[4])/int(values[6]), 2),   # 3PG
                   round(int(values[3])/int(values[6]), 2),     # 2PG
                   points_per_game]         # PPG

            writer.writerow(row)

    return


raw_data = get_game_logs(get_game_urls(main_url))

stats = create_stats(raw_data)

create_csv(stats)
