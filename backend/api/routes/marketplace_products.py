"""
Marketplace Products API Routes
===============================
E-commerce API for the SANA marketplace.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal

from services.marketplace_products import (
    MarketplaceProductService,
    PrescriptionService,
    CommissionService,
)

router = APIRouter()

# Initialize services
product_service = MarketplaceProductService()
prescription_service = PrescriptionService(product_service)
commission_service = CommissionService()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class AddToCartRequest(BaseModel):
    product_id: UUID
    quantity: int = Field(default=1, ge=1)


class CreateOrderRequest(BaseModel):
    practitioner_id: Optional[UUID] = None
    prescription_id: Optional[UUID] = None
    shipping_address: Optional[Dict[str, Any]] = None


class PrescribedItemRequest(BaseModel):
    product_id: UUID
    dosage: str = "As directed"
    frequency: str = "As directed"
    duration: str = "As needed"
    quantity: int = 1
    notes: Optional[str] = None


class CreatePrescriptionRequest(BaseModel):
    practitioner_id: UUID
    client_id: UUID
    items: List[PrescribedItemRequest]
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    expires_days: int = Field(default=90, ge=1, le=365)


class PurchasePrescriptionRequest(BaseModel):
    shipping_address: Optional[Dict[str, Any]] = None


# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@router.get("/products", summary="Browse marketplace products")
async def browse_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: bool = True,
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Browse and search marketplace products.

    Filters:
    - query: Search by name, brand, description
    - category: Filter by category (herbs, vitamins, minerals, etc.)
    - min_price/max_price: Price range in pence
    - in_stock_only: Only show available products
    """
    products = product_service.search_products(
        query=query,
        category=category,
        min_price=Decimal(str(min_price)) if min_price else None,
        max_price=Decimal(str(max_price)) if max_price else None,
        in_stock_only=in_stock_only,
        limit=limit,
    )

    return {
        "products": [p.model_dump() for p in products],
        "total": len(products),
        "filters": {
            "query": query,
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
        }
    }


@router.get("/products/{product_id}", summary="Get product details")
async def get_product(product_id: UUID):
    """Get full product details"""
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    supplier = product_service.get_supplier(product.supplier_id)

    return {
        "product": product.model_dump(),
        "supplier": supplier.model_dump() if supplier else None,
    }


@router.get("/products/category/{category}", summary="Get products by category")
async def get_products_by_category(
    category: str,
    limit: int = Query(default=20, ge=1, le=100),
):
    """Get products in a specific category"""
    products = product_service.get_products_by_category(category, limit)
    return {
        "category": category,
        "products": [p.model_dump() for p in products],
        "total": len(products),
    }


# ============================================================================
# SUPPLIER ENDPOINTS
# ============================================================================

@router.get("/suppliers", summary="List suppliers")
async def list_suppliers(active_only: bool = True):
    """List all product suppliers"""
    suppliers = product_service.list_suppliers(active_only)
    return {
        "suppliers": [s.model_dump() for s in suppliers],
        "total": len(suppliers),
    }


@router.get("/suppliers/{supplier_id}", summary="Get supplier details")
async def get_supplier(supplier_id: UUID):
    """Get supplier details"""
    supplier = product_service.get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier.model_dump()


@router.get("/suppliers/{supplier_id}/catalog", summary="Get supplier catalog")
async def get_supplier_catalog(supplier_id: UUID):
    """Get all products from a supplier"""
    products = product_service.get_supplier_catalog(supplier_id)
    return {
        "supplier_id": str(supplier_id),
        "products": [p.model_dump() for p in products],
        "total": len(products),
    }


# ============================================================================
# CART ENDPOINTS
# ============================================================================

@router.get("/cart/{user_id}", summary="Get shopping cart")
async def get_cart(user_id: UUID):
    """Get user's shopping cart with totals"""
    cart = product_service.get_or_create_cart(user_id)
    totals = product_service.get_cart_total(cart)

    # Enrich items with product details
    enriched_items = []
    for item in cart.items:
        product = product_service.get_product(item.product_id)
        enriched_items.append({
            "product_id": str(item.product_id),
            "product": product.model_dump() if product else None,
            "quantity": item.quantity,
            "price_at_add": float(item.price_at_add),
            "line_total": float(item.price_at_add * item.quantity) if product else 0,
        })

    return {
        "cart_id": str(cart.id),
        "user_id": str(cart.user_id),
        "items": enriched_items,
        "totals": {k: float(v) if isinstance(v, Decimal) else v for k, v in totals.items()},
        "prescription_id": str(cart.prescription_id) if cart.prescription_id else None,
    }


@router.post("/cart/{user_id}/add", summary="Add to cart")
async def add_to_cart(user_id: UUID, request: AddToCartRequest):
    """Add a product to the shopping cart"""
    try:
        cart = product_service.add_to_cart(
            user_id=user_id,
            product_id=request.product_id,
            quantity=request.quantity,
        )
        totals = product_service.get_cart_total(cart)

        return {
            "success": True,
            "message": "Product added to cart",
            "item_count": totals["item_count"],
            "total": float(totals["total"]),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/cart/{user_id}/remove/{product_id}", summary="Remove from cart")
async def remove_from_cart(user_id: UUID, product_id: UUID):
    """Remove a product from the shopping cart"""
    cart = product_service.remove_from_cart(user_id, product_id)
    totals = product_service.get_cart_total(cart)

    return {
        "success": True,
        "message": "Product removed from cart",
        "item_count": totals["item_count"],
    }


# ============================================================================
# ORDER ENDPOINTS
# ============================================================================

@router.post("/orders/{user_id}", summary="Create order")
async def create_order(user_id: UUID, request: CreateOrderRequest):
    """Create an order from the shopping cart"""
    try:
        order = product_service.create_order(
            user_id=user_id,
            practitioner_id=request.practitioner_id,
            prescription_id=request.prescription_id,
            shipping_address=request.shipping_address,
        )

        # Create commission if practitioner involved
        if order.practitioner_id and order.practitioner_commission > 0:
            commission_service.create_commission(
                practitioner_id=order.practitioner_id,
                order_id=order.id,
                client_id=order.user_id,
                order_total=order.subtotal,
            )

        return {
            "order_id": str(order.id),
            "total": float(order.total),
            "status": order.status.value,
            "practitioner_commission": float(order.practitioner_commission),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/{order_id}", summary="Get order details")
async def get_order(order_id: UUID):
    """Get order details"""
    order = product_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order.model_dump()


@router.get("/orders/user/{user_id}", summary="Get user orders")
async def get_user_orders(user_id: UUID):
    """Get all orders for a user"""
    orders = product_service.get_user_orders(user_id)
    return {
        "orders": [o.model_dump() for o in orders],
        "total": len(orders),
    }


# ============================================================================
# PRESCRIPTION ENDPOINTS
# ============================================================================

@router.post("/prescriptions", summary="Create prescription")
async def create_prescription(request: CreatePrescriptionRequest):
    """
    Create a prescription for a client.

    Practitioner prescribes products that client can purchase.
    """
    try:
        items_data = [item.model_dump() for item in request.items]

        prescription = prescription_service.create_prescription(
            practitioner_id=request.practitioner_id,
            client_id=request.client_id,
            items=items_data,
            diagnosis=request.diagnosis,
            notes=request.notes,
            expires_days=request.expires_days,
        )

        return {
            "prescription_id": str(prescription.id),
            "status": prescription.status.value,
            "purchase_url": prescription_service.get_prescription_purchase_url(prescription.id),
            "expires_at": prescription.expires_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/prescriptions/{prescription_id}", summary="Get prescription")
async def get_prescription(prescription_id: UUID):
    """Get prescription details"""
    prescription = prescription_service.get_prescription(prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription.model_dump()


@router.get("/prescriptions/client/{client_id}", summary="Get client prescriptions")
async def get_client_prescriptions(
    client_id: UUID,
    active_only: bool = True,
):
    """Get all prescriptions for a client"""
    prescriptions = prescription_service.get_client_prescriptions(client_id, active_only)
    return {
        "prescriptions": [p.model_dump() for p in prescriptions],
        "total": len(prescriptions),
    }


@router.post("/prescriptions/{prescription_id}/purchase", summary="Purchase prescription")
async def purchase_prescription(
    prescription_id: UUID,
    request: PurchasePrescriptionRequest,
):
    """Purchase all items in a prescription"""
    try:
        result = prescription_service.purchase_prescription(
            prescription_id=prescription_id,
            shipping_address=request.shipping_address,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# COMMISSION ENDPOINTS
# ============================================================================

@router.get("/commissions/{practitioner_id}", summary="Get practitioner commissions")
async def get_practitioner_commissions(practitioner_id: UUID):
    """Get commission summary for a practitioner"""
    summary = commission_service.get_commission_summary(practitioner_id)
    commissions = commission_service.get_practitioner_commissions(practitioner_id)

    return {
        "summary": summary,
        "recent_commissions": [c.model_dump() for c in commissions[:10]],
    }


@router.get("/commissions/{practitioner_id}/monthly", summary="Monthly commission breakdown")
async def get_monthly_commissions(
    practitioner_id: UUID,
    months: int = Query(default=6, ge=1, le=12),
):
    """Get monthly commission breakdown"""
    breakdown = commission_service.get_monthly_breakdown(practitioner_id, months)
    return {
        "practitioner_id": str(practitioner_id),
        "breakdown": breakdown,
    }


@router.post("/commissions/{practitioner_id}/payout", summary="Request payout")
async def request_payout(practitioner_id: UUID):
    """Request commission payout"""
    try:
        payout = commission_service.create_payout(practitioner_id)
        return {
            "payout_id": str(payout.id),
            "amount": float(payout.amount),
            "commission_count": payout.commission_count,
            "status": payout.status,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
