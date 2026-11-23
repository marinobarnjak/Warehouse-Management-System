from sqlalchemy.orm import Session
from models.product import Product
from sqlalchemy import select, or_, func
from decimal import Decimal

from exceptions.business import NotFoundError, ValidationError, ConflictError

class ProductService():

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_product(self, sku: str) -> Product | None: 
        stmt = select(Product).where(Product.sku == sku)

        return self.session.scalar(stmt)

    def create_product(self, name: str, sku: str, price: Decimal, min_stock: int = 0) -> Product:

            name = name.strip()
            sku = sku.strip()
            if not name:
                raise ValidationError("Name cannot be empty")
            if not sku: 
                raise ValidationError("SKU cannot be empty")
            if price <= 0: 
                raise ValidationError("Price must be greater than zero")
            if min_stock < 0:
                raise ValidationError("Minimal stock cannot be a negative number")

            product = Product()
            product.name = name
            product.sku = sku
            product.price = price
            product.quantity = 0
            product.min_stock = min_stock
            
            self.session.add(product)
            self.session.info.setdefault("log_events",[]).append(f"Product created SKU={sku}")
            return product

    def get_all_products(
            self,
            page: int = 1, 
            page_size: int = 10, 
            search: str | None = None, 
            low_stock: bool = False
            ) -> tuple[list[Product], int]:
        
        offset = (page-1) * page_size
        stmt = select(Product)

        if search: 
            stmt = stmt.where(
                or_(
                    Product.name.ilike(f"%{search}%"), 
                    Product.sku.ilike(f"%{search}%")
                    )
                )

        if low_stock:
            stmt = stmt.where(Product.quantity <= Product.min_stock)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.scalar(count_stmt) or 0

        stmt = stmt.order_by(Product.id).limit(page_size).offset(offset)

        products = self.session.scalars(stmt).all()

        return products, total
        
    def update_product(self, sku: str, new_name: str) -> Product | None:
        product = self.get_product(sku)

        if not product:
            raise NotFoundError("Product cannot be found")

        if product:
            product.name = new_name
            return product
        
        else:
            return None

    def delete_product(self, sku: str) -> bool:
        product = self.get_product(sku)

        if not product:
            raise NotFoundError("Product cannot be found")

        if not product:
            return False

        self.session.delete(product)
        return True

