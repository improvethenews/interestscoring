import json

import wikipedia
import requests
from urllib.parse import quote

WIKIPEDIA_MAX_QUERY_LENGTH = 300
TOP_K_RESULTS = 5
START_DATE = "20220101"
END_DATE = "20230101"


def get_wikipedia_views(claim: str) -> int:
    page_titles = wikipedia.search(claim[:WIKIPEDIA_MAX_QUERY_LENGTH])
    total_views = 0
    for title in page_titles:
        title = quote(title)  # URI encode the title
        # https://wikimedia.org/api/rest_v1/#/Pageviews%20data/get_metrics_pageviews_per_article__project___access___agent___article___granularity___start___end_
        headers = {
            "User-Agent": "jonathan@improvethenews.org",
            "Accept": "application/json"
        }
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{title}" \
              f"/monthly/{START_DATE}/{END_DATE}"

        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            for item in data["items"]:
                total_views += item["views"]
        else:
            data = res.json()
            # print(res.status_code, data["type"])

    return total_views


def get_wikipedia_edits(claim: str) -> int:
    page_titles = wikipedia.search(claim[:WIKIPEDIA_MAX_QUERY_LENGTH])
    total_edits = 0
    for title in page_titles:
        title = quote(title)  # URI encode the title
        headers = {
            "User-Agent": "jonathan@improvethenews.org",
            "Accept": "application/json"
        }
        url = f"https://wikimedia.org/api/rest_v1/metrics/edits/per-page/en.wikipedia/{title}/user" \
              f"/monthly/{START_DATE}/{END_DATE}"

        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            for result in data["items"][0]["results"]:
                total_edits += result["edits"]
        else:
            data = res.json()

    return total_edits


if __name__ == "__main__":
    print(get_wikipedia_views("United States Nuclear Strike on China"))
    print(get_wikipedia_edits("United States Nuclear Strike on China"))
