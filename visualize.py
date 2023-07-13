import mysql.connector
import numpy as np
import plotly.express as px


def visualize():
    """Randomly sample 1000 articles from the keywords table and plot log(uses) vs log(wiki_views) and log(uses) vs
    log(wiki_edits)"""
    try:
        con = mysql.connector.connect(user='root', password='DdlrsIjzp52YeOs8',
                                      host='localhost', database="improvethenews", port="3306")
    except mysql.connector.Error as err:
        print(err)
        return
    else:
        cursor = con.cursor()
        cursor.execute(
            "SELECT text, uses, wiki_views22, wiki_edits22 FROM `keywords` WHERE COALESCE(`wiki_views22`, 0) != 0 OR COALESCE(`wiki_edits22`) != 0 ORDER BY RAND() LIMIT 1000 "
        )
        articles = cursor.fetchall()
        cursor.close()
        article_names = [article[0] for article in articles]
        articles = [article[1:] for article in articles]
        articles = np.array(articles)

        # remove rows where uses, wiki_views, or wiki_edits is 0
        indices = np.where(np.any(articles == 0, axis=1))
        articles = np.delete(articles, indices, axis=0)
        article_names = np.delete(article_names, indices, axis=0)
        uses = articles[:, 0]
        wiki_views = articles[:, 1]
        wiki_edits = articles[:, 2]

        fig = px.scatter(x=np.log10(uses), y=np.log10(wiki_views), hover_name=article_names)
        fig.update_layout(
            title=f"Correlation: {np.corrcoef(np.log10(uses), np.log10(wiki_views))[0, 1]}",
            xaxis_title="Log(uses)",
            yaxis_title="Log(wiki_views)",
        )
        fig.show()

        fig = px.scatter(x=np.log10(uses), y=np.log10(wiki_edits), hover_name=article_names)
        fig.update_layout(
            title=f"Correlation: {np.corrcoef(np.log10(uses), np.log10(wiki_edits))[0, 1]}",
            xaxis_title="Log(uses)",
            yaxis_title="Log(wiki_edits)",
        )
        fig.show()

        fig = px.histogram(x=np.log10(uses), nbins=100)
        fig.update_layout(
            title="Distribution of log_10(uses)",
            xaxis_title="Log(uses)",
            yaxis_title="Frequency",
        )
        # get the items in the histogram
        fig.show()


if __name__ == "__main__":
    visualize()
