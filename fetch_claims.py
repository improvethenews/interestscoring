import mysql.connector


def fetch_data():
    try:
        con = mysql.connector.connect(user='root', password='DdlrsIjzp52YeOs8',
                                      host='localhost', database="improvethenews", port="3306")
    except mysql.connector.Error as err:
        print(err)
    else:
        cursor = con.cursor()

        cursor.execute(
            "SELECT text, keyworded_claim FROM `claimarticles` LIMIT 1000 "
        )
        claimarticles = cursor.fetchall()

        # save to claims.txt
        with open('claims_10.txt', 'w', encoding="utf-8") as f:
            for claimarticle in claimarticles[:10]:
                (text, keyworded_claim) = claimarticle
                f.write(text + '\n')
                f.write(keyworded_claim + '\n')

        with open('claims_100.txt', 'w', encoding="utf-8") as f:
            for claimarticle in claimarticles[:100]:
                (text, keyworded_claim) = claimarticle
                f.write(text + '\n')
                f.write(keyworded_claim + '\n')

        with open('claims_1000.txt', 'w', encoding="utf-8") as f:
            for claimarticle in claimarticles[:1000]:
                (text, keyworded_claim) = claimarticle
                f.write(text + '\n')
                f.write(keyworded_claim + '\n')


if __name__ == "__main__":
    fetch_data()
