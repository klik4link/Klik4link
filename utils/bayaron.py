import json
import logging
import uuid

import httpx

from config import (
    BAYARON_API_KEY,
    BAYARON_MERCHANT
)


logger = logging.getLogger(__name__)


BASE_URL = "https://api.bayaron.com"


class BayarOn:


    @staticmethod
    def headers():

        return {
            "Authorization": f"Bearer {BAYARON_API_KEY}",
            "X-Merchant-ID": BAYARON_MERCHANT,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }



    @staticmethod
    async def create_payment(
        amount: int,
        description: str,
        customer_name: str | None = None,
        customer_email: str | None = None,
        customer_phone: str | None = None,
    ):

        if not BAYARON_API_KEY:
            logger.error(
                "BAYARON_API_KEY kosong"
            )
            return None


        reference_id = (
            f"INV-{uuid.uuid4().hex[:12]}"
        )


        payload = {

            "reference_id": reference_id,

            "amount": amount,

            "description": description,

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

            logger.info(
                "BayarOn create payment | %s",
                reference_id
            )


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

                    headers=BayarOn.headers(),

                    json=payload
                )



            logger.info(
                "BayarOn status=%s",
                response.status_code
            )


            logger.info(
                "BayarOn response=%s",
                response.text
            )


            response.raise_for_status()


            return response.json()



        except Exception:

            logger.exception(
                "BayarOn create payment failed"
            )

            return None




    @staticmethod
    async def init_qris(
        reference_id: str
    ):


        payload = {

            "method": "qris",

            "channel": "qris"

        }



        try:


            logger.info(
                "BayarOn QRIS init | %s",
                reference_id
            )



            async with httpx.AsyncClient(
                timeout=30
            ) as client:


                response = await client.post(

                    f"{BASE_URL}/p/{reference_id}/init-method",

                    headers=BayarOn.headers(),

                    json=payload
                )



            logger.info(
                "QRIS status=%s",
                response.status_code
            )


            logger.info(
                "QRIS response=%s",
                response.text
            )


            response.raise_for_status()


            return response.json()



        except Exception:


            logger.exception(
                "BayarOn QRIS failed"
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

                    f"{BASE_URL}/p/{reference_id}/status",

                    headers=BayarOn.headers()

                )



            logger.info(
                "CHECK PAYMENT %s | %s",
                reference_id,
                response.status_code
            )


            logger.info(
                "CHECK RESPONSE %s",
                response.text
            )



            response.raise_for_status()


            return response.json()



        except Exception:


            logger.exception(
                "BayarOn check payment failed | %s",
                reference_id
            )


            return None
