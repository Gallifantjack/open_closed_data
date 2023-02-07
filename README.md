# Author information of ICU papers and Biobank papers.

This repository contains the code to scrape all ICU related papers and UK Biobank on pubmed between 2010-2022.

## Strategy
Data is extracted from Pubmed using a pipeline based off [here](https://github.com/joxang/health_ai_end_to_end)

Pubmed (MEDLINE) is searched using Bio Entrez API for all papers related to ICU, with loop to get around 10,000 retmax.

Enter own email address and API key to run the code. This can be found by logging into NCBI and going to https://www.ncbi.nlm.nih.gov/account/settings/

## Search terms

- ICU PubMed search strategy is based on [Van De Sande et al., 2021](https://doi.org/10.1007/s00134-021-06446-7), and has been vetted by ICU physicians LC + JG.
- UK Biobank PubMed search strategy combines all papers related to ("UK Biobank") OR ("United Kingdom Biobank")

## Metadata

The following metadata is extracted:

- title
- abstract
- authors
- publication date
- journal
- pmid
- mesh terms

## Data

The data is stored in the `data` folder. The data is split into two files:

- `pubmed_icu_papers.csv` - all papers related to ICU
- `pubmed_biobank_papers.csv` - all papers related to UK Biobank
