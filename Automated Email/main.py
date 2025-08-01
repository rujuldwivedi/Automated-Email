import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# --- Step 1: Auth with Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-creds.json", scope)
client = gspread.authorize(creds)

# --- Step 2: Read Sheet ---
sheet = client.open("Recruiters").sheet1  # Adjust name if needed
data = sheet.get_all_records()
df = pd.DataFrame(data)

# --- Step 3: Track Last Row ---
STATE_FILE = "last_row.txt"
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        last_row = int(f.read().strip())
else:
    last_row = 0

# --- Step 4: Filter New Rows ---
new_rows = df.iloc[last_row:]
if new_rows.empty:
    print("✅ No new rows to send.")
    exit()

# --- Step 5: Email Sender Setup ---
EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

def send_email(to, name, job_id, job_link):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to
    msg["Subject"] = "Reaching Out for Referral Opportunity"

    body = f"""
    Hi {name},

    I hope you're doing well. I recently came across a position at your company that aligns with my background and interests. 
    I’d be truly grateful if you could consider referring me for the role.

    👉 Job ID: {job_id or 'N/A'}
    🔗 Job Link: {job_link or 'Not provided'}

    Please find my resume attached here: [Insert your resume link]

    Thank you so much in advance!

    Best,  
    Rujul Dwivedi  
    """

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        print(f"📩 Sent to {to}")

# --- Step 6: Send Emails for New Rows ---
for _, row in new_rows.iterrows():
    try:
        send_email(row["Email"], row["Name"], row.get("Job ID", ""), row.get("Job Link", ""))
    except Exception as e:
        print(f"❌ Failed for {row['Email']}: {e}")

# --- Step 7: Update Last Row Tracker ---
with open(STATE_FILE, "w") as f:
    f.write(str(len(df)))

print("✅ Done processing all new rows.")
