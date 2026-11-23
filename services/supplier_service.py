from sqlalchemy.orm import Session
from models.supplier import Supplier
from sqlalchemy import select, or_, func
from services.product_service import ProductService
from exceptions.business import NotFoundError, ValidationError, ConflictError

class SupplierService():
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_supplier(self, id: int) -> Supplier:
        stmt = select(Supplier).where(Supplier.id == id)

        return self.session.scalar(stmt)

    def get_all_suppliers(
            self,
            page: int = 1, 
            page_size: int = 10, 
            search: str | None = None,
            ) -> tuple[list[Supplier], int]:
         
        offset = (page-1) * page_size
        stmt = select(Supplier)

        if search:
            stmt = stmt.where(
                Supplier.name.ilike(f"%{search}%"),
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.scalar(count_stmt) or 0 

        stmt = stmt.order_by(Supplier.id).limit(page_size).offset(offset)

        suppliers = self.session.scalars(stmt).all()

        return suppliers, total

    def create_supplier(self, name: str, email: str | None = None, phone: str | None = None) -> Supplier | None:
        name = name.strip()

        if not name:
            raise NotFoundError("Name cannot be empty")

        supplier = Supplier()
        supplier.name = name

        if email:
            supplier.email = email.strip()  

        if phone: 
            supplier.phone = phone.strip()

        self.session.add(supplier)
        return supplier

    def add_product_to_supplier(self, supplier_id : int, sku: str) -> Supplier:

        supplier = self.get_supplier(supplier_id)
        product = ProductService(self.session)
        product = product.get_product(sku)

        if not supplier:
            raise NotFoundError("Supplier does not exist")
        if not product:
            raise NotFoundError("Product does not exist")

        if product not in supplier.products:
            supplier.products.append(product)

        return supplier
        