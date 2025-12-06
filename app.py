from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import re
import smtplib
import ssl
from email.message import EmailMessage
import html as html_module

# Load environment variables from .env in root
load_dotenv()

app = Flask(__name__)
CORS(app)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Backend is running"}), 200

def send_email_to_owner(name: str, sender_email: str, message_text: str) -> None:
    """Send contact form submission via Gmail SMTP"""
    
    # Load credentials from environment
    gmail_user = os.environ.get("MAIL_USERNAME")
    gmail_pass = os.environ.get("MAIL_PASSWORD")
    mail_to = os.environ.get("MAIL_TO", gmail_user)
    
    if not gmail_user or not gmail_pass:
        raise RuntimeError("Missing MAIL_USERNAME or MAIL_PASSWORD in .env file")
    
    # Create email message
    msg = EmailMessage()
    msg["Subject"] = f"Portfolio Contact: {name}"
    msg["From"] = gmail_user
    msg["To"] = mail_to
    msg["Reply-To"] = sender_email
    
    # Plain text version
    plain_text = f"""
New contact form submission from your portfolio:

Name: {name}
Email: {sender_email}

Message:
{message_text}

---
Reply directly to this email to respond to {sender_email}
"""
    msg.set_content(plain_text)
    
    # HTML version
    safe_name = html_module.escape(name)
    safe_email = html_module.escape(sender_email)
    safe_message = html_module.escape(message_text).replace("\n", "<br>")
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #135bec; color: white; padding: 20px; border-radius: 5px; }}
        .content {{ background: #f9f9f9; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .field {{ margin: 15px 0; }}
        .label {{ font-weight: bold; color: #135bec; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📧 New Portfolio Contact</h2>
        </div>
        <div class="content">
            <div class="field">
                <span class="label">From:</span> {safe_name}
            </div>
            <div class="field">
                <span class="label">Email:</span> {safe_email}
            </div>
            <div class="field">
                <span class="label">Message:</span><br>
                <p>{safe_message}</p>
            </div>
        </div>
        <div class="footer">
            Reply directly to this email to respond to {safe_email}
        </div>
    </div>
</body>
</html>
"""
    msg.add_alternative(html_content, subtype="html")
    
    # Send email with fallback ports
    context = ssl.create_default_context()
    
    # Try port 587 (STARTTLS) first
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(gmail_user, gmail_pass)
            server.send_message(msg)
            print(f"✓ Email sent successfully via port 587 from {sender_email}")
            return
    except Exception as e:
        print(f"Port 587 failed: {e}. Trying port 465...")
    
    # Fallback to port 465 (SSL)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=30) as server:
        server.login(gmail_user, gmail_pass)
        server.send_message(msg)
        print(f"✓ Email sent successfully via port 465 from {sender_email}")

@app.route("/api/contact", methods=["POST"])
def contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json(silent=True) or {}
        
        # Extract and validate fields
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        message = (data.get("message") or "").strip()
        
        # Validation
        if not name or not email or not message:
            return jsonify({"error": "All fields are required"}), 400
        
        if not EMAIL_RE.match(email):
            return jsonify({"error": "Please provide a valid email address"}), 400
        
        if len(name) < 2:
            return jsonify({"error": "Name must be at least 2 characters"}), 400
        
        if len(message) < 10:
            return jsonify({"error": "Message must be at least 10 characters"}), 400
        
        # Send email
        send_email_to_owner(name, email, message)
        
        return jsonify({
            "success": True,
            "message": "Thanks! Your message has been sent successfully."
        }), 200
        
    except Exception as e:
        app.logger.exception("Failed to process contact form")
        return jsonify({
            "error": "Failed to send your message. Please try again later."
        }), 500

if __name__ == "__main__":
    # Check environment variables on startup
    if not os.environ.get("MAIL_USERNAME") or not os.environ.get("MAIL_PASSWORD"):
        print("⚠️  WARNING: MAIL_USERNAME or MAIL_PASSWORD not found in .env file")
    else:
        print(f"✓ Email configured for: {os.environ.get('MAIL_USERNAME')}")
    
    print("🚀 Starting Flask server on http://127.0.0.1:5000")
    print("📧 Contact form endpoint: http://127.0.0.1:5000/api/contact")
    app.run(host="127.0.0.1", port=5000, debug=True)