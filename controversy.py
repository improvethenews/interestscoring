"""Controversy scoring using entropy"""
import mysql.connector
from typing import List, Tuple
import math
import plotly.express as px
import numpy as np


def get_mysql_connection():
    try:
        con = mysql.connector.connect(user='root', password='DdlrsIjzp52YeOs8',
                                      host='localhost', database="improvethenews", port="3306")
        cursor = con.cursor()
    except mysql.connector.Error as err:
        print(err)
        exit(1)
    return con, cursor


def get_clusters(ids: List[int]) -> List[Tuple[int, str]]:
    con, cursor = get_mysql_connection()
    cursor.execute(
        "SELECT id, title FROM `claimclusters` WHERE `id` IN (%s)" % ', '.join(['%s'] * len(ids)),
        ids
    )
    claim_clusters = cursor.fetchall()
    return claim_clusters  # type: ignore


def get_claims(cluster_id: int) -> List[Tuple[int]]:
    con, cursor = get_mysql_connection()
    cursor.execute(
        "SELECT claim_id FROM `claimmatches` WHERE `cluster_id` = %s",
        (cluster_id,)
    )
    claims = cursor.fetchall()
    return claims  # type: ignore


def get_inferences(claim_ids: List[int]) -> List[Tuple[int, int, int, int]]:
    """
    We want to get
    :param claim_ids:
    :return: List of tuples of (id, claim_id1, claim_id2, inference_id)
    inference_id: 0 = neutral, 1 = entailment, 2 = contradiction
    """
    con, cursor = get_mysql_connection()
    placeholders = ', '.join(['%s'] * len(claim_ids))
    cursor.execute(
        f"SELECT id, claim_id1, claim_id2, inference_id FROM `claiminferences` "
        f"WHERE `claim_id1` IN ({placeholders}) AND `claim_id2` IN ({placeholders})",
        claim_ids * 2
    )
    inferences = cursor.fetchall()
    return inferences  # type: ignore


def get_controversy_score(num_entailments: int, num_contradictions: int) -> float:
    """entropy-based controversy score"""
    if num_entailments == 0 or num_contradictions == 0:
        return 0
    num_total = num_entailments + num_contradictions
    p_a, p_b = num_entailments / num_total, num_contradictions / num_total
    score = (p_a * math.log(p_a) + p_b * math.log(p_b)) / math.log(1/2)
    return score


if __name__ == "__main__":
    clusters = get_clusters([x for x in range(1, 100)])
    controversy_scores = {}
    num_entailments = []
    num_contradictions = []
    cluster_names = []
    for cluster in clusters:
        claims = get_claims(cluster[0])
        inferences = get_inferences([x for (x,) in claims])  # convert to list of ints
        entailments = [x for x in inferences if x[3] == 1]
        contradictions = [x for x in inferences if x[3] == 2]
        num_entailments.append(len(entailments))
        num_contradictions.append(len(contradictions))
        cluster_names.append(cluster[1])
        controversy_scores[cluster[1]] = get_controversy_score(len(entailments), len(contradictions))

    # sort by controversy score
    controversy_scores = {k: v for k, v in sorted(controversy_scores.items(), key=lambda item: item[1], reverse=True)}
    for cluster, score in controversy_scores.items():
        print(cluster, score)

    fig = px.scatter(x=num_entailments, y=num_contradictions, hover_name=cluster_names)
    fig.update_layout(
        title="Entailments vs. Contradictions Linear",
        xaxis_title="Number of Entailments",
        yaxis_title="Number of Contradictions",
    )
    # print correlation
    arr = np.array([num_entailments, num_contradictions])
    arr = arr[:, ~np.all(arr == 0, axis=0)]
    print(np.corrcoef(arr[0], arr[1]))
    fig.show()

    fig = px.scatter(x=num_entailments, y=num_contradictions, hover_name=cluster_names, log_x=True, log_y=True)
    fig.update_layout(
        title="Entailments vs. Contradictions Log",
        xaxis_title="Number of Entailments",
        yaxis_title="Number of Contradictions",
    )
    # print correlation of log, remove 0s
    arr = np.array([num_entailments, num_contradictions])
    arr = arr[:, ~np.all(arr == 0, axis=0)]
    print(np.corrcoef(np.log(arr[0]), np.log(arr[1])))
    fig.show()
