from flask import Flask, request, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
import subprocess
import json

# Create Flask app with the current directory as the static folder
app = Flask(__name__, static_folder='./')

# Configure upload settings
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    # Serve your exact HTML file name
    return send_from_directory('./', 'FrontEndDemo.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No video part'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Run the analysis notebook on the uploaded video
        result = run_analysis(filepath)
        
        return jsonify(result)

def run_analysis(video_path):
    # Your exact notebook name
    notebook_path = 'itrackerprep.ipynb'
    
    try:
        # Run notebook with papermill
        output_path = 'executed_notebook.ipynb'
        subprocess.run([
            'papermill', 
            notebook_path, 
            output_path, 
            '-p', 'video_path', video_path
        ], check=True)
        
        # Read results from the executed notebook's output file
        try:
            with open('analysis_results.json', 'r') as f:
                results = json.load(f)
            return results
        except FileNotFoundError:
            # If your notebook doesn't create this file yet
            return {'message': 'Video processed successfully, but no results file found. Check your notebook output.'}
            
    except Exception as e:
        print(f"Error executing notebook: {str(e)}")
        return {'error': f'Analysis failed: {str(e)}'}

if __name__ == '__main__':
    # Enable debug mode for detailed error messages
    app.run(debug=True)