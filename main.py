from flask import Flask, request, render_template, send_file
import csv
import os
import uuid
from dhs_checker_script import check_id_status

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return "Only CSV files are allowed", 400

    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.csv")
    output_path = os.path.join(UPLOAD_FOLDER, f"results_{uuid.uuid4()}.csv")
    file.save(input_path)

    with open(input_path, newline='') as infile, open(output_path, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        writer.writerow(['ID Number', 'Debt Review Status', 'Debt Counsellor'])

        for row in reader:
            id_number = row[0].strip()
            if not id_number or not id_number.isdigit():
                continue
            status, dc_name = check_id_status(id_number)
            writer.writerow([id_number, status, dc_name])

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
