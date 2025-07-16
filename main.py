from flask import Flask, request, render_template_string, send_file
import csv
import os
from check_dhs import check_dhs_status

app = Flask(__name__)

HTML_FORM = '''
<h1>DHS Checker Upload</h1>
<form method="post" enctype="multipart/form-data">
  <input type="file" name="file" accept=".csv">
  <input type="submit" value="Check">
</form>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return '⚠️ No file selected.'

        filepath = os.path.join('uploads', uploaded_file.filename)
        os.makedirs('uploads', exist_ok=True)
        uploaded_file.save(filepath)

        id_numbers = []
        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip header
            for row in reader:
                if row:
                    id_numbers.append(row[0].strip())

        results = []
        for id_num in id_numbers:
            print(f"🔎 Processing: {id_num}")
            status, dc_name = check_dhs_status(id_num)
            results.append([id_num, status, dc_name])

        output_path = "output.csv"
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID Number', 'Debt Review Status', 'Debt Counsellor'])
            writer.writerows(results)

        return send_file(output_path, as_attachment=True)

    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)



