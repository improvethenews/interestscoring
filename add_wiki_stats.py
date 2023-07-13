import mysql.connector
from urllib.parse import quote
from claimranking import get_wikipedia_views, get_wikipedia_edits


def get_stats() -> None:
    try:
        con = mysql.connector.connect(user='root', password='DdlrsIjzp52YeOs8',
                                      host='localhost', database="improvethenews", port="3306")
    except mysql.connector.Error as err:
        print(err)
        return
    else:
        while True:  # Add a loop to keep the script running
            try:
                cursor = con.cursor()
                cursor.execute(
                    "SELECT id, text FROM `keywords` WHERE COALESCE(`wiki_views22`, 0) = 0 AND COALESCE(`wiki_edits22`) = 0 ORDER BY `uses` ASC LIMIT 100 "
                )
                articles = cursor.fetchall()
                if not articles:  # Break loop if no more articles to process
                    break
                for article in articles:
                    try:
                        article_id = article[0]
                        article_text = quote(article[1].strip())
                        print(article_id, article_text)

                        wiki_views = get_wikipedia_views(article_text)
                        wiki_edits = get_wikipedia_edits(article_text)

                        update_query = """UPDATE `keywords` SET `wiki_views22` = %s, `wiki_edits22` = %s WHERE `id` = %s"""
                        cursor.execute(update_query, (wiki_views, wiki_edits, article_id))
                        con.commit()
                    except Exception as e:
                        print(f"Failed to update article {article_id}. Error: {e}")
                        continue  # Continue with the next row
            except Exception as e:
                print(f"Error: {e}")
                continue
            finally:
                cursor.close()
        con.close()


if __name__ == "__main__":
    get_stats()
