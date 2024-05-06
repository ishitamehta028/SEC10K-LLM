# -*- coding: utf-8 -*-
"""SEC10K.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kRoOMOAwvDZ7Ockm1xwCELF5BpUy9PDO
"""

# pip install -U sec-edgar-downloader

from sec_edgar_downloader import Downloader
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import string
import nltk
from nltk.corpus import stopwords
from transformers import BertTokenizer
from transformers import pipeline
import re
import string
import yfinance as yf
nltk.download('stopwords')

import requests
from transformers import pipeline
import spacy
from spacy.lang.en import English
import os
from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup
from bs4 import ParserRejectedMarkup
import html
import datetime
nlp = spacy.load("en_core_web_sm")


"""# Item 7. MD&A EXTRACTION FROM SEC-EDGAR 10-K FILINGS"""


def clean_extract_item7(text):
    """
    Extracts and cleans the text content of Item 7 (MD&A) from 10-K filings.

    Parameters:
    text (str): The text containing the 10-K financial report.

    Returns:
    str or None: The cleaned text content of Item 7 (MD&A) if found, otherwise None.
    """
    # extract body content
    if '<body>' in text:
        soup = BeautifulSoup(text, "html.parser")
        body_content = soup.find('body').get_text(separator='\n', strip=True)
    else:
        body_content = text

    # clean 10-K filing
    body_content = html.unescape(body_content)
    body_content = body_content.encode("ascii", "ignore").decode()
    body_content = re.sub(r'https?://\S+|www\.\S+', '', body_content)
    body_content = re.sub(r'(?<!\n)\s+', ' ', body_content)

    # delete TABLE OF CONTENTS
    pattern = re.compile(re.escape(r'TABLE OF CONTENTS') + r'(.*?)' + re.escape(r'Item 10.'), re.DOTALL)
    body_content = pattern.sub('', body_content)

    # Extract Item 7 MD&A via regex
    pattern = re.compile(r"Item\s+7\.\s*MANAGEMENT(?:’|'|’|‘)?s?\s*DISCUSSION\s+AND\s+ANALYSIS\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS(.*?)Item\s*7A\.?", re.DOTALL | re.IGNORECASE)
    match = pattern.search(body_content)

    if match:
        section_content = match.group(1).strip()
        return section_content
    else:
        return None

def extract_year(directory):
    """
    Extracts the year from a directory name and returns it as a four-digit integer.

    Parameters:
    directory (str): A string representing the directory name from SEC filings.

    Returns:
    int: The four-digit year extracted.
    """
    current_year = datetime.datetime.now().year % 100
    year = int(directory.split('-')[1])
    if year <= current_year:
        return 2000 + year
    else:
        return 1900 + year

def access_submission_files(directory, ticker):
    """
    Accesses the submission files for a given ticker, extracts the MD&A section
    from each file, and returns a dictionary containing the cleaned MD&A texts
    mapped to their respective years.

    Parameters:
    directory (str): The directory containing the SEC filings.
    ticker (str): The ticker symbol of the company.

    Returns:
    dict: A dictionary with keys as years and values are cleaned MD&A texts.
    """

    data = {}
    ticker_dir = os.path.join(directory, 'sec-edgar-filings', ticker, '10-K')
    for root, dirs, files in os.walk(ticker_dir):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            submission_file_path = os.path.join(dir_path, 'full-submission.txt')

            if os.path.isfile(submission_file_path):
                year = extract_year(dir)

                with open(submission_file_path, "r", encoding="utf-8") as file:
                  text = file.read()
                try:
                  clean_text = clean_extract_item7(text)
                  if clean_text:
                    data[year]= clean_text.lower()
                except ParserRejectedMarkup as e:
                  print(f"Parser rejected markup for file: {submission_file_path}. Skipping...")
                  continue
                except Exception as e:
                  print(f"An error occurred while processing file: {submission_file_path}. Error: {e}")
                  continue
    MDA = dict(sorted(data.items()))
    return MDA




"""# LLM API INFERENCE TO GENERATE INSIGHTS

1.  Document Comparison for similarity checking
2.  Sentiment Analysis
3.  QAnswering

# 1. Document Comparison
Of consecutive years and comparing with the stock prices
"""

#HERE WE WILL TAKE DIFFERENT DOCUMENTS SEC7 MDA AND COMPARE TO EACH OTHER TO GENERATE SCORE
import requests
API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": "Bearer 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"}

def dquery(payload):
	"""
    Sends a query payload API for sentence embedding generation.

    Parameters:
    payload (dict): A dictionary containing the query payload.

    Returns:
    dict: The JSON response with the similarity score for the embeddings.
  """
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

def document_comparison(MDA_text) :
  """
    Compares the MD&A texts of consecutive years using sentence
    transformers model MiniLM via API call.

    Parameters:
    MDA_text (dict): A dictionary, keys are years and values are MD&A texts.

    Returns:
    dict: A dictionary where keys represent pairs of consecutive years,
          and values represent the similarity scores between the MD&A texts.
  """
  document_comparison = {}

  for i in range(1, len(MDA_text)) :
    current_year = list(MDA_text.keys())[i]
    previous_year = list(MDA_text.keys())[i - 1]
    current_text = MDA_text[current_year]
    previous_text = MDA_text[previous_year]

    input_data = {
            "inputs": {
                "source_sentence": current_text,
                "sentences": [previous_text]
            }
        }
    output = dquery(input_data)
    key = f"{previous_year}-{current_year}"
    document_comparison[key] = output[0]

  return document_comparison

def plot_document_comparison(document_comparison, directory, ticker):
    """
    Plots the document similarity scores and the stock prices for the given ticker.

    Parameters:
    document_comparison (dict): A dictionary containing document similarity scores.
    directory(str) : path to directory
    ticker (str): The ticker symbol of the company.

    Returns: None
    """

    years = list(document_comparison.keys())
    similarity_scores = list(document_comparison.values())
    start_year = int(years[0].split('-')[0])
    end_year = int(years[-1].split('-')[1])

    plt.figure(figsize=(10, 12))

    # #PLOT SIMILARITY SCORES GRAPH
    plt.subplot(2, 1, 1)
    plt.plot(years, similarity_scores, marker='o', linestyle='-')
    plt.title(f'Document Similarity Scores 1995-2023 for {ticker}')
    plt.xlabel('Year Interval')
    plt.ylabel('Similarity Score')
    plt.xticks(rotation=45)
    plt.grid(True)

    #PLOT TICKER STOCK PRICES HERE

    stock_data = yf.download(ticker, start=f'{start_year}-01-01', end=f'{end_year}-12-31')
    plt.subplot(2, 1, 2)
    plt.plot(stock_data['Adj Close'], color='orange', label='Stock Prices')
    plt.xlabel('Year')
    plt.ylabel('Stock Prices')
    plt.title(f'Stock Prices for {ticker}')
    plt.xticks(rotation=45)
    plt.grid(True)

    plt.tight_layout()
    plot_path = os.path.join(directory, ticker, f'{ticker}consecutive_doc_comparison.png')
    plt.savefig(plot_path)

    plt.show()


"""# 2. Sentiment Analysis
Conduct a sentiment analysis on chunks, average the score of all chunks to get sentiments of the doc and calculate a polarity score accordingly
"""

def tokenize_text(text) :
  """
    Tokenizes the input text using BERT tokenizer and removes English stopwords.
    This is useful when chunking.

    Parameters:
    text (str): The input text to be tokenized.

    Returns:
    list: A list of tokens.
  """
  tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
  tokens = tokenizer.tokenize(text)
  stop_words = set(stopwords.words('english'))
  tokens = [token for token in tokens if token.lower() not in stop_words]

  return tokens

# Chunking Function for parsing into FinBert

def text_to_chunks(text):
    """
    Splits the input text into chunks. Word limit- 300 words per chunk.

    Parameters:
    text (str): The input text to be chunked.

    Returns:
    list: A list of last 3 chunks from long-text input.
    This is so that API limit does not run out.
    """
    chunks = [[]]
    chunk_total_words = 0

    sentences = nlp(text)

    for sentence in sentences.sents:
        words_in_sentence = len(sentence.text.split(" "))

        if chunk_total_words + words_in_sentence > 300:
            chunks.append([])
            chunk_total_words = 0

        chunk_total_words += words_in_sentence
        chunks[-1].append(sentence.text)

    chunks = chunks[-3:] #Storing only last 3 chunks because otherwise API might run out of limit. The last lines in a text generally provide a summary into the content and can be useful
    return chunks

import time

def squery(payload, max_retries=5, retry_delay=5):
    """
    Sends a query payload to the API for sentiment analysis using the FinBERT model.

    Parameters:
    payload (dict): A dictionary containing the query payload.
    max_retries (int): Maximum number of retries.
    retry_delay (int): Number of seconds to wait between retries.

    Returns:
    dict: The JSON response containing the sentiment analysis results.
    """
    API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
    headers = {"Authorization": "Bearer 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"}

    for _ in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            response_json = response.json()
            if 'error' in response_json and response_json['error'] == 'Model ProsusAI/finbert is currently loading':
                print("FinBERT model is still loading. Retrying after delay...")
                time.sleep(retry_delay)
            else:
                return response_json
        except Exception as e:
            print(f"Error: {e}. Retrying after delay...")
            time.sleep(retry_delay)

    raise Exception("Maximum number of retries reached. Unable to get response from the model.")

def sentiment_analysis(MDA_text) :
  """
  Analyzes the sentiment and polarity of MD&A texts for all years.

  Parameters:
  MDA_text (dict): A dictionary with keys as years and values are MD&A texts.

  Returns:
  tuple: A tuple containing two dictionaries: sentiment_scores, polarity_scores.

  sentiment_scores: Dict, keys are years and values are average sentiment scores for
  positive, negative, and neutral sentiments.
  polarity_scores: Dict, keys are years and values are polarity scores
  """

  sentiment_scores = {}
  polarity_scores = {}

  for year, text in MDA_text.items() :
    chunks = text_to_chunks(text)
    positive = []
    negative = []
    neutral = []

    try :
      for chunk in chunks :
        t = " ".join(chunk)
        if len(tokenize_text(t)) < 400 :
          output = squery({"inputs": t})

          positive_scores = [sentiment['score'] for sentiment in output[0] if sentiment['label'] == 'positive']
          negative_scores = [sentiment['score'] for sentiment in output[0] if sentiment['label'] == 'negative']
          neutral_scores = [sentiment['score'] for sentiment in output[0] if sentiment['label'] == 'neutral']
          positive.extend(positive_scores)
          negative.extend(negative_scores)
          neutral.extend(neutral_scores)

    except requests.exceptions.HTTPError as e:
            print(f"Error: {e}. Using sentiment scores obtained so far and generating graphs.")
            break

    avg_positive = sum(positive) / len(positive) if positive else 0
    avg_negative = sum(negative) / len(negative) if negative else 0
    avg_neutral = sum(neutral) / len(neutral) if neutral else 0
    #Calculate Polarity Values
    polarity_score = sum(positive) - sum(negative)

    sentiment_scores[year] = {'positive': avg_positive, 'negative': avg_negative, 'neutral': avg_neutral}
    polarity_scores[year] = polarity_score

  return sentiment_scores, polarity_scores

def plot_sentiment_scores(sentiment_scores, polarity_scores, directory, ticker):
    """
    Plots sentiment analysis scores and polarity scores for the given ticker.

    Parameters:
    sentiment_scores (dict): sentiment analysis scores for each year.
    polarity_scores (dict):  polarity scores for each year.
    directory(str) : path to directory
    ticker (str): The ticker symbol of the company.

    Returns: None
    """

    # PLOT SENTIMENTS
    years = list(sentiment_scores.keys())
    positive_scores = [sentiment_scores[year]['positive'] for year in years]
    negative_scores = [sentiment_scores[year]['negative'] for year in years]
    neutral_scores = [sentiment_scores[year]['neutral'] for year in years]

    fig, axs = plt.subplots(2, 1, figsize=(18, 12))
    bar_width = 0.4
    bar_positions = [year - bar_width for year in years]

    for year, pos, neu, neg in zip(years, positive_scores, neutral_scores, negative_scores):
        axs[0].bar(year - bar_width, pos, color='limegreen', label='Positive', width=bar_width)
        axs[0].bar(year, neu, color='gold', label='Neutral', width=bar_width)
        axs[0].bar(year + bar_width, neg, color='red', label='Negative', width=bar_width)

    axs[0].set_title(f'Sentiment Analysis Scores for {ticker}')
    axs[0].set_xlabel('Year')
    axs[0].set_ylabel('Sentiment Score')
    axs[0].set_xticks(years)
    axs[0].legend(['Positive', 'Neutral', 'Negative'], loc='upper right', ncol=1)

    # PLOT POLARITY SCORES
    axs[1].bar(years, polarity_scores.values(), label='Polarity Scores', color='lightblue')
    axs[1].set_title(f'Polarity Scores for {ticker}')
    axs[1].set_xlabel('Year')
    axs[1].set_ylabel('Polarity Score')
    axs[1].set_xticks(years)
    axs[1].legend()
    axs[1].grid(True)

    plt.tight_layout()
    plot_path = os.path.join(directory, ticker, f'{ticker}sentiment_analysis.png')
    plt.savefig(plot_path)

    plt.show()


"""# 3. Question-Answering Engine

no need to chunk or summarize, inbuilt batching system

"""

def qa(text, questions) :
  """
    question-answering on the given text using distilbert

    Parameters:
    text (str): the context text.
    questions (list): questions to be answered.

    Returns:
    list: A list of answers corresponding to questions.
  """
  qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad", tokenizer="distilbert-base-uncased")
  answers = []

  for question in questions:
    result = qa_pipeline(question=question, context=text)
    answers.append(result['answer'])
  for i, ans in enumerate(answers):
    print(f"Question {i+1}: {questions[i]}")
    print(f"Answer: {ans}\n")

  return answers

def extract_numerical_value(answer):
    """
    Extracts a numerical value from the answers in QA engine.

    Parameters:
    answer (str): The answer string from which to extract the numerical value.

    Returns:
    float or None: The numerical value extracted from the answer.
    """
    numerical_value = re.findall(r'\d+\.*\d*', answer)
    if numerical_value:
        return float(numerical_value[0])
    else:
        return None

def plot_qa(answers, directory, ticker) :
  """
    Plots the  values from the QA engine for net sales and gross profit

    Parameters:
    answers (list): A list of answers.
    directory(str) : path to directory
    ticker (str): The ticker symbol of the company.

    Returns: None
  """
  net_sales = {}
  gross_profit = {}

  years = [2023,2022,2021]

  #NET SALES
  for i in range(3):
        answer = answers[i]
        numerical_value = extract_numerical_value(answer)
        if numerical_value:
            net_sales[years[i]] = numerical_value

  plt.figure(figsize=(10, 12))

  plt.subplot(2, 1, 1)
  plt.plot(net_sales.keys(), net_sales.values(), marker='o', color='blue')
  plt.title(f'Net Sales for {ticker}')
  plt.xlabel('Year')
  plt.ylabel('Amount ($ million/billion)')
  plt.grid(True)

  #GROSS PROFIT
  for i in range(3, 6):
        answer = answers[i]
        numerical_value = extract_numerical_value(answer)
        if numerical_value:
            gross_profit[years[i-3]] = numerical_value

  plt.subplot(2, 1, 2)
  plt.plot(gross_profit.keys(), gross_profit.values(), marker='o', color='green')
  plt.title(f'Gross Profit for {ticker}')
  plt.xlabel('Year')
  plt.ylabel('Amount ($ million/billion)')
  plt.grid(True)

  plt.tight_layout()
  plot_path = os.path.join(directory, ticker, f'{ticker}question_answer_engine.png')
  plt.savefig(plot_path)
  plt.show()

def run_script(directory, ticker) :
  """
    Checks for cached results and outputs it.
    Else, runs the script to generate visualizations on the financial reports.

    Parameters:
    directory (str): The directory containing the SEC filings.
    ticker (str): The ticker symbol of the company.

    Returns: None
  """


  ## THIS IS THE TEXT FOR THE PLOTS TO BE DISPLAYED

  text_for_doc = """
    1. CONSECUTIVE DOCUMENT COMPARISON\n
    **HYPOTHESIS** -\nAs per Lazy Prices, a paper proposed by Cohen et al., it asserts that when companies make active and significant changes in their reporting, \nthis provides an important signal about future performance.
    \nI have compared each consecutive year’s MD&A for language with the previous one and checked for similarity index. Lower the similarity score would ideally indicate major changes in the company \nand should be indicated by more positive returns on stock prices. Similarity scores generated via comparison are visualized here along with their stock prices.
    """
  text_for_sentiment = """
    2. SENTIMENT ANALYSIS\n
    **HYPOTHESIS** - \nSince 10-Ks are forward-looking documents, the sentiments in them are indicative of the company's financial performance, business strategies, and future prospects. \nNegative sentiments may indicate risks or weaknesses while positive sentiments may indicate optimism and areas of strength. \nNeutral sentiments are generally factual and objective.
    \nHere sentiments are plotted alongside their polarity score values. A positive polarity value indicates higher positive sentiments and negative polarity indicates higher negative sentiments.
    """
  text_for_qa = """
    3. QUESTION-ANSWER ENGINE\n
    **HYPOTHESIS** - \nUsing the latest report from 2023, qualitative and quantitative questions can be answered related to sales and profit margins. \nThese QA are also visualized in the graphs.
    Since the engine may not yield correct answers, the graph may not be completely reliable \nbut still would indicate an approximation of a company’s finances.
    """

  text_data = {
    'consecutive_doc_comparison': text_for_doc,
    'sentiment_analysis': text_for_sentiment,
    'question_answer_engine': text_for_qa
    }


  ## CHECKING FOR CACHING

  cache_dir = os.path.join(directory, ticker)
  if os.path.exists(cache_dir) :
    print("Fetching from cache....")
    plot_paths = {
            'consecutive_doc_comparison': os.path.join(cache_dir, f'{ticker}consecutive_doc_comparison.png'),
            'sentiment_analysis': os.path.join(cache_dir, f'{ticker}sentiment_analysis.png'),
            'question_answer_engine': os.path.join(cache_dir, f'{ticker}question_answer_engine.png')
              }

    for key, value in plot_paths.items():
      if os.path.exists(value):
        print(text_data[key])
        img = plt.imread(value)
        plt.figure(figsize=(18, 12))
        plt.imshow(img)
        plt.show()


  ## RUNNING THE SCRIPT

  else :
    print("running script....\n")
    if not os.path.exists(cache_dir) :
      os.makedirs(cache_dir)

    #Collect and store documents in a dictionary
    dl = Downloader("Georgia Tech", "ishim028@gmail.com", directory)
    print("Collecting documents....")
    dl.get("10-K", ticker, after="1995-01-01", before="2024-01-01")
    print("It may take a couple of minutes to generate visualizations....")
    MDA = access_submission_files(directory, ticker)

    #Consecutive Doc comparison
    document = document_comparison(MDA)
    print(text_for_doc)
    plot_document_comparison(document, directory, ticker)


    #Sentiment Analysis
    sentiment_scores, polarity_scores = sentiment_analysis(MDA)
    print(text_for_sentiment)
    plot_sentiment_scores(sentiment_scores, polarity_scores, directory, ticker)


    #QA Engine
    questions = [
    "What was the total net sales (in $) for the year 2023?",
    "What was the total net sales (in $) for the year 2022?",
    "What was the total net sales (in $) for the year 2021?",
    "What was the gross profit margin percentage for products and services in 2023?",
    "What was the gross profit margin percentage for products and services in 2022?",
    "What was the gross profit margin percentage for products and services in 2021?",
    "What are the key risks and uncertainties mentioned in the text that could impact the company's financial condition and results of operations in the future?",
    "What is the company's future projected profit (in $) for 2024?"
    ]
    print("loading QA engine....")
    answers = qa(MDA[2023], questions)
    print(text_for_qa)
    plot_qa(answers, directory, ticker)