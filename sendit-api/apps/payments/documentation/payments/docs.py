from drf_spectacular.utils import OpenApiExample



WEB_FUNDING_400_RESPONSE = OpenApiExample(
    '400 BAD REQUEST',
    summary='Missing or invalid amount',
    description='Returned when the `amount` field is missing or invalid.',
    value={'error': "Amount is required"},
    response_only=True,
    status_codes=['400']
)

WEB_FUNDING_200_RESPONSE = OpenApiExample(
    '200 OK',
    summary='Funding initiated successfully',
    description='Returned when a wallet funding transaction is successfully created and payload is generated.',
    value={
        "message": "Funding initiated",
        "transaction_id": 123,
        "form_payload": {
            "merchantId": "XYZ123",
            "transactionRef": "TXN_123ABC",
            "amount": 5000,
            "currency": "NGN",
            "redirectUrl": "https://yourapp.com/payment/callback",
            # ... other payload fields
        }
    },
    response_only=True,
    status_codes=['200']
)
