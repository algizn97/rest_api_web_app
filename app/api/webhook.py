from sanic import Blueprint, json
from sqlalchemy import text
from app.database import AsyncSessionLocal
import hashlib

webhook_bp = Blueprint('webhook')

SECRET_KEY = "gfdmhghif38yrf9ew0jkf32"


def verify_webhook_signature(data: dict, signature: str) -> bool:
    """Check the webhook signature."""
    sign_string = (
        str(data['account_id']) +
        str(data['amount']) +
        str(data['transaction_id']) +
        str(data['user_id']) +
        SECRET_KEY
    )
    expected = hashlib.sha256(sign_string.encode()).hexdigest()
    print(f"Webhook sign: '{sign_string}' → {expected[:16]} | Got: {signature[:16]}")
    return expected == signature


@webhook_bp.post('/payments')
async def webhook_payment(request):
    """Process the payment webhook."""
    data = request.json
    transaction_id = data.get('transaction_id')
    account_id = data.get('account_id')
    user_id = data.get('user_id')
    amount = data.get('amount')
    signature = data.get('signature')

    # Check signature
    if not verify_webhook_signature(data, signature):
        return json({'error': 'Invalid signature'}, 400)

    # Check if transaction already processed
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT payment_id FROM payments WHERE transaction_id = :tx_id"),
            {"tx_id": transaction_id}
        )
        if result.fetchone():
            return json({'error': 'Transaction already processed'}, 409)

        # Create account if not exists
        result = await session.execute(
            text("SELECT account_id FROM accounts WHERE account_id = :account_id AND user_id = :user_id"),
            {"account_id": account_id, "user_id": user_id}
        )
        if not result.fetchone():
            await session.execute(
                text("INSERT INTO accounts (account_id, user_id, balance) VALUES (:account_id, :user_id, 0.0)"),
                {"account_id": account_id, "user_id": user_id}
            )

        # Save payment
        await session.execute(
            text("""
                INSERT INTO payments (transaction_id, user_id, account_id, amount) 
                VALUES (:tx_id, :user_id, :account_id, :amount)
            """),
            {"tx_id": transaction_id, "user_id": user_id, "account_id": account_id, "amount": amount}
        )

        # Balance update
        await session.execute(
            text("UPDATE accounts SET balance = balance + :amount WHERE account_id = :account_id"),
            {"amount": amount, "account_id": account_id}
        )

        await session.commit()
        return json({'status': 'Payment processed', 'transaction_id': transaction_id}, 200)
