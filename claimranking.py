import re
import mysql.connector
import wikipedia
import requests
from urllib.parse import quote
import math

WIKIPEDIA_MAX_QUERY_LENGTH = 300
TOP_K_RESULTS = 5
START_DATE = "20220101"
END_DATE = "20230101"


def get_wikipedia_views(title: str) -> int:
    headers = {
        "User-Agent": "jonathan@improvethenews.org",
        "Accept": "application/json"
    }
    # https://wikimedia.org/api/rest_v1/#/Pageviews%20data/get_metrics_pageviews_per_article__project___access___agent___article___granularity___start___end_
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{title}" \
          f"/monthly/{START_DATE}/{END_DATE}"

    res = requests.get(url, headers=headers)
    total_views = 0
    if res.status_code == 200:
        data = res.json()
        for item in data["items"]:
            total_views += item["views"]
    else:
        data = res.json()
        # print(res.status_code, data["type"])

    return total_views


def get_wikipedia_edits(title: str) -> int:
    headers = {
        "User-Agent": "jonathan@improvethenews.org",
        "Accept": "application/json"
    }
    url = f"https://wikimedia.org/api/rest_v1/metrics/edits/per-page/en.wikipedia/{title}/user" \
          f"/monthly/{START_DATE}/{END_DATE}"

    res = requests.get(url, headers=headers)
    total_edits = 0
    if res.status_code == 200:
        data = res.json()
        for result in data["items"][0]["results"]:
            total_edits += result["edits"]
    else:
        data = res.json()

    return total_edits


def get_keyword_references(claim: str) -> tuple[int, float]:
    """
    :param claim:
    :return: 2-tuple of (keyword_hits, sum of keyword log)
    """
    matches = re.findall(r'\[\d+\]', claim)
    id_list = [int(match[1:-1]) for match in matches]
    if len(id_list) == 0:
        return 0, 0
    num_references = 0
    sum_log_e = 0
    try:
        con = mysql.connector.connect(user='root', password='DdlrsIjzp52YeOs8',
                                      host='localhost', database="improvethenews", port="3306")
    except mysql.connector.Error as err:
        print(err)
    else:
        cursor = con.cursor()

        cursor.execute(
            "SELECT uses FROM keywords WHERE id IN (%s)" % ', '.join(['%s'] * len(id_list)),
            id_list
        )
        uses = cursor.fetchall()
        num_references = sum([use[0] for use in uses])
        sum_log_e = sum([math.log(use[0]) for use in uses])
    return num_references, sum_log_e


if __name__ == "__main__":
    with open('claims_10.txt', 'r', encoding="utf-8") as f:
        claim_stats = {}
        while True:
            text = f.readline()
            keyworded_claim = f.readline()
            if not text:
                break

            _claim = text.strip()
            keyworded_claim = keyworded_claim.strip()
            page_titles = wikipedia.search(_claim[:WIKIPEDIA_MAX_QUERY_LENGTH])
            views = 0
            edits = 0
            (keyword_hits, keyword_hits_e) = get_keyword_references(keyworded_claim)
            for page_title in page_titles:
                page_title = quote(page_title)
                views += get_wikipedia_views(page_title)
                edits += get_wikipedia_edits(page_title)

            claim_stats[_claim] = {
                "wikipedia_views": views,
                "wikipedia_edits": edits,
                "page_titles": page_titles,
                "keyword_hits": keyword_hits,
                "keyword_hits_e": keyword_hits_e
            }

            # sort by wikipedia_views
            sorted_claim_stats = sorted(claim_stats.items(), key=lambda x: x[1]["wikipedia_views"], reverse=True)
            with open('claim_views_10.txt', 'w', encoding="utf-8") as f1:
                for claim_stat in sorted_claim_stats:
                    f1.write(claim_stat[0])
                    f1.write("\n")
                    f1.write("wikipedia_views: " + str(claim_stat[1]["wikipedia_views"]))
                    f1.write("\n")
                    f1.write("page_titles: " + str(claim_stat[1]["page_titles"]))
                    f1.write("\n")
                    f1.write("\n")

            # sort by wikipedia_edits
            sorted_claim_stats = sorted(claim_stats.items(), key=lambda x: x[1]["wikipedia_edits"], reverse=True)
            with open('claim_edits_10.txt', 'w', encoding="utf-8") as f2:
                for claim_stat in sorted_claim_stats:
                    f2.write(claim_stat[0])
                    f2.write("\n")
                    f2.write("wikipedia_edits: " + str(claim_stat[1]["wikipedia_edits"]))
                    f2.write("\n")
                    f2.write("page_titles: " + str(claim_stat[1]["page_titles"]))
                    f2.write("\n")
                    f2.write("\n")

            # sort by keyword_hits
            sorted_claim_stats = sorted(claim_stats.items(), key=lambda x: x[1]["keyword_hits"], reverse=True)
            with open('claim_keyword_hits_10.txt', 'w', encoding="utf-8") as f3:
                for claim_stat in sorted_claim_stats:
                    f3.write(claim_stat[0])
                    f3.write("\n")
                    f3.write("keyword_hits: " + str(claim_stat[1]["keyword_hits"]))
                    f3.write("\n")
                    f3.write("\n")

            # sort by keyword_hits_e
            sorted_claim_stats = sorted(claim_stats.items(), key=lambda x: x[1]["keyword_hits_e"], reverse=True)
            with open('claim_keyword_hits_e_10.txt', 'w', encoding="utf-8") as f4:
                for claim_stat in sorted_claim_stats:
                    f4.write(claim_stat[0])
                    f4.write("\n")
                    f4.write("keyword_hits_e: " + str(claim_stat[1]["keyword_hits_e"]))
                    f4.write("\n")
                    f4.write("\n")
