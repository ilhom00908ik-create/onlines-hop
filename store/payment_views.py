import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Order, PaymentTransaction

@csrf_exempt
def click_webhook_view(request):
    """ Click to'lov tizimi webhook simulyatsiyasi """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('click_paydoc_id') or data.get('merchant_trans_id')
            click_trans_id = str(data.get('click_trans_id', 'MOCK_CLICK_12345'))
            amount = data.get('amount')

            order = get_object_or_404(Order, id=order_id)

            # Transaction yaratish yoki yangilash (Field nomlari models.py ga moslandi)
            transaction, created = PaymentTransaction.objects.get_or_create(
                transaction_id=click_trans_id,
                defaults={
                    'order': order,
                    'provider': 'click',
                    'amount': amount or order.total_price,
                    'status': 'success'
                }
            )

            # Buyurtma statusini o'zgartirish
            order.status = 'paid'
            order.save()

            return JsonResponse({
                "click_trans_id": click_trans_id,
                "merchant_trans_id": order.id,
                "error": 0,
                "error_note": "Success"
            })
        except Exception as e:
            return JsonResponse({"error": -1, "error_note": str(e)}, status=400)

    return JsonResponse({"error": -2, "error_note": "Invalid method"}, status=405)


@csrf_exempt
def payme_webhook_view(request):
    """ Payme to'lov tizimi JSON-RPC webhook simulyatsiyasi """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            params = data.get('params', {})

            order_id = params.get('account', {}).get('order_id') or params.get('id')
            payme_trans_id = str(params.get('id', 'MOCK_PAYME_67890'))

            if order_id:
                order = get_object_or_404(Order, id=order_id)

                # Transaction yaratish yoki yangilash (Field nomlari models.py ga moslandi)
                PaymentTransaction.objects.get_or_create(
                    transaction_id=payme_trans_id,
                    defaults={
                        'order': order,
                        'provider': 'payme',
                        'amount': order.total_price,
                        'status': 'success'
                    }
                )

                order.status = 'paid'
                order.save()

            return JsonResponse({
                "result": {
                    "perform_time": 1000,
                    "transaction": payme_trans_id,
                    "state": 2
                },
                "error": None,
                "id": data.get('id')
            })
        except Exception as e:
            return JsonResponse({"error": {"code": -32400, "message": str(e)}}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)