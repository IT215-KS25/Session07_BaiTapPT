from fastapi import FastAPI, status, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime

app = FastAPI()

class APIResponse(BaseModel):
    status_code: int
    status: str
    message: str
    data: Any | None = None
    error: str | None = None
    timestamp: datetime
    path: str

class PaymentInfo(BaseModel):
    id: int
    code: str
    payment_status: str
    method: str

class PaymentResponse(APIResponse):
    data: PaymentInfo | None = None

orders_list = [
    {"id": 1, "code": "SP001", "payment_status": "PAID", "method": "BANK_TRANSFER"},
    {"id": 2, "code": "SP002", "payment_status": "UNPAID", "method": "NONE"}
]

orders_dict = {order["id"]: order for order in orders_list}

def create_response(status_code, status, message, data=None, error=None, path=""):
    return {
        "status_code": status_code,
        "status": status,
        "message": message,
        "data": data,
        "error": error,
        "timestamp": datetime.now().isoformat(),
        "path": path
    }

@app.get("/orders/{order_id}/payment", tags=["Payment"], status_code=status.HTTP_200_OK, response_model=PaymentResponse)
def get_payment_history(order_id: int, request: Request):
    order = orders_dict.get(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy đơn hàng có id={order_id}"
        )

    try:
        payment_data = {
            "id": order["id"],
            "code": order["code"],
            "payment_status": order["payment_status"],
            "method": order["method"]
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã có lỗi xảy ra trong quá trình xử lý dữ liệu thanh toán"
        )

    return create_response(
        status_code=status.HTTP_200_OK,
        status="success",
        message="Lấy lịch sử thanh toán thành công",
        data=payment_data,
        path=request.url.path
    )