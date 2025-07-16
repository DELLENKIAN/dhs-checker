from flask import Flask, render_template, request, send_file
import os
import pandas as pd
import uuid

from dhs_checker_script import check_dhs_status

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return "No file uploaded."

    df = pd.read_csv(file)
print("COLUMNS IN UPLOADED FILE:", df.columns.tolist())  # ADD THIS LINE

for id_number in df['ID Number']:
    ...


    for id_number in df['ID Number']:
        status, counsellor = check_dhs_status(id_number)
        results.append({'ID Number': id_number, 'Status': status, 'Debt Counsellor': counsellor})

    output_df = pd.DataFrame(results)
    output_filename = f"{uuid.uuid4()}.csv"
    output_df.to_csv(output_filename, index=False)

    return send_file(output_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
