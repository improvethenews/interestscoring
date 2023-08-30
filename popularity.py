from datetime import datetime, timedelta
import requests
import plotly
import mysql.connector


def update_figure_popularity(week_start: str) -> None:
    week_start = datetime.strptime(week_start, "%d%m%y").strftime("%Y%m%d")
    week_end = (datetime.strptime(week_start, "%Y%m%d") + timedelta(days=7)).strftime("%Y%m%d")
    try:
        con = mysql.connector.connect(user='root', password='DdlrsIjzp52YeOs8',
                                      host='localhost', database="improvethenews", port="3306")
    except mysql.connector.Error as err:
        print(err)
    else:
        cursor = con.cursor()

        # get (id, name) from figures table
        cursor.execute(
            "SELECT id, name FROM `figures` ORDER BY `id` ASC "
        )
        figures = cursor.fetchall()
        for figure in figures:
            print(figure)
            # get figure views for past week
            # url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
            #        f"{figure[1]}/daily/{week_start}/{week_end}")
            # cursor.execute(
            #     "INSERT INTO `figurepopularity` (`id`, `week_start_date`, `view_count`) "
            #     "VALUES (%s, %s, %s) ",
            #     (figure[0], week_start, get_wikipedia_views(figure[1]))
            # )


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
    # get latest full week starting Monday
    today = datetime.today()
    week_start = today - timedelta(days=today.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    if (today - week_start).days < 7:
        week_start -= timedelta(days=7)
    week_start = week_start.strftime("%d%m%y")  # make DDMMYY
    update_figure_popularity(week_start)

    # graph_figure_popularity("Donald_Trump")
