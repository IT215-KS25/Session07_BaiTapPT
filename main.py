from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any
from datetime import datetime

app = FastAPI()

class APIResponse(BaseModel):
    statusCode: int
    message: str
    data: Any | None = None
    error: str | None = None
    timestamp: str
    path: str


def build_envelope(status_code, message, request, data=None, error=None):
    return {
        "statusCode": status_code,
        "message": message,
        "data": data,
        "error": error,
        "timestamp": datetime.now().isoformat(),
        "path": request.url.path
    }


orders_db = [
    {"id": 1, "code": "SP001", "status": "PENDING"},
    {"id": 2, "code": "SP002", "status": "DELIVERED"}
]


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=build_envelope(
            status_code=422,
            message="Dữ liệu đầu vào không hợp lệ",
            request=request,
            error="Vui lòng kiểm tra lại dữ liệu gửi lên"
        )
    )


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=build_envelope(
            status_code=exc.status_code,
            message=exc.detail,
            request=request,
            error=exc.detail
        )
    )


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=build_envelope(
            status_code=500,
            message="Đã có lỗi hệ thống xảy ra, vui lòng thử lại sau",
            request=request,
            error="Internal Server Error"
        )
    )


def find_order(order_id):
    for order in orders_db:
        if order["id"] == order_id:
            return order
    return None


@app.delete("/orders/{order_id}", tags=["Orders"], status_code=200, response_model=APIResponse)
def cancel_order(order_id: int, request: Request):
    order = find_order(order_id)

    if order is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng có id={order_id}")

    if order["status"] == "DELIVERED":
        raise HTTPException(status_code=400, detail=f"Đơn hàng {order['code']} đã giao thành công, không thể hủy")

    order["status"] = "CANCELLED"

    return build_envelope(
        status_code=200,
        message=f"Hủy đơn hàng {order['code']} thành công",
        request=request,
        data=order
    )