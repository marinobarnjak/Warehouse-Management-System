from fastapi import FastAPI

from api.routers.products import router as product_router
from api.routers.inventory import router as inventory_router
from api.routers.suppliers import router as supplier_router
from api.routers.orders import router as order_router

from exceptions.business import ValidationError, NotFoundError, ConflictError
from api.exception_handlers import conflict_handler, not_found_handler, validation_handler, integrity_error_handler
from sqlalchemy.exc import IntegrityError

app = FastAPI()
app.title="Warehouse Managment System"

app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(ValidationError, validation_handler)
app.add_exception_handler(ConflictError, conflict_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)

@app.get('/')
def root():
    return {"message": "WMS API is running"}

app.include_router(product_router)
app.include_router(inventory_router)
app.include_router(supplier_router)
app.include_router(order_router)