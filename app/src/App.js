import React, { useState } from 'react';
import './App.css';

function App() {

  const [selectedCompany, setSelectedCompany] = useState('');
  const [visualizationsData, setVisualizationsData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleCompanySelect = (event) => {
    setSelectedCompany(event.target.value);
  };

  const fetchData = () => {
    setIsLoading(true);
    fetch('http://127.0.0.1:5000/generate-visualizations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ ticker: selectedCompany })
    })
    .then(response => response.json())
    .then(data => {
      setVisualizationsData(data);
      setIsLoading(false);
    })
    .catch(error => {
      console.error('Error fetching data:', error);
      setIsLoading(false);
    });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchData();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>SEC-EDGAR 10-K Filing Analysis</h1>
        <h5>Using NLP on financial texts, like the 10-K forms as a source of forward-looking information, we can generate meaningful insights into a company’s operations and finances. I have extracted Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations for 3 companies - Apple, NVIDIA and Adobe, ranging from 1995 - 2023, since it is more suitable to extract item sections rather than utilizing the entire document for analysis.</h5>
        <h3>Select a ticker for generating visual insights in any of these companies.</h3>
        <form onSubmit={handleSubmit}>
          <select
            value={selectedCompany}
            onChange={handleCompanySelect}
            style={{
              width: '80%',
              color: selectedCompany ? '#000000' : '#686868',
              fontStyle: selectedCompany ? 'normal' : 'italic'
            }}
          >
            <option value="" disabled style={{ color: '#686868', fontStyle: 'italic' }}>Select Company Ticker</option>
            <option value="AAPL">AAPL | Apple Inc.</option>
            <option value="NVDA">NVDA | NVIDIA</option>
            <option value="ADBE">ADBE | Adobe</option>
          </select>
          <button type="submit">Generate Insights</button>
        </form>
        {isLoading && <p>Loading...</p>}
        {visualizationsData && (
          <div>
            <p>Fetched from cache....</p>
            <h3>1. CONSECUTIVE DOCUMENT COMPARISON</h3>
            <h4>HYPOTHESIS -</h4>
            <h5>
            As per Lazy Prices, a paper proposed by Cohen et al., it asserts that when companies make active and significant changes 
in their reporting,
this provides an important signal about future performance.

I have compared each consecutive year’s MD&A for language with the previous one and checked for similarity index. Lower the similarity score would ideally indicate major changes in the company
and should be indicated by more positive returns on stock prices. Similarity scores generated via comparison are visualized here along with their stock prices.
            </h5>


            <h3>2. SENTIMENT ANALYSIS </h3>
            <h4>HYPOTHESIS -</h4>
            <h5>
            Since 10-Ks are forward-looking documents, the sentiments in them are indicative of the company's financial performance, 
business strategies, and future prospects.
Negative sentiments may indicate risks or weaknesses while positive sentiments may indicate optimism and areas of strength.
Neutral sentiments are generally factual and objective.

Here sentiments are plotted alongside their polarity score values. A positive polarity value indicates higher positive sentiments and negative polarity indicates higher negative sentiments.
            </h5>


            <h3>3. QUESTION-ANSWER ENGINE </h3>
            <h4>HYPOTHESIS -</h4>
            <h5>
            Using the latest report from 2023, qualitative and quantitative questions can be answered related to sales and profit margins.
These QA are also visualized in the graphs.
    Since the engine may not yield correct answers, the graph may not be completely reliable
but still would indicate an approximation of a company’s finances.
            </h5>
            <img src={`/${visualizationsData.consecutive_doc_comparison}`} alt="Consecutive Document Comparison" />
            <img src={visualizationsData.sentiment_analysis} alt="Sentiment Analysis" />
            <img src={visualizationsData.question_answer_engine} alt="Question Answer Engine" />
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
