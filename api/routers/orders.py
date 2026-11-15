from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_transactional_db
from services.order_service import OrderService
from schemas.order import OrderCreate, OrderItemCreate, OrderResponse, OrderItemResponse
from exceptions.business import NotFoundError

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", status_code=201, response_model=OrderResponse)
def create_order(order_create: OrderCreate, session: Session = Depends(get_transactional_db, scope="function")):
    order_service = OrderService(session)

    
    order = order_service.create_order(order_create.supplier_id)
    session.flush()
    session.refresh(order)

    return OrderResponse.model_validate(order)

@router.get("/", response_model=list[OrderResponse])
def get_all_orders(session: Session = Depends(get_db)):
    
    return OrderService(session).get_all_orders()

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, session: Session = Depends(get_db)):
    order_service = OrderService(session)
    order = order_service.get_order(order_id)

    if order is None:
        raise NotFoundError("Order with given ID does not exist")
    
    return order

@router.post("/{order_id}/items", status_code=201, response_model=OrderItemResponse)
def create_order_item(
    order_id: int,
    order_item: OrderItemCreate,
    session: Session = (Depends(get_transactional_db, scope="function"))
    ):

    order_service = OrderService(session)

    
    added_item = order_service.add_item(order_id, order_item.sku, order_item.quantity)
    session.flush()
    session.refresh(added_item)

    return OrderItemResponse.model_validate(added_item)

@router.post("/{order_id}/complete-order", status_code=200, response_model=OrderResponse)
def complete_order(order_id: int, session: Session = Depends(get_transactional_db, scope="function")):

    completed_order = OrderService(session).complete_order(order_id)
    session.flush()
    session.refresh(completed_order)

    return OrderResponse.model_validate(completed_order)

@router.post("/{order_id}/cancel-order", status_code=200, response_model=OrderResponse)
def cancel_order(order_id: int, session: Session = Depends(get_transactional_db, scope="function")):

    
    canceled_order = OrderService(session).cancel_order(order_id)
    session.flush()
    session.refresh(canceled_order)

    return OrderResponse.model_validate(canceled_order)