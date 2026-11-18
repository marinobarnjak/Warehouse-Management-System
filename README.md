# Warehouse Management System (WMS)

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)
![pytest](https://img.shields.io/badge/pytest-testing-blue)
![Status](https://img.shields.io/badge/Status-In%20Development-orange)

## Overview

Warehouse Management System (WMS) is a REST API for managing warehouse operations, built with Python, FastAPI and PostgreSQL.

The application manages products, suppliers, inventory movements and purchase orders. The project focuses on backend development, relational database design, business logic, transaction management and automated testing.

The core backend is implemented. Application logging and a web user interface are planned next.

## Features

### Product Management

- Create, retrieve, rename and delete products using unique SKUs.
- Manage product prices, quantities and minimum stock levels.
- Validate product creation data.

### Inventory Management

- Receive and issue stock.
- Check stock levels and list low-stock products.
- Record incoming (`IN`) and outgoing (`OUT`) stock movements with timestamps.
- Prevent issuing more stock than is available.
- Use row-level locking (`SELECT FOR UPDATE`) during stock changes.

### Supplier Management

- Create and retrieve suppliers and their contact information.
- Associate products with suppliers using a many-to-many relationship.
- Retrieve products associated with a supplier.

### Order Management

- Create purchase orders for suppliers.
- Add multiple products with quantities and stored unit prices.
- Calculate order totals using `Decimal`.
- Validate supplier-product relationships and prevent duplicate order items.
- Complete pending orders and automatically receive ordered stock in a single transaction.
- Cancel pending orders and prevent invalid status transitions.

Order statuses: `pending`, `completed`, `cancelled`.

## Tech Stack

| Technology | Purpose |
| --- | --- |
| Python | Backend development |
| FastAPI | REST API |
| PostgreSQL | Relational database |
| SQLAlchemy 2 | ORM and transactions |
| Psycopg 3 | PostgreSQL driver |
| Pydantic 2 | Request and response validation |
| Alembic | Database migrations |
| python-dotenv | Environment configuration |
| Uvicorn | ASGI server |
| pytest | Automated testing |

## Project Structure

```text
Warehouse-Managment-System/
├── api/
│   ├── routers/
│   │   ├── inventory.py
│   │   ├── orders.py
│   │   ├── products.py
│   │   └── suppliers.py
│   ├── dependencies.py
│   └── exception_handlers.py
├── database/
│   ├── base.py
│   └── connection.py
├── exceptions/
│   └── business.py
├── migrations/
│   ├── versions/
│   └── env.py
├── models/
│   ├── order.py
│   ├── order_item.py
│   ├── product.py
│   ├── product_suppliers.py
│   ├── stock_movement.py
│   └── supplier.py
├── schemas/
│   ├── inventory.py
│   ├── order.py
│   ├── product.py
│   └── supplier.py
├── services/
│   ├── inventory_services.py
│   ├── order_service.py
│   ├── product_service.py
│   └── supplier_service.py
├── tests/
│   ├── conftest.py
│   ├── test_inventory_service.py
│   ├── test_order_service.py
│   ├── test_product_service.py
│   └── test_supplier_service.py
├── alembic.ini
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

## Architecture

The application uses a layered architecture:

```text
Client / Swagger UI
        |
   FastAPI routers
        |  Pydantic schemas
   Service layer
        |
   SQLAlchemy ORM
        |
    PostgreSQL
```

Routers handle HTTP requests, schemas validate data, and services implement business rules. Database sessions are injected into endpoints; transactional dependencies commit successful operations and roll back on exceptions. Custom exception handlers translate business and database errors into HTTP responses.

The database contains six tables: `products`, `suppliers`, `product_suppliers`, `orders`, `order_items` and `stock_movements`.

## Getting Started

### 1. Clone the repository

Prerequisites: Python 3.10+, PostgreSQL and Git.

```bash
git clone https://github.com/marinobarnjak/Warehouse-Managment-System.git
cd Warehouse-Managment-System
python -m venv .venv
```

Activate the virtual environment on Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure PostgreSQL

Create an empty PostgreSQL database (for example, `wms`) and a `.env` file in the project root. Replace the example credentials with your own:

```dotenv
DB_SERVER=localhost
DB_PORT=5432
DB_NAME=wms
DB_USER=postgres
DB_PASSWORD=your_password
```

Do not commit `.env` or `.env.test` to version control.

### 4. Apply database migrations

```bash
alembic upgrade head
```

### 5. Run the application

```bash
python -m uvicorn app:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | Check API availability |
| GET | `/products/` | List products |
| POST | `/products/` | Create product |
| GET | `/products/{sku}` | Get product |
| PATCH | `/products/{sku}` | Rename product |
| DELETE | `/products/{sku}` | Delete product |
| POST | `/inventory/receive` | Receive stock |
| POST | `/inventory/issue` | Issue stock |
| GET | `/inventory/stock/{sku}` | Check stock |
| GET | `/inventory/low-stock` | List low-stock products |
| GET | `/inventory/movements` | List stock movements |
| GET | `/suppliers/` | List suppliers |
| POST | `/suppliers/` | Create supplier |
| GET | `/suppliers/{id}` | Get supplier |
| POST | `/suppliers/{supplier_id}/products` | Associate a product |
| GET | `/suppliers/{supplier_id}/products` | List supplier products |
| GET | `/orders/` | List orders |
| POST | `/orders/` | Create order |
| GET | `/orders/{order_id}` | Get order |
| POST | `/orders/{order_id}/items` | Add order item |
| POST | `/orders/{order_id}/complete-order` | Complete order |
| POST | `/orders/{order_id}/cancel-order` | Cancel order |

## Running Tests

The project contains service-layer tests for product management, inventory, suppliers and orders, including validation, stock movement history, status transitions and order transaction atomicity.

Create a separate PostgreSQL database named `wms_test`. Add a `.env.test` file in the project root:

```dotenv
DB_SERVER=localhost
DB_PORT=5432
DB_NAME=wms_test
DB_USER=postgres
DB_PASSWORD=your_password
```

Run tests from the project root:

```bash
python -m pytest -v
```

The test setup verifies the database name, creates tables from the ORM metadata and rolls back each test transaction to isolate test data.

## Development Roadmap

- [x] Database design and migrations
- [x] Product management
- [x] Inventory management and low-stock checks
- [x] Stock movement history
- [x] Supplier management
- [x] Purchase order management
- [x] REST API and data validation
- [x] Transaction management and inventory row locking
- [x] Custom exception handling
- [x] Service-layer test suite
- [ ] Application logging and broader operation history
- [ ] Web user interface

## Author

[Marino Barnjak](https://github.com/marinobarnjak)

This project is developed for learning and practical backend development experience.
