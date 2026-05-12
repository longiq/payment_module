import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from stripe_payment import init_stripe, create_payment_intent, retrieve_payment_intent
from stripe_payment.exceptions import StripePaymentError

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = Flask(__name__)
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
init_stripe()


@app.route("/")
def index():
    return render_template("checkout.html",
                           publishable_key=STRIPE_PUBLISHABLE_KEY,
                           amount=5000,
                           currency="USD")


@app.route("/success")
def success():
    payment_intent_id = request.args.get("payment_intent")
    status, amount_display = "unknown", ""
    if payment_intent_id:
        try:
            result = retrieve_payment_intent(payment_intent_id)
            status = result.status.value
            amount_display = result.amount_display
        except StripePaymentError:
            pass
    return render_template("success.html",
                           payment_intent_id=payment_intent_id,
                           status=status,
                           amount_display=amount_display)


@app.route("/cancel")
def cancel():
    return render_template("cancel.html")


@app.route("/api/create-payment-intent", methods=["POST"])
def api_create_payment_intent():
    data = request.get_json() or {}
    try:
        result = create_payment_intent(
            amount=int(data.get("amount", 5000)),
            currency=data.get("currency", "usd"),
            metadata={"source": "payment_element_demo"},
        )
        return jsonify({"clientSecret": result.client_secret})
    except StripePaymentError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    print(f"\n→ Mở http://localhost:8080 trên browser\n")
    app.run(debug=True, port=8080)
