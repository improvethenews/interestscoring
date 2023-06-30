import wikipedia
import requests
from urllib.parse import quote

WIKIPEDIA_MAX_QUERY_LENGTH = 300
TOP_K_RESULTS = 5


def get_wikipedia_views(claim: str) -> int:
    page_titles = wikipedia.search(claim[:WIKIPEDIA_MAX_QUERY_LENGTH])
    print(len(page_titles))
    total_views = 0
    for title in page_titles:
        title = quote(title)  # URI encode the title
        # https://wikimedia.org/api/rest_v1/#/Pageviews%20data/get_metrics_pageviews_per_article__project___access___agent___article___granularity___start___end_
        headers = {
            "User-Agent": "jonathan@improvethenews.org",
            "Accept": "application/json"
        }
        start_date = "20220101"
        end_date = "20230101"
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{title}" \
              f"/monthly/{start_date}/{end_date}"

        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            for item in data["items"]:
                total_views += item["views"]
        else:
            data = res.json()
            # print(res.status_code, data["type"])

    return total_views


if __name__ == "__main__":
    print(get_wikipedia_views("United States Nuclear Strike on China"))
