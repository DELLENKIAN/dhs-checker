from flask import Flask, request, render_template, send_file
import pandas as pd
from check_dhs import check_dhs_status

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    df = pd.read_csv(file)

    print("COLUMNS IN UPLOADED FILE:", df.columns.tolist())  # Debugging line

    results = []
    for id_number in df['ID Number']:
        status, counsellor = check_dhs_status(str(id_number))
        results.append({
            'ID Number': id_number,
            'Status': status,
            'Debt Counsellor': counsellor
        })

    output_df = pd.DataFrame(results)
    output_filename = 'dhs_results.csv'
    output_df.to_csv(output_filename, index=False)

    return send_file(output_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
