import json
import logging
import time
import uuid
import hmac
import hashlib
import httpx
from config import DOMPETX_API_KEY
logger = logging.getLogger(__name__)
BASE_URL = "https://api.dompetx.com"
class DompetX:
    # =================================================
    # SIGNATURE
    # =================================================
    @staticmethod
    def _signature(
        timestamp: str,
        body: str
    ) -> str:
        if not DOMPETX_API_KEY:
            raise ValueError(
                "DOMPETX_API_KEY belum diisi"
            )
        signature_data = (
            f"{timestamp}.{body}"
        )
        return hmac.new(
            DOMPETX_API_KEY.encode(),
            signature_data.encode(),
            hashlib.sha256
        ).hexdigest()
    # =================================================
    # HEADERS
    # =================================================
    @staticmethod
    def headers(
        timestamp: str,
        body: str,
        idempotency_key: str | None = None
    ):
        if not DOMPETX_API_KEY:
            raise ValueError(
                "DOMPETX_API_KEY belum diisi"
            )
        signature = DompetX._signature(
            timestamp=timestamp,
            body=body
        )
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-DOMPAY-API-Key":
                DOMPETX_API_KEY,
            "X-DOMPAY-Signature":
                signature,
            "X-DOMPAY-Timestamp":
                timestamp,
        }
        if idempotency_key:
            headers["Idempotency-Key"] = (
                idempotency_key
            )
        return headers
    # =================================================
    # BUILD REQUEST
    # =================================================
    @staticmethod
    def _prepare_request(
        payload: dict | None = None,
        idempotency_key: str | None = None
    ):
        if payload is None:
            body = ""
        else:
            body = json.dumps(
                payload,
                separators=(",", ":"),
                ensure_ascii=False
            )
        timestamp = str(
            int(time.time())
        )
        headers = DompetX.headers(
            timestamp=timestamp,
            body=body,
            idempotency_key=idempotency_key
        )
        return body, headers
    # =================================================
    # CREATE PAYMENT
    # POST /v1/payments
    # =================================================
    @staticmethod
    async def create_payment(
        amount: int,
        description: str,
        customer_name: str | None = None,
        customer_email: str | None = None,
        customer_phone: str | None = None,
        reference: str | None = None,
        redirect_url: str | None = None,
        notes: str | None = None,
    ):
        if not DOMPETX_API_KEY:
            raise ValueError(
                "DOMPETX_API_KEY belum diisi"
            )
        reference = reference or (
            f"INV-{uuid.uuid4().hex[:12]}"
        )
        metadata = {
            "order_name": description,
            "product_name": description,
        }
        if customer_name:
            metadata["customer_name"] = (
                customer_name
            )
        if customer_email:
            metadata["customer_email"] = (
                customer_email
            )
        if customer_phone:
            metadata["customer_phone"] = (
                customer_phone
            )
        if notes:
            metadata["notes"] = notes
        payload = {
            "method": "QRIS",
            "amount": int(amount),
            "currency": "IDR",
            "reference": reference,
            "metadata": metadata,
        }
        if redirect_url:
            payload["redirectUrl"] = (
                redirect_url
            )
        body, headers = (
            DompetX._prepare_request(
                payload=payload,
                idempotency_key=(
                    f"req_{uuid.uuid4().hex}"
                )
            )
        )
        try:
            logger.info(
                "DompetX CREATE PAYMENT | "
                "reference=%s | amount=%s",
                reference,
                amount
            )
            logger.info(
                "DompetX payload=%s",
                body
            )
            async with httpx.AsyncClient(
                timeout=30
            ) as client:
                response = await client.post(
                    f"{BASE_URL}/v1/payments",
                    content=body,
                    headers=headers
                )
            logger.info(
                "DompetX create status=%s",
                response.status_code
            )
            logger.info(
                "DompetX create response=%s",
                response.text
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            logger.exception(
                "DompetX create payment failed | "
                "reference=%s",
                reference
            )
            return None
    # =================================================
    # CREATE CHECKOUT
    # POST /v1/payments/checkout
    #
    # RESPONSE:
    # {
    #   "id": "...",
    #   "status": "pending",
    #   "payment_link": "https://..."
    # }
    # =================================================
    @staticmethod
    async def create_checkout(
        amount: int,
        description: str,
        customer_name: str | None = None,
        customer_email: str | None = None,
        customer_phone: str | None = None,
        reference: str | None = None,
        redirect_url: str | None = None,
        notes: str | None = None,
        items: list | None = None,
    ):
        if not DOMPETX_API_KEY:
            raise ValueError(
                "DOMPETX_API_KEY belum diisi"
            )
        reference = reference or (
            f"INV-{uuid.uuid4().hex[:12]}"
        )
        metadata = {
            "order_name": description,
            "product_name": description,
        }
        if customer_name:
            metadata["customer_name"] = (
                customer_name
            )
        if customer_email:
            metadata["customer_email"] = (
                customer_email
            )
        if customer_phone:
            metadata["customer_phone"] = (
                customer_phone
            )
        if notes:
            metadata["notes"] = notes
        if items:
            metadata["items"] = items
        payload = {
            "amount": int(amount),
            "currency": "IDR",
            "reference": reference,
            "metadata": metadata,
        }
        if redirect_url:
            payload["redirectUrl"] = (
                redirect_url
            )
        body, headers = (
            DompetX._prepare_request(
                payload=payload,
                idempotency_key=(
                    f"checkout_{uuid.uuid4().hex}"
                )
            )
        )
        try:
            logger.info(
                "DompetX CREATE CHECKOUT | "
                "reference=%s | amount=%s",
                reference,
                amount
            )
            logger.info(
                "DompetX checkout payload=%s",
                body
            )
            async with httpx.AsyncClient(
                timeout=30
            ) as client:
                response = await client.post(
                    f"{BASE_URL}/v1/payments/checkout",
                    content=body,
                    headers=headers
                )
            logger.info(
                "DompetX checkout status=%s",
                response.status_code
            )
            logger.info(
                "DompetX checkout response=%s",
                response.text
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            logger.exception(
                "DompetX create checkout failed | "
                "reference=%s",
                reference
            )
            return None
    # =================================================
    # GET PAYMENT DETAIL
    # =================================================
    @staticmethod
    async def get_payment(
        payment_id: str
    ):
        if not DOMPETX_API_KEY:
            raise ValueError(
                "DOMPETX_API_KEY belum diisi"
            )
        body, headers = (
            DompetX._prepare_request()
        )
        try:
            logger.info(
                "DompetX GET PAYMENT | id=%s",
                payment_id
            )
            async with httpx.AsyncClient(
                timeout=30
            ) as client:
                response = await client.get(
                    f"{BASE_URL}/v1/payments/detail/{payment_id}",
                    headers=headers
                )
            logger.info(
                "DompetX detail status=%s",
                response.status_code
            )
            logger.info(
                "DompetX detail response=%s",
                response.text
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            logger.exception(
                "DompetX get payment failed | id=%s",
                payment_id
            )
            return None
    # =================================================
    # CHECK PAYMENT BY ID
    # =================================================
    @staticmethod
    async def check_payment(
        payment_id: str
    ):
        if not DOMPETX_API_KEY:
            raise ValueError(
                "DOMPETX_API_KEY belum diisi"
            )
        body, headers = (
            DompetX._prepare_request()
        )
        try:
            logger.info(
                "DompetX CHECK PAYMENT | id=%s",
                payment_id
            )
            async with httpx.AsyncClient(
                timeout=30
            ) as client:
                response = await client.get(
                    f"{BASE_URL}/v1/payments/check-status/{payment_id}",
                    headers=headers
                )
            logger.info(
                "DompetX check status=%s",
                response.status_code
            )
            logger.info(
                "DompetX check response=%s",
                response.text
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            logger.exception(
                "DompetX check payment failed | id=%s",
                payment_id
            )
            return None
    # =================================================
    # CHECK PAYMENT BY REFERENCE
    # =================================================
    @staticmethod
    async def check_by_reference(
        reference: str
    ):
        if not DOMPETX_API_KEY:
            raise ValueError(
                "DOMPETX_API_KEY belum diisi"
            )
        body, headers = (
            DompetX._prepare_request()
        )
        try:
            logger.info(
                "DompetX CHECK REFERENCE | "
                "reference=%s",
                reference
            )
            async with httpx.AsyncClient(
                timeout=30
            ) as client:
                response = await client.get(
                    f"{BASE_URL}/v1/payments/check-status",
                    params={
                        "reference": reference
                    },
                    headers=headers
                )
            logger.info(
                "DompetX reference status=%s",
                response.status_code
            )
            logger.info(
                "DompetX reference response=%s",
                response.text
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            logger.exception(
                "DompetX check reference failed | "
                "reference=%s",
                reference
            )
            return None
    # =================================================
    # CANCEL PAYMENT
    # =================================================
    @staticmethod
    async def cancel_payment(
        payment_id: str
    ):
        if not DOMPETX_API_KEY:
            raise ValueError(
                "DOMPETX_API_KEY belum diisi"
            )
        body, headers = (
            DompetX._prepare_request()
        )
        try:
            logger.info(
                "DompetX CANCEL PAYMENT | id=%s",
                payment_id
            )
            async with httpx.AsyncClient(
                timeout=30
            ) as client:
                response = await client.post(
                    f"{BASE_URL}/v1/payments/cancel/{payment_id}",
                    headers=headers
                )
            logger.info(
                "DompetX cancel status=%s",
                response.status_code
            )
            logger.info(
                "DompetX cancel response=%s",
                response.text
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            logger.exception(
                "DompetX cancel payment failed | id=%s",
                payment_id
            )
            return None
