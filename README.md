# Open vs Closed datasets extraction pipeline

This repository contains the code for the extraction pipeline of the Open vs Closed datasets.

Data is extracted from Pubmed using a pipeline based off [here](https://github.com/joxang/health_ai_end_to_end):

Pubmed is searched using Bio Entrez API for all papers related to AI.

Methods of getting ICU subset

1. Re- search PubMed search strategy:

- (intensive care unit(tiab) OR ICU(tiab) OR critically ill(tiab)).

2. Use JZ NLP to label papers as ICU related

- see 4_char

3. Use dictionary of terms

- see 56 of 4b

The following metadata is extracted:

- title
- abstract
- authors
- publication date
- journal
- pmid
- mesh terms

All papers related to AI are included in the dataset.

A subgroup label of critical care is also included.

# Todo:

## Demo

- Run pipeline on all papers since 2020
  - including all AI related papers
