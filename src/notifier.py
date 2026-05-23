# src/notifier.py
import json
import http.client
import base64

class MailjetNotifier:
    def __init__(self, api_key=None, secret_key=None, sender_email=None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.sender_email = sender_email

    def is_configured(self):
        """Validates if the user has provided all required Mailjet credentials."""
        return all([self.api_key, self.secret_key, self.sender_email])

    def send_trade_alert(self, ticker, action, headline, details):
        """
        Dispatches a structured operational alert via Mailjet's V3.1 Send API.
        Fails silently back to terminal logs if credentials are unconfigured or invalid.
        """
        if not self.is_configured():
            return False

        try:
            # Construct Basic Auth header string safely
            auth_string = f"{self.api_key}:{self.secret_key}"
            encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

            conn = http.client.HTTPSConnection("api.mailjet.com")
            headers = {
                "Authorization": f"Basic {encoded_auth}",
                "Content-Type": "application/json"
            }

            # Define high-visibility email styling properties based on trade action
            color_theme = "#00cc66" if action == "BUY" else "#ff3333" if action == "SELL" else "#ff9900"
            
            email_html = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd; border-radius: 8px; max-width: 600px;">
                <h2 style="color: {color_theme}; border-bottom: 2px solid {color_theme}; padding-bottom: 10px;">
                    📊 Bloomberg AI Terminal Alert: {action} {ticker}
                </h2>
                <p><strong>Market Event:</strong> {headline}</p>
                <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid {color_theme}; margin: 15px 0;">
                    <strong>Execution Details:</strong><br/>{details}
                </div>
                <p style="font-size: 11px; color: #888; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px;">
                    Asynchronous Automated Execution Engine • Production Workspace Instance
                </p>
            </div>
            """

            payload = json.dumps({
                "Messages": [
                    {
                        "From": {
                            "Email": self.sender_email,
                            "Name": "Bloomberg AI Terminal"
                        },
                        "To": [
                            {
                                "Email": self.sender_email,  # Sends notification alerts back to yourself
                                "Name": "Terminal Administrator"
                            }
                        ],
                        "Subject": f"🚨 [TERMINAL ALERT] {action} {ticker} Execution Triggered",
                        "HTMLPart": email_html
                    }
                ]
            })

            conn.request("POST", "/v3.1/send", payload, headers)
            response = conn.getresponse()
            res_data = response.read().decode()
            conn.close()

            return response.status == 200
        except Exception:
            # Shield worker loop from network delays or incorrect credential errors
            return False