from sqlalchemy.orm import Session, selectinload
from models.order import Order
from sqlalchemy import func, select
from services.supplier_service import SupplierService
from models.order_item import OrderItem
from services.product_service import ProductService
from decimal import Decimal
from services.inventory_services import InventoryService
from exceptions.business import NotFoundError, ValidationError, ConflictError

class OrderService():
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_order(self, supplier_id: int) -> Order:
        supplier = SupplierService(self.session).get_supplier(supplier_id)

        if not supplier: 
            raise NotFoundError("Supplier does not exist")

        order = Order()
        order.supplier = supplier

        self.session.add(order)
        self.session.flush()
        self.session.info.setdefault("log_events", []).append(f"Order created: order_id={order.id}, supplier_id={supplier.id}")
        return order

    def get_order(self, order_id: int) -> Order | None:
        stmt = select(Order).where(Order.id == order_id)

        return self.session.scalar(stmt)

    def get_all_orders(
            self,
            page: int = 1, 
            page_size: int = 10, 
            status: str | None = None,
            supplier_id: int | None = None
            ) -> tuple[list[Order], int]:

        offset = (page-1) * page_size
        stmt = select(Order).options(selectinload(Order.items))

        if status:
            stmt = stmt.where(
                Order.status == status
            )

        if supplier_id: 
            stmt = stmt.where(
                Order.supplier_id == supplier_id
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.scalar(count_stmt) or 0
        
        stmt = stmt.order_by(Order.id.desc()).limit(page_size).offset(offset)  

        orders = self.session.scalars(stmt).all()
        
        return orders, total

    def add_item(self, order_id: int, sku: str, quantity: int) -> OrderItem:
        order = self.get_order(order_id)
        
        if not order: 
            raise NotFoundError("Order does not exist")

        if order.status != "pending":
            raise ConflictError("Order status is not pending")

        product = ProductService(self.session).get_product(sku)

        if not product:
            raise NotFoundError("Product cannot be found")
        
        if not product in order.supplier.products:
            raise ConflictError("Product is not in list of orders")

        if quantity < 1:
            raise ValidationError("Quantity cannot be less than zero")

        for item in order.items:
            if item.product_id == product.id:
                raise ConflictError("Product already exist in that Order")

        order_item = OrderItem()

        order_item.order = order
        order_item.product = product
        order_item.quantity = quantity
        order_item.unit_price = product.price

        order.total_price += product.price * quantity

        self.session.add(order_item)
        return order_item

    def calculate_total(self, order_id: int) -> Decimal:
        order = self.get_order(order_id)

        if not order: 
            raise NotFoundError("Order does not exist")

        total = Decimal("0.00")

        for items in order.items:
            total += items.quantity * items.unit_price

        return total

    def complete_order(self, order_id : int) -> Order:
        order = self.get_order(order_id)

        if not order: 
            raise NotFoundError("Order does not exist")

        if not order.items: 
            raise ConflictError("There is no items in the given order")

        if order.status != "pending":
            raise ConflictError("Only pending orders can be completed")

        product_service = ProductService(self.session)    
        inventory_service = InventoryService(self.session, product_service)

        for item in order.items:    
            inventory_service.receive_stock(item.product.sku, item.quantity)

        order.status = "completed"

        self.session.info.setdefault("log_events", []).append(f"Order completed: order_id={order.id}, total_price={order.total_price}")

        return order

    def cancel_order(self, order_id : int) -> Order:
        order = self.get_order(order_id)

        if not order: 
            raise NotFoundError("Order does not exist")

        if order.status != "pending":
            raise ConflictError("Only pending orders can be cancelled")

        order.status = "cancelled"

        self.session.info.setdefault("log_events", []).append(f"Order cancelled: order_id={order.id}")

        return order
        

