import json
import logging

import httpx

from config import BAYARON_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://api.bayaron.com"


class BayarOn:

    @staticmethod
    async def create_payment(
        amount: int,
        description: str,
        payment_url: str = "",
        callback_url: str | None = None,
        redirect_url: str | None = None,
        customer_name: str | None = None,
        customer_phone: str | None = None,
        payment_method: str = "qris",
    ):

        headers = {
            "Authorization": f"Bearer {BAYARON_API_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        payload = {
            "items": [
                {
                    "name": description,
                    "qty": 1,
                    "price": amount,
                }
            ],
            "buyer_name": customer_name or "Telegram User",
            "buyer_email": "user@example.com",
            "buyer_phone": customer_phone or "",
        }

        if redirect_url:
            payload["return_url"] = redirect_url

        try:
            logger.info("BayarOn create payment request")
            logger.debug(
                json.dumps(
                    payload,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            async with httpx.AsyncClient(
                timeout=30,
                follow_redirects=True,
            ) as client:
                response = await client.post(
                    f"{BASE_URL}/payments",
                    headers=headers,
                    json=payload,
                )

            logger.info(
                "Create payment status: %s",
                response.status_code,
            )

            logger.debug(
                "Create payment body: %s",
                response.text,
            )

            response.raise_for_status()

            return response.json()

        except Exception:
            logger.exception("Create payment failed")
            return None

    @staticmethod
    async def check_payment(reference_id: str):

        headers = {
            "Authorization": f"Bearer {BAYARON_API_KEY}",
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(
                timeout=30,
                follow_redirects=True,
            ) as client:
                response = await client.get(
                    f"{BASE_URL}/payments/{reference_id}",
                    headers=headers,
                )

            logger.info(
                "Check payment status: %s",
                response.status_code,
            )

            logger.debug(
                "Check payment body: %s",
                response.text,
            )

            response.raise_for_status()

            return response.json()

        except Exception:
            logger.exception(
                "Check payment failed | reference=%s",
                reference_id,
            )
            return None
