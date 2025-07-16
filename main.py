from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from dhs_checker_script import check_id_status  # This must be your working DHS scraper
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')  # Renders form

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return "No file uploaded", 400

    df = pd.read_csv(file)
    if 'id_number' not in df.columns:
        return "CSV must have an 'id_number' column", 400

    results = []
    for id_number in df['id_number']:
        status, counsellor = check_dhs_status(str(id_number))
        results.append({
            'id_number': id_number,
            'debt_review_status': status,
            'debt_counsellor': counsellor
        })

    result_df = pd.DataFrame(results)
    output_filename = f"results_{uuid.uuid4().hex}.csv"
    result_df.to_csv(output_filename, index=False)

    return send_file(output_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
