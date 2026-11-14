from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependecies import get_db, get_transactional_db
from services.product_service import ProductService
from schemas.product import ProductResponse, ProductCreate, ProductUpdate
from exceptions.business import NotFoundError

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=list[ProductResponse])
def products(session: Session = Depends(get_db)):
    return ProductService(session).get_all_products()

@router.post("/", status_code = 201, response_model=ProductResponse)
def create_product(product: ProductCreate, session: Session = Depends(get_transactional_db, scope="function")):
    product_service = ProductService(session)
    
    created_product = product_service.create_product(
        name=product.name,
        sku=product.sku,
        price=product.price, 
        min_stock=product.min_stock
        )
    
    session.flush()
    session.refresh(created_product)

    return ProductResponse.model_validate(created_product)

@router.get("/{sku}", response_model=ProductResponse)
def get_product(sku: str, session: Session = Depends(get_db)):
    product = ProductService(session)

    obtained_product = product.get_product(sku)
    
    if obtained_product == None: 
        raise NotFoundError("Product with given SKU does not exist")

    return obtained_product

@router.patch("/{sku}", response_model=ProductResponse)
def update_product(sku: str, product: ProductUpdate, session: Session = Depends(get_transactional_db, scope="function")):
    update = ProductService(session)

    updated_product = update.update_product(sku, product.name)

    session.flush()
    session.refresh(updated_product)

    return ProductResponse.model_validate(updated_product)


@router.delete("/{sku}", status_code=204)
def delete_product(sku: str, session: Session = Depends(get_transactional_db, scope="function")):
    product = ProductService(session)
    
    product.delete_product(sku)
    session.flush()
    
    