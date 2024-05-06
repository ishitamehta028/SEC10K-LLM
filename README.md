# SEC EDGAR 10-K Filing Dashboard
This project aims to provide a comprehensive financial analysis dashboard utilizing Python and React. It leverages various technologies including natural language processing (NLP) and machine learning (ML) models from Hugging Face to perform sentiment analysis, document comparison, and question-answering tasks on financial documents.
The script generates visualizations and text summaries for 3 companies- AAPL, ADBE, NVDA i.e. Apple, Adobe, NVIDIA. 
For each analysis performed, the script provides insights into the company's financial performance and prospects.

The script for generating insights is written in Python and the interactive dashboard is based in React. Flask is used to expose the endpoint for calling API and generate requests.

## Introduction
The Form 10-K reports are typically long documents, while specific downstream analysis only relies on one or a few Item sections rather than utilizing the entire document. 
It is more suitable to apply NLP techniques on those specific Item sections while dropping other uninformative Item sections. Here, the script uses the sec-edgar package to download the filings from 
1995 - 2024 for the company ticker as specified and generates insights.

Financial NLP is used to perform 3 tasks via calling LLM Inference API from HuggingFace. These are document comparison for similarity checking, sentiment analysis on financial text and QA-engine for answering questions related to text.



## Tech Stack
 - ### Frontend:
React: 
 - ### Backend:
Python: Libraries for cleaning and merging - Beautiful Soup, re, os, HTML, datetime
Libraries for calling HuggingFace API - requests, pipeline, tokenizer, transformers 
Libraries for 



## Functionality
   ### 1.   Consecutive Document Comparison : 
   Compares each consecutive year's MD&A for language similarity and visualizes the similarity scores alongside stock prices.
   ### 2.   Sentiment Analysis: 
    Analyzes sentiments in the MD&A texts and plots sentiment scores along with polarity scores to indicate positive, negative, and neutral sentiments.
   ### 3.   Question-Answering: 
    Uses the latest report to answer qualitative and quantitative questions related to sales and profit margins. Visualizes the QA results for easy interpretation.


