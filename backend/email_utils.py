import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

def send_inquiry_email(name, email, phone, message, product):
    """Send inquiry email to Ankita"""
    try:
        # Email configuration
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        receiver_email = os.getenv("RECEIVER_EMAIL")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"New Rakhi Inquiry: {product['name']} from {name}"
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>New Rakhi Inquiry Received</h2>
            <p><strong>Product:</strong> {product['name']}</p>
            <p><strong>Price:</strong> ₹{product['price']}</p>
            <p><strong>Customer Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone}</p>
            <p><strong>Message:</strong> {message}</p>
            <hr>
            <p><em>This is an automated notification from AnkitaCreation Rakhi Website</em></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False