from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from sec10k import run_script

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Flask server activated'

@app.route('/generate-visualizations', methods=['POST'])
def generate_visualizations():
    print("Reached generate_visualizations")
    if request.method == 'POST':
        data = request.json 
        ticker = data.get('ticker') 
        if ticker:
            directory = r'C:\Users\Ishita\Desktop\SEC10K' 
            print("going to run the script now")
            run_script(directory, ticker)
            plot_paths = {
                'consecutive_doc_comparison': f'/{ticker}/{ticker}consecutive_doc_comparison.png',
                'sentiment_analysis': f'/{ticker}/{ticker}sentiment_analysis.png',
                'question_answer_engine': f'/{ticker}/{ticker}question_answer_engine.png'
            }
            
            return jsonify(plot_paths)
        else:
            return jsonify({'error': 'Ticker not provided'}), 400
if __name__ == '__main__':
    app.run(debug=True)
