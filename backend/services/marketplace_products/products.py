"""
Marketplace Product Service
===========================
Handles product catalog, suppliers, and e-commerce functionality.
"""

import logging
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============================================================================
# MODELS
# ============================================================================

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class SupplierStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class MarketplaceProduct(BaseModel):
    """E-commerce product in the marketplace"""
    id: UUID = Field(default_factory=uuid4)
    supplier_id: UUID
    name: str
    description: Optional[str] = None
    category: str
    brand: str

    # Pricing
    price: Decimal = Field(..., ge=0)  # In pence/cents
    currency: str = "GBP"
    rrp: Optional[Decimal] = None  # Recommended retail price

    # Inventory
    sku: str
    barcode: Optional[str] = None
    stock_quantity: int = 0
    status: ProductStatus = ProductStatus.ACTIVE

    # Practitioner commission
    practitioner_margin_percent: Decimal = Field(default=Decimal("15.0"))

    # Product details
    ingredients: Optional[str] = None
    directions: Optional[str] = None
    warnings: Optional[str] = None
    size: Optional[str] = None  # "60 capsules", "100ml"

    # Images
    image_urls: List[str] = Field(default_factory=list)
    thumbnail_url: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Supplier(BaseModel):
    """Product supplier/vendor"""
    id: UUID = Field(default_factory=uuid4)
    name: str
    contact_email: str
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    status: SupplierStatus = SupplierStatus.PENDING

    # Business details
    company_registration: Optional[str] = None
    vat_number: Optional[str] = None
    address: Optional[Dict] = None

    # Commission settings
    platform_commission_percent: Decimal = Field(default=Decimal("20.0"))

    # Integration
    api_enabled: bool = False
    api_key: Optional[str] = None

    # Metadata
    product_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CartItem(BaseModel):
    """Shopping cart item"""
    product_id: UUID
    quantity: int = Field(ge=1)
    price_at_add: Decimal


class ShoppingCart(BaseModel):
    """User's shopping cart"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    items: List[CartItem] = Field(default_factory=list)
    prescription_id: Optional[UUID] = None  # If from prescription
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(BaseModel):
    """Customer order"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    practitioner_id: Optional[UUID] = None
    prescription_id: Optional[UUID] = None

    # Items
    items: List[CartItem]

    # Pricing
    subtotal: Decimal
    shipping: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    total: Decimal

    # Commission split
    platform_fee: Decimal
    practitioner_commission: Decimal = Decimal("0")
    supplier_payout: Decimal

    # Status
    status: OrderStatus = OrderStatus.PENDING
    payment_intent_id: Optional[str] = None

    # Shipping
    shipping_address: Optional[Dict] = None
    tracking_number: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


# ============================================================================
# SERVICE
# ============================================================================

class MarketplaceProductService:
    """
    Marketplace Product Service

    Manages:
    - Product catalog
    - Supplier relationships
    - Shopping cart
    - Order processing
    """

    PLATFORM_FEE_PERCENT = Decimal("15.0")  # 15% platform fee
    DEFAULT_PRACTITIONER_MARGIN = Decimal("15.0")  # 15% to practitioners

    def __init__(self):
        # In-memory storage (would be database in production)
        self._products: Dict[UUID, MarketplaceProduct] = {}
        self._suppliers: Dict[UUID, Supplier] = {}
        self._carts: Dict[UUID, ShoppingCart] = {}
        self._orders: Dict[UUID, Order] = {}

        # Seed demo data
        self._seed_demo_data()

    def _seed_demo_data(self):
        """Seed demo products and suppliers"""
        # Create demo suppliers
        suppliers = [
            Supplier(
                id=uuid4(),
                name="Nature's Best Supplements",
                contact_email="orders@naturesbest.com",
                status=SupplierStatus.ACTIVE,
            ),
            Supplier(
                id=uuid4(),
                name="Herbal Traditions Co",
                contact_email="wholesale@herbaltraditions.com",
                status=SupplierStatus.ACTIVE,
            ),
        ]

        for supplier in suppliers:
            self._suppliers[supplier.id] = supplier

        # Create demo products
        supplier_ids = list(self._suppliers.keys())
        products = [
            MarketplaceProduct(
                supplier_id=supplier_ids[0],
                name="Practitioner-Grade Ashwagandha 600mg",
                category="herbs",
                brand="Nature's Best",
                price=Decimal("2499"),  # £24.99
                sku="NB-ASH-600",
                stock_quantity=100,
                size="90 capsules",
            ),
            MarketplaceProduct(
                supplier_id=supplier_ids[0],
                name="High-Potency Magnesium Glycinate",
                category="minerals",
                brand="Nature's Best",
                price=Decimal("1899"),  # £18.99
                sku="NB-MAG-400",
                stock_quantity=150,
                size="120 capsules",
            ),
            MarketplaceProduct(
                supplier_id=supplier_ids[1],
                name="Organic Passionflower Tincture",
                category="herbs",
                brand="Herbal Traditions",
                price=Decimal("1599"),  # £15.99
                sku="HT-PASS-50",
                stock_quantity=75,
                size="50ml",
            ),
            MarketplaceProduct(
                supplier_id=supplier_ids[1],
                name="Clinical Probiotic 50B CFU",
                category="probiotics",
                brand="Herbal Traditions",
                price=Decimal("3499"),  # £34.99
                sku="HT-PRO-50B",
                stock_quantity=50,
                size="30 capsules",
            ),
        ]

        for product in products:
            self._products[product.id] = product
            self._suppliers[product.supplier_id].product_count += 1

    # Product Methods
    def get_product(self, product_id: UUID) -> Optional[MarketplaceProduct]:
        """Get product by ID"""
        return self._products.get(product_id)

    def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        supplier_id: Optional[UUID] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        in_stock_only: bool = True,
        limit: int = 20,
    ) -> List[MarketplaceProduct]:
        """Search and filter products"""
        results = []

        for product in self._products.values():
            # Filter by stock
            if in_stock_only and product.stock_quantity <= 0:
                continue

            # Filter by status
            if product.status != ProductStatus.ACTIVE:
                continue

            # Filter by category
            if category and product.category.lower() != category.lower():
                continue

            # Filter by supplier
            if supplier_id and product.supplier_id != supplier_id:
                continue

            # Filter by price
            if min_price and product.price < min_price:
                continue
            if max_price and product.price > max_price:
                continue

            # Filter by query
            if query:
                query_lower = query.lower()
                if not any([
                    query_lower in product.name.lower(),
                    query_lower in product.brand.lower(),
                    product.description and query_lower in product.description.lower(),
                ]):
                    continue

            results.append(product)

        return results[:limit]

    def get_products_by_category(self, category: str, limit: int = 20) -> List[MarketplaceProduct]:
        """Get products by category"""
        return self.search_products(category=category, limit=limit)

    # Supplier Methods
    def get_supplier(self, supplier_id: UUID) -> Optional[Supplier]:
        """Get supplier by ID"""
        return self._suppliers.get(supplier_id)

    def list_suppliers(self, active_only: bool = True) -> List[Supplier]:
        """List all suppliers"""
        suppliers = list(self._suppliers.values())
        if active_only:
            suppliers = [s for s in suppliers if s.status == SupplierStatus.ACTIVE]
        return suppliers

    def get_supplier_catalog(self, supplier_id: UUID) -> List[MarketplaceProduct]:
        """Get all products from a supplier"""
        return [
            p for p in self._products.values()
            if p.supplier_id == supplier_id and p.status == ProductStatus.ACTIVE
        ]

    # Cart Methods
    def get_or_create_cart(self, user_id: UUID) -> ShoppingCart:
        """Get or create shopping cart for user"""
        for cart in self._carts.values():
            if cart.user_id == user_id:
                return cart

        cart = ShoppingCart(user_id=user_id)
        self._carts[cart.id] = cart
        return cart

    def add_to_cart(
        self,
        user_id: UUID,
        product_id: UUID,
        quantity: int = 1
    ) -> ShoppingCart:
        """Add product to cart"""
        cart = self.get_or_create_cart(user_id)
        product = self.get_product(product_id)

        if not product:
            raise ValueError("Product not found")

        if product.stock_quantity < quantity:
            raise ValueError("Insufficient stock")

        # Check if already in cart
        for item in cart.items:
            if item.product_id == product_id:
                item.quantity += quantity
                cart.updated_at = datetime.utcnow()
                return cart

        # Add new item
        cart.items.append(CartItem(
            product_id=product_id,
            quantity=quantity,
            price_at_add=product.price,
        ))
        cart.updated_at = datetime.utcnow()

        return cart

    def remove_from_cart(self, user_id: UUID, product_id: UUID) -> ShoppingCart:
        """Remove product from cart"""
        cart = self.get_or_create_cart(user_id)
        cart.items = [i for i in cart.items if i.product_id != product_id]
        cart.updated_at = datetime.utcnow()
        return cart

    def get_cart_total(self, cart: ShoppingCart) -> Dict:
        """Calculate cart totals"""
        subtotal = Decimal("0")

        for item in cart.items:
            product = self.get_product(item.product_id)
            if product:
                subtotal += product.price * item.quantity

        platform_fee = subtotal * (self.PLATFORM_FEE_PERCENT / 100)
        total = subtotal  # Add shipping, tax as needed

        return {
            "subtotal": subtotal,
            "platform_fee": platform_fee,
            "total": total,
            "item_count": sum(i.quantity for i in cart.items),
        }

    # Order Methods
    def create_order(
        self,
        user_id: UUID,
        practitioner_id: Optional[UUID] = None,
        prescription_id: Optional[UUID] = None,
        shipping_address: Optional[Dict] = None,
    ) -> Order:
        """Create order from cart"""
        cart = self.get_or_create_cart(user_id)

        if not cart.items:
            raise ValueError("Cart is empty")

        totals = self.get_cart_total(cart)

        # Calculate commission split
        subtotal = totals["subtotal"]
        platform_fee = totals["platform_fee"]

        practitioner_commission = Decimal("0")
        if practitioner_id:
            practitioner_commission = subtotal * (self.DEFAULT_PRACTITIONER_MARGIN / 100)

        supplier_payout = subtotal - platform_fee - practitioner_commission

        order = Order(
            user_id=user_id,
            practitioner_id=practitioner_id,
            prescription_id=prescription_id,
            items=cart.items.copy(),
            subtotal=subtotal,
            total=totals["total"],
            platform_fee=platform_fee,
            practitioner_commission=practitioner_commission,
            supplier_payout=supplier_payout,
            shipping_address=shipping_address,
        )

        self._orders[order.id] = order

        # Clear cart
        cart.items = []
        cart.updated_at = datetime.utcnow()

        return order

    def get_order(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID"""
        return self._orders.get(order_id)

    def get_user_orders(self, user_id: UUID) -> List[Order]:
        """Get all orders for a user"""
        return [o for o in self._orders.values() if o.user_id == user_id]

    def update_order_status(self, order_id: UUID, status: OrderStatus) -> Order:
        """Update order status"""
        order = self.get_order(order_id)
        if not order:
            raise ValueError("Order not found")

        order.status = status

        if status == OrderStatus.PAID:
            order.paid_at = datetime.utcnow()
        elif status == OrderStatus.SHIPPED:
            order.shipped_at = datetime.utcnow()
        elif status == OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()

        return order
