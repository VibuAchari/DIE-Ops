from flask import Flask, render_template, request, jsonify
import requests
import os

# Flask UI server
app = Flask(__name__)

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000"   # your running FastAPI service

# -------------------------------
# Home (Overview Dashboard)
# -------------------------------
@app.route("/")
def home():
    return render_template("home.html")

# -------------------------------
# Customer Explorer
# -------------------------------
@app.route("/customers")
def customers():
    return render_template("customers.html")

@app.route("/search_customer", methods=["POST"])
def search_customer():
    customer_id = request.form.get("customer_id")
    if not customer_id:
        return "<p class='text-red-600'>Customer ID required.</p>"

    # Call FastAPI
    resp = requests.post(f"{API_URL}/score/customer", json={"customer_id": customer_id})

    if resp.status_code != 200:
        return "<p class='text-red-600'>Customer not found.</p>"

    data = resp.json()

    # Map backend fields to card fields
    customer = {
        "customer_id": customer_id,
        "churn_prob": round(data.get("churn_prob", 0), 4),
        "cltv": round(data.get("cltv", 0), 4),
        "uplift": round(data.get("uplift", 0), 4),
        "action": data.get("action", "—"),
        "reason": data.get("reason")
    }

    return render_template("components/customer_card.html", customer=customer)


# -------------------------------
# Campaign Builder
# -------------------------------
@app.route("/campaign")
def campaign():
    return render_template("campaign.html")

@app.route("/run_campaign", methods=["POST"])
def run_campaign():
    budget = float(request.form.get("budget", 5000))
    cost = float(request.form.get("cost", 20))

    # Call FastAPI recommendation endpoint
    payload = {"budget": budget, "cost_per_action": cost}
    resp = requests.post(f"{API_URL}/recommend", json=payload)
    return jsonify(resp.json())

# -------------------------------
# Reports Page
# -------------------------------
@app.route("/reports")
def reports():
    # list generated HTML files
    reports_dir = "output"
    files = []
    if os.path.exists(reports_dir):
        for f in os.listdir(reports_dir):
            if f.endswith(".html"):
                files.append(f)
    return render_template("reports.html", files=files)

# -------------------------------
# Run Flask app
# -------------------------------
if __name__ == "__main__":
    app.run(port=5001, debug=True)
