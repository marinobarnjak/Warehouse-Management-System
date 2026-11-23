from sqlalchemy import func, select, desc
from sqlalchemy.orm import Session
from models.product import Product
from services.product_service import ProductService
from models.stock_movement import StockMovement
from exceptions.business import NotFoundError, ValidationError, ConflictError

import logging

logger = logging.getLogger("wms.inventory")

class InventoryService():

    def __init__(self, session: Session, product: ProductService) -> None:
        self.session = session
        self.product_service = product

    def receive_stock(self, sku: str, quantity: int) -> StockMovement:
    
        if quantity < 1:
            raise ValidationError("Quantity must be greater than zero")

        stmt = select(Product).where(Product.sku == sku).with_for_update().execution_options(populate_existing=True)
        product = self.session.scalar(stmt)

        if not product:
            raise NotFoundError("Product with given SKU does not exist")
        
        product.quantity += quantity

        stock_movement = StockMovement()
        stock_movement.movement_type = "IN" 
        stock_movement.quantity = quantity
        stock_movement.product = product

        self.session.info.setdefault("log_events", []).append(
            f"Stock received: SKU={sku}, quantity={quantity}, new_stock={stock_movement.quantity}"
            )

        self.session.add(stock_movement)

        return stock_movement

    def issue_stock(self, sku: str, quantity: int) -> StockMovement:

        if quantity < 1:
            raise ValidationError("Quantity must be greater than zero")
        
        stmt = select(Product).where(Product.sku == sku).with_for_update().execution_options(populate_existing=True)
        product = self.session.scalar(stmt)

        if not product:
            raise NotFoundError("Product with given SKU does not exist")

        if quantity > product.quantity:
            logger.warning("Insufficient stock: SKU=%s requested=%s available=%s",
                           sku,
                           quantity,
                           product.quantity
                    )
            raise ConflictError("Insufficient stock")

        product.quantity -= quantity

        stock_movement = StockMovement()
        stock_movement.movement_type = "OUT" 
        stock_movement.quantity = quantity
        stock_movement.product = product

        self.session.info.setdefault("log_events", []).append(
            f"Stock issued: SKU={sku}, quantity={quantity}, new_stock={stock_movement.quantity}"
            )

        self.session.add(stock_movement)
        
        return stock_movement

    def get_stock(self, sku: str) -> int:
        product = self.product_service.get_product(sku)
        
        if not product:
            raise NotFoundError("Product with given SKU does not exist")

        return product.quantity

    def is_low_stock(self, sku: str) -> bool:
        product = self.product_service.get_product(sku)

        if not product:
            raise NotFoundError("Product with given SKU does not exist")

        return product.quantity < product.min_stock

    def get_low_stock_products(self) -> list[Product]:
        stmt = select(Product).where(Product.quantity < Product.min_stock)

        return self.session.scalars(stmt).all()

    def get_all_movements(
            self,
            page: int = 1, 
            page_size: int = 10, 
            sku: str | None = None,
            movement_type: str | None = None
            ) -> tuple[list[StockMovement], int]:

        offset = (page-1) * page_size
        stmt = select(StockMovement)

        if sku: 
            stmt = stmt.join(Product, StockMovement.product_id == Product.id).where(
                Product.sku == sku
            )

        if movement_type:
            stmt = stmt.where(
                StockMovement.movement_type == movement_type
            )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.scalar(count_stmt) or 0
        
        stmt = stmt.order_by(
            StockMovement.created_at.desc(),
            StockMovement.id.desc()).limit(page_size).offset(offset)  

        movements = self.session.scalars(stmt).all()
        
        return movements, total