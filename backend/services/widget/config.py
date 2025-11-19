"""
Widget configuration service for practitioner booking widgets.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import hashlib
import logging

logger = logging.getLogger(__name__)


class WidgetStyle(str, Enum):
    """Widget display styles."""
    INLINE = "inline"  # Embedded in page
    POPUP = "popup"    # Modal popup
    SLIDE = "slide"    # Slide-in panel


class WidgetTheme(str, Enum):
    """Widget themes."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Match system


class ServiceType(BaseModel):
    """A bookable service."""
    id: UUID
    name: str
    description: str
    duration_minutes: int
    price: float
    currency: str = "GBP"
    is_active: bool = True


class WidgetConfig(BaseModel):
    """Practitioner widget configuration."""
    id: UUID
    practitioner_id: UUID

    # Widget identifiers
    widget_key: str  # Public key for embedding
    slug: str  # URL-friendly identifier

    # Appearance
    style: WidgetStyle = WidgetStyle.INLINE
    theme: WidgetTheme = WidgetTheme.LIGHT
    primary_color: str = "#6366f1"
    secondary_color: str = "#8b5cf6"
    border_radius: int = 8
    font_family: str = "Inter, system-ui, sans-serif"

    # Branding
    show_sana_branding: bool = True
    custom_logo_url: Optional[str] = None
    custom_header: Optional[str] = None
    custom_footer: Optional[str] = None

    # Display options
    show_profile: bool = True
    show_bio: bool = True
    show_credentials: bool = True
    show_reviews: bool = True
    show_sana_index: bool = True
    show_prices: bool = True

    # Booking options
    services: List[ServiceType] = []
    booking_window_days: int = 60  # How far ahead can book
    min_notice_hours: int = 24  # Minimum notice required
    buffer_minutes: int = 15  # Buffer between appointments
    require_payment: bool = False
    allow_telehealth: bool = True

    # Notifications
    confirmation_message: str = "Your appointment has been confirmed!"
    reminder_hours: int = 24

    # Analytics
    track_views: bool = True
    track_conversions: bool = True

    # Status
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class WidgetAnalytics(BaseModel):
    """Widget analytics data."""
    widget_id: UUID
    total_views: int = 0
    unique_visitors: int = 0
    bookings_started: int = 0
    bookings_completed: int = 0
    conversion_rate: float = 0.0
    top_referrers: List[Dict[str, Any]] = []
    views_by_day: List[Dict[str, Any]] = []


class WidgetConfigService:
    """
    Manages widget configurations for practitioners.

    Features:
    - Widget creation and customization
    - Embed code generation
    - Shareable link generation
    - Analytics tracking
    """

    def __init__(self):
        self.widgets: Dict[UUID, WidgetConfig] = {}
        self.widget_by_key: Dict[str, UUID] = {}
        self.widget_by_slug: Dict[str, UUID] = {}
        self.analytics: Dict[UUID, WidgetAnalytics] = {}
        logger.info("WidgetConfigService initialized")

    def create_widget(
        self,
        practitioner_id: UUID,
        slug: Optional[str] = None,
        services: Optional[List[Dict]] = None
    ) -> WidgetConfig:
        """
        Create a new widget for a practitioner.

        Args:
            practitioner_id: Practitioner UUID
            slug: Custom URL slug (generated if not provided)
            services: Initial services to offer

        Returns:
            Created widget config
        """
        # Generate widget key
        widget_key = self._generate_widget_key(practitioner_id)

        # Generate slug if not provided
        if not slug:
            slug = f"book-{uuid4().hex[:8]}"

        # Ensure unique slug
        if slug in self.widget_by_slug:
            slug = f"{slug}-{uuid4().hex[:4]}"

        now = datetime.utcnow()

        # Convert services
        service_list = []
        if services:
            for s in services:
                service_list.append(ServiceType(
                    id=uuid4(),
                    name=s.get("name", "Consultation"),
                    description=s.get("description", ""),
                    duration_minutes=s.get("duration_minutes", 60),
                    price=s.get("price", 0),
                    currency=s.get("currency", "GBP")
                ))

        widget = WidgetConfig(
            id=uuid4(),
            practitioner_id=practitioner_id,
            widget_key=widget_key,
            slug=slug,
            services=service_list,
            created_at=now,
            updated_at=now
        )

        self.widgets[widget.id] = widget
        self.widget_by_key[widget_key] = widget.id
        self.widget_by_slug[slug] = widget.id

        # Initialize analytics
        self.analytics[widget.id] = WidgetAnalytics(widget_id=widget.id)

        logger.info(f"Created widget {widget.id} for practitioner {practitioner_id}")

        return widget

    def _generate_widget_key(self, practitioner_id: UUID) -> str:
        """Generate unique widget key."""
        data = f"{practitioner_id}{datetime.utcnow().timestamp()}{uuid4().hex}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    def get_widget(self, widget_id: UUID) -> Optional[WidgetConfig]:
        """Get widget by ID."""
        return self.widgets.get(widget_id)

    def get_widget_by_key(self, widget_key: str) -> Optional[WidgetConfig]:
        """Get widget by public key."""
        widget_id = self.widget_by_key.get(widget_key)
        if widget_id:
            return self.widgets.get(widget_id)
        return None

    def get_widget_by_slug(self, slug: str) -> Optional[WidgetConfig]:
        """Get widget by URL slug."""
        widget_id = self.widget_by_slug.get(slug)
        if widget_id:
            return self.widgets.get(widget_id)
        return None

    def get_practitioner_widget(self, practitioner_id: UUID) -> Optional[WidgetConfig]:
        """Get widget for a practitioner."""
        for widget in self.widgets.values():
            if widget.practitioner_id == practitioner_id:
                return widget
        return None

    def update_widget(
        self,
        widget_id: UUID,
        updates: Dict[str, Any]
    ) -> WidgetConfig:
        """Update widget configuration."""
        if widget_id not in self.widgets:
            raise ValueError("Widget not found")

        widget = self.widgets[widget_id]

        # Update allowed fields
        allowed_fields = [
            'style', 'theme', 'primary_color', 'secondary_color',
            'border_radius', 'font_family', 'show_sana_branding',
            'custom_logo_url', 'custom_header', 'custom_footer',
            'show_profile', 'show_bio', 'show_credentials',
            'show_reviews', 'show_sana_index', 'show_prices',
            'booking_window_days', 'min_notice_hours', 'buffer_minutes',
            'require_payment', 'allow_telehealth', 'confirmation_message',
            'reminder_hours', 'track_views', 'track_conversions', 'is_active'
        ]

        for key, value in updates.items():
            if key in allowed_fields and hasattr(widget, key):
                setattr(widget, key, value)

        widget.updated_at = datetime.utcnow()
        return widget

    def add_service(
        self,
        widget_id: UUID,
        name: str,
        description: str,
        duration_minutes: int,
        price: float,
        currency: str = "GBP"
    ) -> ServiceType:
        """Add a service to widget."""
        if widget_id not in self.widgets:
            raise ValueError("Widget not found")

        widget = self.widgets[widget_id]

        service = ServiceType(
            id=uuid4(),
            name=name,
            description=description,
            duration_minutes=duration_minutes,
            price=price,
            currency=currency
        )

        widget.services.append(service)
        widget.updated_at = datetime.utcnow()

        return service

    def remove_service(self, widget_id: UUID, service_id: UUID) -> bool:
        """Remove a service from widget."""
        if widget_id not in self.widgets:
            return False

        widget = self.widgets[widget_id]
        widget.services = [s for s in widget.services if s.id != service_id]
        widget.updated_at = datetime.utcnow()

        return True

    def generate_embed_code(
        self,
        widget_id: UUID,
        base_url: str = "https://sana.health"
    ) -> Dict[str, str]:
        """
        Generate embed codes for the widget.

        Returns multiple embed options.
        """
        if widget_id not in self.widgets:
            raise ValueError("Widget not found")

        widget = self.widgets[widget_id]

        # Inline embed (iframe)
        iframe_code = f'''<iframe
  src="{base_url}/widget/{widget.widget_key}"
  style="width: 100%; min-height: 600px; border: none; border-radius: {widget.border_radius}px;"
  title="Book with SANA"
  loading="lazy"
></iframe>'''

        # JavaScript embed (more flexible)
        js_code = f'''<div id="sana-widget"></div>
<script src="{base_url}/widget/embed.js"></script>
<script>
  SANAWidget.init({{
    key: '{widget.widget_key}',
    container: '#sana-widget',
    style: '{widget.style.value}',
    theme: '{widget.theme.value}',
    primaryColor: '{widget.primary_color}'
  }});
</script>'''

        # Popup button
        popup_code = f'''<button onclick="SANAWidget.open('{widget.widget_key}')">
  Book Appointment
</button>
<script src="{base_url}/widget/embed.js"></script>'''

        # React component
        react_code = f'''import {{ SANAWidget }} from '@sana/widget-react';

<SANAWidget
  widgetKey="{widget.widget_key}"
  style="{widget.style.value}"
  theme="{widget.theme.value}"
  primaryColor="{widget.primary_color}"
/>'''

        return {
            "iframe": iframe_code,
            "javascript": js_code,
            "popup": popup_code,
            "react": react_code
        }

    def generate_shareable_link(
        self,
        widget_id: UUID,
        base_url: str = "https://sana.health"
    ) -> Dict[str, str]:
        """Generate shareable booking links."""
        if widget_id not in self.widgets:
            raise ValueError("Widget not found")

        widget = self.widgets[widget_id]

        return {
            "booking_page": f"{base_url}/book/{widget.slug}",
            "short_link": f"{base_url}/b/{widget.slug}",
            "calendar_link": f"{base_url}/book/{widget.slug}/calendar",
            "qr_code_url": f"{base_url}/api/v1/widget/{widget.widget_key}/qr"
        }

    def track_view(
        self,
        widget_id: UUID,
        referrer: Optional[str] = None,
        visitor_id: Optional[str] = None
    ) -> None:
        """Track a widget view."""
        if widget_id not in self.analytics:
            return

        analytics = self.analytics[widget_id]
        analytics.total_views += 1

        # Track unique visitors (simplified)
        if visitor_id:
            analytics.unique_visitors += 1

        # Track referrer
        if referrer:
            for ref in analytics.top_referrers:
                if ref["domain"] == referrer:
                    ref["count"] += 1
                    break
            else:
                analytics.top_referrers.append({
                    "domain": referrer,
                    "count": 1
                })

    def track_booking_started(self, widget_id: UUID) -> None:
        """Track when booking flow is started."""
        if widget_id in self.analytics:
            self.analytics[widget_id].bookings_started += 1

    def track_booking_completed(self, widget_id: UUID) -> None:
        """Track when booking is completed."""
        if widget_id in self.analytics:
            analytics = self.analytics[widget_id]
            analytics.bookings_completed += 1

            # Update conversion rate
            if analytics.bookings_started > 0:
                analytics.conversion_rate = (
                    analytics.bookings_completed / analytics.bookings_started
                )

    def get_analytics(self, widget_id: UUID) -> Optional[WidgetAnalytics]:
        """Get widget analytics."""
        return self.analytics.get(widget_id)

    def regenerate_widget_key(self, widget_id: UUID) -> str:
        """Regenerate widget key (invalidates old embeds)."""
        if widget_id not in self.widgets:
            raise ValueError("Widget not found")

        widget = self.widgets[widget_id]

        # Remove old key
        if widget.widget_key in self.widget_by_key:
            del self.widget_by_key[widget.widget_key]

        # Generate new key
        new_key = self._generate_widget_key(widget.practitioner_id)
        widget.widget_key = new_key
        widget.updated_at = datetime.utcnow()

        self.widget_by_key[new_key] = widget_id

        return new_key
