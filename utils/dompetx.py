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
    # =========================================================
    # CONFIG
    # =========================================================
    @staticmethod
    def _check_api_key():
        if not DOMPETX_API_KEY:
            raise ValueError(
                "DOMPETX_API_KEY belum diisi"
            )
    # =========================================================
    # SIGNATURE
    # =========================================================
    @staticmethod
    def _signature(
        timestamp: str,
        body: str
    ) -> str:
        signature_data = (
            f"{timestamp}.{body}"
        )
        return hmac.new(
            DOMPETX_API_KEY.encode(),
            signature_data.encode(),
            hashlib.sha256
        ).hexdigest()
    # =========================================================
    # HEADERS
    # =========================================================
    @staticmethod
    def headers(
        timestamp: str,
        body: str,
        idempotency_key: str | None = None
    ):
        DompetX._check_api_key()
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
                timestamp
        }
        if idempotency_key:
            headers["Idempotency-Key"] = (
                idempotency_key
            )
        return headers
    # =========================================================
    # CREATE PAYMENT
    # POST /v1/payments
    # =========================================================
    @staticmethod
    async def create_payment(
        amount: int,
        description: str,
        customer_name: str | None = None,
        customer_email: str | None = None,
        customer_phone: str | None = None,
        reference: str | None = None
    ):
        DompetX._check_api_key()
        reference = reference or (
            f"INV-{uuid.uuid4().hex[:12].upper()}"
        )
        payload = {
            "method": "QRIS",
            "amount": int(amount),
            "currency": "IDR",
            "reference": reference,
            "settlementSpeed": "standard",
            "metadata": {
                "order_name": description,
                "product_name": description
            }
        }
        if customer_name:
            payload["metadata"][
                "customer_name"
            ] = customer_name
        if customer_email:
            payload["metadata"][
                "customer_email"
            ] = customer_email
        if customer_phone:
            payload["metadata"][
                "customer_phone"
            ] = customer_phone
        body = json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False
        )
        timestamp = str(
            int(time.time())
        )
        idempotency_key = (
            f"req_{uuid.uuid4().hex}"
        )
        headers = DompetX.headers(
            timestamp=timestamp,
            body=body,
            idempotency_key=idempotency_key
        )
        try:
            logger.info(
                "DompetX CREATE PAYMENT | "
                "reference=%s | amount=%s",
                reference,
                amount
            )
            logger.debug(
                "DompetX REQUEST BODY=%s",
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
                "DompetX RESPONSE | "
                "status=%s | body=%s",
                response.status_code,
                response.text
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "DompetX HTTP ERROR | "
                "status=%s | body=%s",
                exc.response.status_code,
                exc.response.text
            )
            return None
        except Exception:
            logger.exception(
                "DompetX create payment failed"
            )
            return None
    # =========================================================
    # GET PAYMENT DETAIL
    # GET /v1/payments/detail/{paymentId}
    # =========================================================
    @staticmethod
    async def get_payment(
        payment_id: str
    ):
        DompetX._check_api_key()
        body = "{}"
        timestamp = str(
            int(time.time())
        )
        headers = DompetX.headers(
            timestamp=timestamp,
            body=body
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
                "DompetX DETAIL RESPONSE | "
                "status=%s | body=%s",
                response.status_code,
                response.text
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "DompetX detail HTTP ERROR | "
                "status=%s | body=%s",
                exc.response.status_code,
                exc.response.text
            )
            return None
        except Exception:
            logger.exception(
                "DompetX get payment failed | id=%s",
                payment_id
            )
            return None
    # =========================================================
    # CHECK PAYMENT BY ID
    # GET /v1/payments/check-status/{paymentId}
    # =========================================================
    @staticmethod
    async def check_payment(
        payment_id: str
    ):
        DompetX._check_api_key()
        body = "{}"
        timestamp = str(
            int(time.time())
        )
        headers = DompetX.headers(
            timestamp=timestamp,
            body=body
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
                "DompetX CHECK RESPONSE | "
                "status=%s | body=%s",
                response.status_code,
                response.text
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "DompetX check HTTP ERROR | "
                "status=%s | body=%s",
                exc.response.status_code,
                exc.response.text
            )
            return None
        except Exception:
            logger.exception(
                "DompetX check payment failed | id=%s",
                payment_id
            )
            return None
    # =========================================================
    # CHECK PAYMENT BY REFERENCE
    # GET /v1/payments/check-status?reference={reference}
    # =========================================================
    @staticmethod
    async def check_by_reference(
        reference: str
    ):
        DompetX._check_api_key()
        body = "{}"
        timestamp = str(
            int(time.time())
        )
        headers = DompetX.headers(
            timestamp=timestamp,
            body=body
        )
        try:
            logger.info(
                "DompetX CHECK REFERENCE | reference=%s",
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
                "DompetX REFERENCE RESPONSE | "
                "status=%s | body=%s",
                response.status_code,
                response.text
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "DompetX reference HTTP ERROR | "
                "status=%s | body=%s",
                exc.response.status_code,
                exc.response.text
            )
            return None
        except Exception:
            logger.exception(
                "DompetX check reference failed | reference=%s",
                reference
            )
            return None
    # =========================================================
    # CANCEL PAYMENT
    # POST /v1/payments/cancel/{paymentId}
    # =========================================================
    @staticmethod
    async def cancel_payment(
        payment_id: str
    ):
        DompetX._check_api_key()
        body = "{}"
        timestamp = str(
            int(time.time())
        )
        idempotency_key = (
            f"cancel_{uuid.uuid4().hex}"
        )
        headers = DompetX.headers(
            timestamp=timestamp,
            body=body,
            idempotency_key=idempotency_key
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
                    content=body,
                    headers=headers
                )
            logger.info(
                "DompetX CANCEL RESPONSE | "
                "status=%s | body=%s",
                response.status_code,
                response.text
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "DompetX cancel HTTP ERROR | "
                "status=%s | body=%s",
                exc.response.status_code,
                exc.response.text
            )
            return None
        except Exception:
            logger.exception(
                "DompetX cancel payment failed | id=%s",
                payment_id
            )
            return None
    # =========================================================
    # GET QRIS IMAGE
    # GET /v1/qr/{paymentId}
    # =========================================================
    @staticmethod
    async def get_qr(
        payment_id: str
    ):
        DompetX._check_api_key()
        try:
            logger.info(
                "DompetX GET QR | id=%s",
                payment_id
            )
            async with httpx.AsyncClient(
                timeout=30
            ) as client:
                response = await client.get(
                    f"{BASE_URL}/v1/qr/{payment_id}"
                )
            logger.info(
                "DompetX QR RESPONSE | "
                "status=%s | content_type=%s",
                response.status_code,
                response.headers.get(
                    "content-type"
                )
            )
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as exc:
            logger.error(
                "DompetX QR HTTP ERROR | "
                "status=%s | body=%s",
                exc.response.status_code,
                exc.response.text
            )
            return None
        except Exception:
            logger.exception(
                "DompetX get QR failed | id=%s",
                payment_id
            )
            return None
