import os
import smtplib
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from email.message import EmailMessage

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "google-creds.json"
SPREADSHEET_NAME = "Recruiters"
LAST_ROW_TRACK_FILE = "last_row.txt"

GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

# === Step 3: Email Template ===
def generate_email(name, company, job_id, job_link):
    subject = f"Application for SWE role at {company}"
    if job_id:
        subject += f" - Job ID: {job_id}"

    body = f"""
Hi {name}, I hope this email finds you well. 

I am writing to express my keen interest in the Software Engineering position {job_link if job_link else ''} at {company}. As a recent graduate with a strong foundation in mathematics and computer science, I am eager to contribute to your team's success. 

My experience includes developing and deploying a BERT + LSTM NLP pipeline on enterprise-scale imbalanced data for Databricks during my recent internship and applied machine learning for option pricing using PINNs and LSTMs.
On the software engineering front, I have led the development of full-stack platforms using Spring Boot, MERN, and Django, and built production-ready systems with technologies like Kafka, Redis, Docker, and Firebase. I am also thorough with Core Programming and Data Structures and Algorithms.

I would appreciate the opportunity to discuss how my skills and experience can add value to {company}. Please feel free to reach out if you require any additional information. 

P.S. I’ve linked my resume [Link] for your reference. Thank you for your time and consideration.

Warm regards,
Rujul Dwivedi
📞 +91 96951 33900
📧 rujuldwivedi@icloud.com
🔗 Portfolio | LinkedIn | GitHub
"""

    return subject, body

def get_last_row_sent():
    try:
        with open(LAST_ROW_TRACK_FILE, "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 1

def update_last_row_sent(row_num):
    with open(LAST_ROW_TRACK_FILE, "w") as file:
        file.write(str(row_num))

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["From"] = GMAIL_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        smtp.send_message(msg)

def main():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).sheet1
    data = sheet.get_all_values()

    headers = data[0]
    rows = data[1:]
    last_row_sent = get_last_row_sent()

    for i, row in enumerate(rows[last_row_sent:], start=last_row_sent+1):
        try:
            email, name, company, job_id, job_link = row[0:5] + ["", ""][:5-len(row)]
            subject, body = generate_email(name, company, job_id, job_link)
            send_email(email, subject, body)
            print(f"Sent to {email}")
            update_last_row_sent(i)
        except Exception as e:
            print(f"Failed for row {i+1}: {e}")

if __name__ == "__main__":
    main()