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
        customer_name: str | None = None,
        customer_email: str | None = None,
        customer_phone: str | None = None,
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
                    "price": amount
                }
            ]
        }

        if customer_name:
            payload["buyer_name"] = customer_name

        if customer_email:
            payload["buyer_email"] = customer_email

        if customer_phone:
            payload["buyer_phone"] = customer_phone

        try:
            logger.info("BayarOn create payment")

            logger.debug(
                json.dumps(
                    payload,
                    indent=2,
                    ensure_ascii=False
                )
            )

            async with httpx.AsyncClient(
                timeout=30
            ) as client:

                response = await client.post(
                    f"{BASE_URL}/payments",
                    headers=headers,
                    json=payload
                )

            logger.info(
                "BayarOn status: %s",
                response.status_code
            )

            logger.debug(
                "BayarOn response: %s",
                response.text
            )

            response.raise_for_status()

            data = response.json()

            return data


        except Exception:

            logger.exception(
                "BayarOn create payment failed"
            )

            return None



    @staticmethod
    async def init_qris(
        reference_id: str
    ):

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        payload = {
            "method": "qris",
            "channel": "qris"
        }

        try:

            logger.info(
                "BayarOn init QRIS | %s",
                reference_id
            )

            async with httpx.AsyncClient(
                timeout=30
            ) as client:

                response = await client.post(
                    f"{BASE_URL}/p/{reference_id}/init-method",
                    headers=headers,
                    json=payload
                )


            logger.info(
                "BayarOn QRIS status: %s",
                response.status_code
            )


            logger.debug(
                "BayarOn QRIS response: %s",
                response.text
            )


            response.raise_for_status()

            return response.json()


        except Exception:

            logger.exception(
                "BayarOn init QRIS failed"
            )

            return None



    @staticmethod
    async def check_payment(
        reference_id: str
    ):

        try:

            async with httpx.AsyncClient(
                timeout=30
            ) as client:

                response = await client.get(
                    f"{BASE_URL}/p/{reference_id}/status"
                )


            response.raise_for_status()

            return response.json()


        except Exception:

            logger.exception(
                "BayarOn check payment failed | %s",
                reference_id
            )

            return None
