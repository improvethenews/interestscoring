from interest import *

if __name__ == "__main__":
    with open(f'output/claim_keyword_hits_e_100.txt', 'r', encoding="utf-8") as f:
        lines = f.readlines()
    top_10_claims = lines[:60:3]
    claim_stats = {}

    for claim in top_10_claims:
        wikipedia_research = wiki.run(claim)
        messages = chat_prompt.format_prompt(claim=claim, wikipedia_research=wikipedia_research).to_messages()
        response = chat(messages)
        output = response.content
        try:
            output_json = json.loads(output)
            avg_score = sum([output_json[criterion] for criterion in output_json]) / len(output_json) / 10
            claim_stats[claim] = avg_score
        except:
            print("Error parsing JSON output")

    sorted_claim_stats = sorted(claim_stats.items(), key=lambda x: x[1], reverse=True)
    with open(f'output/claim_keyword_hits_e_100_top10gpt.txt', 'w', encoding="utf-8") as f:
        for claim_stat in sorted_claim_stats:
            f.write(claim_stat[0])
            f.write("\n")
            f.write("avg_score: " + str(claim_stat[1]))
            f.write("\n")
            f.write("\n")
