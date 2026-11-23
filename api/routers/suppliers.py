from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import math

from api.dependencies import get_db, get_transactional_db
from schemas.product import ProductResponse
from services.supplier_service import SupplierService
from schemas.supplier import SupplierCreate, SupplierResponse, SupplierAddProduct
from exceptions.business import NotFoundError
from schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.post("/", status_code=201, response_model=SupplierResponse)
def create_supplier(supplier_create: SupplierCreate, session: Session = Depends(get_transactional_db, scope="function")):
    supplier = SupplierService(session)

    created_supplier = supplier.create_supplier(
    name=supplier_create.name, 
    email=supplier_create.email, 
    phone=supplier_create.phone
    )

    session.flush()
    session.refresh(created_supplier)

    return SupplierResponse.model_validate(created_supplier)

@router.get("/", response_model=PaginatedResponse[SupplierResponse])
def get_all_suppliers(
    page: int = Query(1, gt=0), 
    page_size: int = Query(10, ge=1, le=100), 
    search: str = Query(default=None, max_length=100),
    session: Session = Depends(get_db)
    ):

    suppliers, total = SupplierService(session).get_all_suppliers(page, page_size, search)
    return PaginatedResponse[SupplierResponse](
        items=suppliers,
        total=total, 
        page=page, 
        page_size=page_size, 
        total_pages=math.ceil(total / page_size)
    )

@router.get("/{id}", response_model=SupplierResponse)
def get_supplier(id: int, session: Session = Depends(get_db)):
    supplier_service = SupplierService(session)

    supplier = supplier_service.get_supplier(id)

    if supplier is None:
        raise NotFoundError("Supplier with given ID does not exists")

    return supplier

@router.post("/{supplier_id}/products")
def add_product_to_supplier(
    supplier_id: int, 
    supplier_add_product: SupplierAddProduct, 
    session: Session = Depends(get_transactional_db, scope="function")
    ):
    supplier_service = SupplierService(session)
    
    supplier_service.add_product_to_supplier(supplier_id, sku=supplier_add_product.sku)

    return {
        "message": "Successfully",
        "supplier_id": supplier_id,
        "sku": supplier_add_product.sku
    }

@router.get("/{supplier_id}/products", response_model=list[ProductResponse])
def get_supplier_products(supplier_id: int, session: Session = Depends(get_db)):
    supplier = SupplierService(session).get_supplier(supplier_id)

    if supplier is None: 
        raise NotFoundError("Supplier cannot be found")

    return supplier.products