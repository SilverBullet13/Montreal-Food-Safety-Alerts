import yaml
from email.mime.text import MIMEText
import smtplib


def load_email_config():
    with open("./config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config["email"]


def send_email(subject, body, to_email, from_email, password):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, password)
        server.send_message(msg)


def notify_by_email(new_violations):
    if not new_violations:
        return

    config = load_email_config()
    sender = config["sender"]
    password = config["password"]
    recipient = config["recipient"]

    body = "\n\n".join([
        f"Établissement: {v['etablissement']}\n"
        f"Adresse: {v['adresse']}\n"
        f"Date: {v['date']}\n"
        f"Infraction: {v['description']}\n"
        f"Amande: {v['montant']}$"
        for v in new_violations
    ])

    send_email(
        subject="🚨 Nouvelles contraventions détectées 🚨",
        body=body,
        to_email=recipient,
        from_email=sender,
        password=password
    )
