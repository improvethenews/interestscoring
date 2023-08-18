"""Create an entailment graph based on all the claims for a cluster.
Then, remove all cycles to create a DAG.
Then, order the DAG topologically.
"""

import csv
import controversy
from typing import List, Tuple


def get_claim_names(claim_ids: List[int]) -> List[Tuple[int, str]]:
    cursor = controversy.con.cursor()
    placeholders = ', '.join(['%s'] * len(claim_ids))
    cursor.execute(
        f"SELECT id, text FROM `claimarticles` "
        f"WHERE `id` IN ({placeholders})",
        claim_ids
    )
    claims = cursor.fetchall()
    return claims  # type: ignore


if __name__ == "__main__":
    cluster = controversy.get_clusters([1])[0]
    claims = controversy.get_claims(cluster[0])
    claim_names = get_claim_names([x for (x,) in claims])
    inferences = controversy.get_inferences([x for (x,) in claims])
    entailments = [x for x in inferences if x[3] == 1]

    # open graph_input/edges.csv and write header row
    with open("graph_input/edges.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["id1", "id2"])
        for entailment in entailments:
            csvwriter.writerow([entailment[1], entailment[2]])

    with open("graph_input/nodes.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["index", "id", "claim"])
        # for index, claim in enumerate(claims):
        #     csvwriter.writerow([index, claim[0], claim[1]])
        for index, claim in enumerate(claim_names):
            csvwriter.writerow([index + 1, claim[0], claim[1]])
