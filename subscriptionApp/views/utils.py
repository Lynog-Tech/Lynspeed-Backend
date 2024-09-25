import requests
from django.conf import settings


def initialize_paystack_payment(user, plan):
    """
    Initialize a payment session with Paystack for a given user and plan.
    
    Args:
        user: The user initiating the payment.
        plan: The subscription plan for which payment is being made.
        
    Returns:
        A tuple containing the payment URL and a reference for the transaction,
        or (None, None) if initialization fails.
    """
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": user.email,
        "amount": int(plan.price * 100),  # Paystack expects amount in kobo
        "metadata": {
            "plan_id": plan.id,
            "user_id": user.id
        }
    }

    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        payment_data = response.json()
        payment_url = payment_data['data']['authorization_url']
        reference = payment_data['data']['reference']
        return payment_url, reference
    return None, None

def verify_paystack_payment(reference):
    """
    Verify a payment with Paystack using the transaction reference.
    
    Args:
        reference: The Paystack transaction reference.
        
    Returns:
        A tuple containing a boolean indicating success and payment info,
        or (False, None) if verification fails.
    """
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        payment_data = response.json()
        if payment_data['data']['status'] == 'success':
            return True, {
                "amount": payment_data['data']['amount'] / 100,  # Convert back to naira
                "transaction_id": payment_data['data']['id'],
                "plan_id": payment_data['data']['metadata']['plan_id'],
                "user_id": payment_data['data']['metadata']['user_id']
            }
    return False, None
