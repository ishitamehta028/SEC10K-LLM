# SEC EDGAR 10-K Filing Dashboard
This project aims to provide a comprehensive financial analysis dashboard utilizing Python and React. It leverages various technologies including natural language processing (NLP) and machine learning (ML) models from Hugging Face to perform sentiment analysis, document comparison, and question-answering tasks on financial documents.
The script generates visualizations and text summaries for 3 companies- AAPL, ADBE, NVDA i.e. Apple, Adobe, and NVIDIA using Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations. For each analysis performed, the script provides insights into the company's financial performance and prospects.

The script for generating insights is written in Python and the interactive dashboard is based on React. Flask is used to expose the endpoint for calling API and generating requests.

## Introduction
The Form 10-K reports are typically long documents, while specific downstream analysis only relies on one or a few Item sections rather than utilizing the entire document. 
It is more suitable to apply NLP techniques on those specific Item sections while dropping other uninformative Item sections. Here, the script uses the sec-edgar package to download the filings from 1995 - 2023 for the company ticker as specified and generates insights.

10-K Data is extracted from SEC-EDGAR website, and Item 7. MD&A is extracted for all 10-K filings, cleaned and merged into a dictionary with years as keys. Then LLM APIs are called to generate insights and visualizations. This can be accessed via a dashboard which is built in React.

Financial NLP is used to perform 3 tasks via calling LLM Inference API from HuggingFace. These are  - document comparison for similarity checking, sentiment analysis on financial text and QA-engine for answering questions related to text.

Loading the script for a specific ticker can take upto 5 minutes, hence a caching system is used to pre-load the output and store in directory with the ticker name. The dashboard prints the output from pre-loaded visualizations.


## Tech Stack

 - ### Frontend:
  React - React is dynamic, responsive, provides great UI, is versatile and is easy to integrate with backend APIs
 - ### Backend:
  Python: Python is an incredibly powerful language for data-extraction, managing, preprocessing and handling. Additionally, the packages make it convenient to call powerful ML models and APIs. Here data extraction, cleaning, merging, analysing, plotting, generating insights. To interface with the backend, Flask is used that helps expose endpoints. 
 - Libraries for cleaning and merging - Beautiful Soup, re, os, HTML, datetime, spacy, nltk
 - Libraries for generating insights = numpy, matplotlib
 - Libraries for calling HuggingFace API - requests, pipeline, tokenizer, transformers 
 - Libraries for exposing endpoint : Flask, JSONify, string



## Functionality
   ### 1.   Consecutive Document Comparison for similarity scoring : 
   Compares each consecutive year's MD&A for language similarity and visualizes the similarity scores alongside stock prices using sentence transformers model MiniLM.
   HYPOTHESIS - As per Lazy Prices, a paper proposed by Cohen et al., asserts that when companies make active and significant changes in their reporting, this provides an important signal about future performance. I have compared each consecutive year’s MD&A for language with the previous one and checked for similarity index. Lower the similarity score would ideally indicate major changes in the company and should be indicated by more positive returns on stock prices. Similarity scores generated via comparison are visualized here along with their stock prices.

   ### 2.   Sentiment Analysis on Financial text: 
   Analyzes sentiments in the MD&A texts and plots sentiment scores along with polarity scores to indicate positive, negative, and neutral sentiments and polarity of MD&A texts for all years.
   HYPOTHESIS - Since 10-Ks are forward-looking documents, the sentiments in them are indicative of the company's financial performance, business strategies, and future prospects. Negative sentiments may indicate risks or weaknesses while positive sentiments may indicate optimism and areas of strength. Neutral sentiments are generally factual and objective.

   ### 3.   Question-Answering Engine: 
   Uses the latest report to answer qualitative and quantitative questions related to sales and profit margins using distilbert. Visualizes the QA results for easy interpretation. 
   HYPOTHESIS - Using the latest report from 2023, qualitative and quantitative questions can be answered related to sales and profit margins. These QA are also visualized in the graphs. 


