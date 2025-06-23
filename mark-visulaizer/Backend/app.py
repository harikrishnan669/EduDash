from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Grade assignment
#def assign_grade(percentage):
 #   if percentage >= 90:
  #      return 'A+'
   # elif percentage >= 75:
    #    return 'A'
    #elif percentage >= 60:
     #   return 'B'
    #elif percentage >= 50:
     #   return 'C'
    #else:
     #   return 'Fail'

# Power BI refresh
def refresh_power_bi_dataset():
    tenant_id = os.getenv("PBI_TENANT_ID")
    client_id = os.getenv("PBI_CLIENT_ID")
    client_secret = os.getenv("PBI_CLIENT_SECRET")
    group_id = os.getenv("PBI_GROUP_ID")
    dataset_id = os.getenv("PBI_DATASET_ID")

    if not all([tenant_id, client_id, client_secret, group_id, dataset_id]):
        print("Missing Power BI credentials in .env")
        return False

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://analysis.windows.net/powerbi/api/.default'
    }

    token_r = requests.post(token_url, data=token_data)
    if token_r.status_code != 200:
        print("Failed to get Power BI token:", token_r.text)
        return False

    access_token = token_r.json().get("access_token")
    if not access_token:
        print("No access token received from Power BI.")
        return False
    # POWERBI REST API
    refresh_url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/refreshes"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    refresh_r = requests.post(refresh_url, headers=headers)
    if refresh_r.status_code == 202:
        print("Power BI dataset refresh triggered successfully.")
        return True
    else:
        print("Power BI refresh failed:", refresh_r.text)
        return False

# Upload & analyze route
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'excel' not in request.files:
            print("[ERROR] No file part in request")
            return {'status': 'error', 'message': 'No file part'}, 400

        file = request.files['excel']
        if file.filename == '':
            print("[ERROR] No file selected")
            return {'status': 'error', 'message': 'No file selected'}, 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        print(f"[INFO] File uploaded to: {file_path}")

        df = pd.read_excel(file_path)
        print(f"[INFO] Excel file loaded with shape {df.shape}")
        print(f"[DEBUG] Columns in Excel: {df.columns.tolist()}")

        # Ignore personal info fields
        ignored = ['university reg. no', 'roll no', 'name', 'total']
        subject_cols = [col for col in df.columns if col.strip().lower() not in ignored]

        # Make sure subject columns are numeric
        for col in subject_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop old Total column if exists
        if 'Total' in df.columns:
            df.drop(columns=['Total'], inplace=True)

        # Add new analysis columns
        df['Total'] = df[subject_cols].sum(axis=1)
        df['Percentage'] = df['Total'] / (len(subject_cols) * 100) * 100
        #df['Grade'] = df['Percentage'].apply(assign_grade)

        output_path = os.path.join(UPLOAD_FOLDER, 'analyzed.csv')
        df.to_csv(output_path, index=False)
        print(f"[SUCCESS] Analyzed file saved to: {output_path}")

        success = refresh_power_bi_dataset()
        print(f"[INFO] Power BI refresh: {'Success' if success else 'Failed'}")

        return {'status': 'success'}

    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        return {'status': 'error', 'message': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
