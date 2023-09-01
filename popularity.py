from datetime import datetime, timedelta

import mysql.connector.errors

import controversy
import requests
import plotly
from typing import List


def update_figure_wikipedia_links() -> None:
    con, cursor = controversy.get_mysql_connection()

    # get (id, name) from figures table
    cursor.execute(
        "SELECT id, name FROM `figures` ORDER BY `id` ASC "
    )
    figures = cursor.fetchall()
    for figure in figures:
        wiki_link = figure[1]
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&titles={wiki_link}&redirects"
        headers = {
            "User-Agent": "jonathan1@improvethenews.org",
            "Accept": "application/json"
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            correct_link = res.json()["query"]["redirects"][0]["to"] if "redirects" in res.json()["query"] else wiki_link
            print(correct_link)
            # add Wikipedia link to wiki_link column in figures table
            cursor.execute(
                "UPDATE `figures` SET `wiki_link` = %s WHERE `id` = %s",
                (correct_link, figure[0])
            )
            con.commit()


def update_figure_popularity(week_start: str) -> None:
    """
    :param week_start: YYMMDD
    """
    week_start_n = datetime.strptime(week_start, "%y%m%d").strftime("%Y%m%d")
    week_end_n = (datetime.strptime(week_start, "%y%m%d") + timedelta(days=7)).strftime("%Y%m%d")
    con, cursor = controversy.get_mysql_connection()

    # get (id, name) from figures table
    cursor.execute(
        "SELECT id, name, wiki_link FROM `figures` ORDER BY `id` ASC "
    )
    figures = cursor.fetchall()
    for figure in figures:
        wiki_link = figure[2]
        url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
               f"{wiki_link}/daily/{week_start_n}/{week_end_n}")
        headers = {
            "User-Agent": "jonathan1@improvethenews.org",
            "Accept": "application/json"
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            views = sum([item["views"] for item in data["items"]])
            try:
                cursor.execute(
                    "INSERT INTO `figure_popularity` (`id`, `week_start_date`, `view_count`) "
                    "VALUES (%s, %s, %s) ",
                    (figure[0], week_start, views)
                )
                con.commit()
            except mysql.connector.errors.IntegrityError:
                print(f"figure popularity for week starting {week_start} already exists")
                return


def get_figure_popularity(figure_id: int) -> List[int]:
    con, cursor = controversy.get_mysql_connection()
    cursor.execute(
        "SELECT view_count FROM `figure_popularity` WHERE `id` = %s ORDER BY `week_start_date` ASC ",
        (figure_id,)
    )
    view_count = cursor.fetchall()
    return [int(x[0]) for x in view_count]


def get_popularity_rankings() -> dict:
    con, cursor = controversy.get_mysql_connection()
    cursor.execute(
        "SELECT id, name FROM `figures` ORDER BY `id` ASC "
    )
    figures = cursor.fetchall()
    rankings = {}
    for figure in figures:
        popularity = get_figure_popularity(figure[0])
        if len(popularity) > 0:
            rankings[figure[1]] = popularity[-1]
    return rankings


def get_popularity_changes() -> dict:
    con, cursor = controversy.get_mysql_connection()
    cursor.execute(
        "SELECT id, name FROM `figures` ORDER BY `id` ASC "
    )
    figures = cursor.fetchall()
    changes = {}
    for figure in figures:
        popularity = get_figure_popularity(figure[0])
        if len(popularity) > 1:
            # get percent change from last week
            changes[figure[1]] = (popularity[-1] - popularity[-2]) / popularity[-2]
    return changes


def graph_figure_popularity(wiki_link: str) -> None:
    """graph Wikipedia views per day for a public figure"""
    headers = {
        "User-Agent": "jonathan1@improvethenews.org",
        "Accept": "application/json"
    }
    START_DATE = "20200101"
    END_DATE = "20221231"
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{wiki_link}" \
          f"/daily/{START_DATE}/{END_DATE}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        figure = wiki_link.replace("_", " ")
        data = res.json()
        x = [datetime.strptime(item["timestamp"], "%Y%m%d%H") for item in data["items"]]
        y = [item["views"] for item in data["items"]]
        fig = plotly.graph_objects.Figure(
            data=plotly.graph_objects.Scatter(x=x, y=y),
            layout_title_text=f"{figure} Wikipedia Views"
        )
        fig.show()

        # search for the top 1% of days by views on Google
        top_1_percent = sorted(y)[-int(len(y) * 0.01)]
        top_1_percent_dates = [x[i] for i in range(len(y)) if y[i] >= top_1_percent]
        figure = figure.replace(" ", "+")
        for date in top_1_percent_dates:
            # start_date is the day before, end_date is the day after
            start_date = (date - timedelta(days=1)).strftime("%m/%d/%Y")
            end_date = (date + timedelta(days=1)).strftime("%m/%d/%Y")
            google_news_url = (f"https://www.google.com/search?q={figure}&tbm=nws&tbs=cdr:1,cd_min:{start_date},"
                               f"cd_max:{end_date}")
            print("Google News search link:", google_news_url)
    else:
        data = res.json()
        print(res.status_code, data["type"])


if __name__ == "__main__":
    # update wiki_link column in figures table
    # update_figure_wikipedia_links()

    # get latest full week starting Monday
    # today = datetime.today()
    # week_start = today - timedelta(days=today.weekday())
    # week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    # if (today - week_start).days < 7:
    #     week_start -= timedelta(days=7)
    # week_start = week_start.strftime("%y%m%d")  # make YYMMDD
    # update_figure_popularity(week_start)

    # get popularity history of a public figure
    # print(get_figure_popularity(1))

    # rank public figures by change in popularity
    # changes = get_popularity_changes()
    # # sort by change
    # changes = {k: v for k, v in sorted(changes.items(), key=lambda item: item[1], reverse=True)}
    # for figure, change in changes.items():
    #     print(figure, change)

    # rank public figures by popularity
    rankings = get_popularity_rankings()
    # sort by popularity
    rankings = {k: v for k, v in sorted(rankings.items(), key=lambda item: item[1], reverse=True)}
    for figure, popularity in rankings.items():
        print(figure, popularity)

    # visualize popularity history of a public figure
    # graph_figure_popularity("Donald_Trump")
