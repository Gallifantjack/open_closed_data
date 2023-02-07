# retrieve all articles from pubmed using search term, if retmax over 10,000 then loop retstart and retmax at 10,000 and on each loop, set retstart to +10,000 from previous loop

from datetime import datetime as dt

import numpy as np
import pandas as pd
from Bio import Entrez
from tqdm import trange


def search(query, retmax, mindate=None, maxdate=None, reldate=None):
    Entrez.email = "k1927130@kcl.ac.uk"
    Entrez.api_key = "0e05ceabf7ff6ad2daff4de85eb8ac10360a"
    handle = Entrez.esearch(
        db="pubmed",
        retmax=retmax,
        retmode="xml",
        term=query,
        mindate=mindate,
        maxdate=maxdate,
        datetype="edat",
    )
    results = Entrez.read(handle)
    return results


def fetch_details(id_list):
    ids = ",".join(id_list)
    Entrez.email = "k1927130@kcl.ac.uk"
    Entrez.api_key = "0e05ceabf7ff6ad2daff4de85eb8ac10360a"
    handle = Entrez.efetch(db="pubmed", retmode="xml", id=ids)
    results = Entrez.read(handle)
    return results


def parse_article(article):
    # Empty dict for each article
    article_dict = {}

    # PMID
    article_dict["pmid"] = str(article["MedlineCitation"]["PMID"])

    # Parse out the DOI, annoyingly it's mixed into PII fields and doesn't always seem to be there
    doi = np.nan

    for i in article["MedlineCitation"]["Article"]["ELocationID"]:
        if i.attributes["EIdType"] == "doi":
            doi = str(i)
        else:
            doi = np.nan

    article_dict["doi"] = doi

    # Title
    article_dict["title"] = article["MedlineCitation"]["Article"]["ArticleTitle"]

    # Abstract
    try:
        article_dict["abstract"] = "".join(
            article["MedlineCitation"]["Article"]["Abstract"]["AbstractText"]
        )
    except:
        article_dict["abstract"] = np.nan

    # Article dates
    try:  # Doesn't always seem to have a date
        article_date = "-".join(
            list(article["MedlineCitation"]["Article"]["ArticleDate"][0].values())
        )
        article_dict["article_date"] = dt.strptime(article_date, "%Y-%m-%d")
    except:
        pass

    # Date available on pubmed
    for i in article["PubmedData"]["History"]:
        if i.attributes["PubStatus"] == "pubmed":
            pubmed_date = "-".join(list(i.values())[:3])
            article_dict["pubmed_date"] = dt.strptime(pubmed_date, "%Y-%m-%d")

    # Article type
    try:
        article_dict["article_type"] = str(
            article["MedlineCitation"]["Article"]["PublicationTypeList"][0]
        )
    except:
        pass

    # Article language
    try:
        article_dict["lang"] = article["MedlineCitation"]["Article"]["Language"][0]
    except:
        pass

    # Long form journal
    try:
        article_dict["journal"] = article["MedlineCitation"]["Article"]["Journal"][
            "Title"
        ]
    except:
        pass

    # ISO Journal abbreviation
    try:
        article_dict["journal_short"] = article["MedlineCitation"]["Article"][
            "Journal"
        ]["ISOAbbreviation"]
    except:
        pass

    # Journal country
    try:
        article_dict["journal_country"] = article["MedlineCitation"][
            "MedlineJournalInfo"
        ]["Country"]
    except:
        pass

    # Authors
    authors = []
    try:  # Sometimes there aren't proper authors listed
        for author in article["MedlineCitation"]["Article"]["AuthorList"]:
            authors.append(author["LastName"] + " " + author["ForeName"])
    except:
        authors = np.nan

    article_dict["authors"] = authors

    # Affiliations
    affils = []
    try:
        for author in article["MedlineCitation"]["Article"]["AuthorList"]:
            affils.append(author["AffiliationInfo"][0]["Affiliation"])
    except:
        affils = np.nan

    article_dict["author_affils"] = affils

    # Article keywords
    try:
        article_dict["keywords"] = [
            str(i) for i in (article["MedlineCitation"]["KeywordList"][0])
        ]
    except:
        article_dict["keywords"] = np.nan

    # Article Mesh terms
    mesh_terms = []
    try:  # Not always mesh terms
        for i in article["MedlineCitation"]["MeshHeadingList"]:
            mesh_terms.append(str(i["DescriptorName"]))
    except Exception as e:
        mesh_terms = np.nan

    article_dict["mesh_terms"] = mesh_terms

    # References (if included)
    references_pmids = []
    try:  # References not always included
        for i in article["PubmedData"]["ReferenceList"][0]["Reference"]:
            references_pmids.append(str(i["ArticleIdList"][0]))
    except:
        references_pmids = np.nan

    article_dict["references_pmids"] = references_pmids

    return article_dict


# Search term
search_term = """(exp "Intensive Care Units"/ OR exp "Critical Care"/ OR (ICU OR IC OR ((intensive OR critical) ADJ3 (care OR therapy OR unit* OR patient* OR department\*)))"""

# create function called retrieve_articles to search pubmed using search term, if retmax over 10,000 then loop retstart and retmax at 10,000 and on each loop, set retstart to +10,000 from previous loop
def retrieve_articles(search_term, retmax, chunk_size=50, mindate=None, maxdate=None):
    # fetch the list of pmids from pubmed
    result = search(search_term, retmax, mindate, maxdate)

    # if retmax is over 10,000 then loop retstart and retmax at 10,000 and on each loop, set retstart to +10,000 from previous loop
    if retmax > 10000:
        # create empty list to store pmids
        id_list = []
        # set retstart to 0
        retstart = 0
        # set retmax to 10000
        retmax = 10000
        # while retstart is less than the total number of pmids
        while retstart < int(result["Count"]):
            # fetch the list of pmids from pubmed
            result = search(search_term, retmax, mindate, maxdate, retstart)
            # append the list of pmids to the empty list
            id_list.extend(result["IdList"])
            # add 10,000 to retstart
            retstart += 10000
            # print the new retstart
            print("Retstart is now " + str(retstart))
    else:
        # if retmax is less than 10,000 then just fetch the list of pmids from pubmed
        id_list = result["IdList"]

    search_time = dt.now()

    print(f"List of {len(id_list)} PMIDs retrieved of {result['Count']} results.")
    print("Downloading and parsing:")

    paper_list = []

    # Retrieve in chunks
    for chunk_i in trange(0, len(id_list), chunk_size):
        chunk = id_list[chunk_i : chunk_i + chunk_size]

        papers = fetch_details(chunk)

        for i, paper in enumerate(papers["PubmedArticle"]):
            paper_list.append(parse_article(paper))

    df = pd.DataFrame(paper_list)

    df["pmid"] = df.pmid.astype(int)

    most_recent_date = df.pubmed_date.max()

    return (df, search_time, most_recent_date)


article_df, search_time, most_recent_article_date = retrieve_articles(
    search_term=search_term, mindate=2010, maxdate=2022, retmax=200000, chunk_size=200
)

article_df.to_csv("pubmed_icu_articles.csv", index=False)
