from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum


# Enums for type safety
class AssetType(str, Enum):
    STOCK = "stock"
    OPTION = "option"
    CRYPTO = "crypto"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True)
    email: str = Field(unique=True, max_length=255)
    full_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    portfolios: List["Portfolio"] = Relationship(back_populates="user")
    watchlists: List["Watchlist"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="user")


class Asset(SQLModel, table=True):
    __tablename__ = "assets"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(max_length=20, unique=True, index=True)
    name: str = Field(max_length=200)
    asset_type: AssetType = Field(index=True)
    exchange: str = Field(max_length=50)
    current_price: Decimal = Field(decimal_places=8, max_digits=20)
    market_cap: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=20)
    volume_24h: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=20)
    price_change_24h: Decimal = Field(default=Decimal("0"), decimal_places=8, max_digits=20)
    price_change_percent_24h: Decimal = Field(default=Decimal("0"), decimal_places=4, max_digits=10)
    is_active: bool = Field(default=True)
    asset_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    options: List["Option"] = Relationship(back_populates="underlying_asset")
    holdings: List["Holding"] = Relationship(back_populates="asset")
    watchlist_items: List["WatchlistItem"] = Relationship(back_populates="asset")
    orders: List["Order"] = Relationship(back_populates="asset")
    price_history: List["PriceHistory"] = Relationship(back_populates="asset")


class Option(SQLModel, table=True):
    __tablename__ = "options"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(max_length=50, unique=True, index=True)
    underlying_asset_id: int = Field(foreign_key="assets.id")
    option_type: OptionType
    strike_price: Decimal = Field(decimal_places=8, max_digits=20)
    expiration_date: datetime
    current_price: Decimal = Field(decimal_places=8, max_digits=20)
    implied_volatility: Optional[Decimal] = Field(default=None, decimal_places=4, max_digits=10)
    delta: Optional[Decimal] = Field(default=None, decimal_places=6, max_digits=10)
    gamma: Optional[Decimal] = Field(default=None, decimal_places=6, max_digits=10)
    theta: Optional[Decimal] = Field(default=None, decimal_places=6, max_digits=10)
    vega: Optional[Decimal] = Field(default=None, decimal_places=6, max_digits=10)
    open_interest: Optional[int] = Field(default=None)
    volume: Optional[int] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    underlying_asset: Asset = Relationship(back_populates="options")
    holdings: List["Holding"] = Relationship(back_populates="option")
    orders: List["Order"] = Relationship(back_populates="option")


class Portfolio(SQLModel, table=True):
    __tablename__ = "portfolios"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    cash_balance: Decimal = Field(default=Decimal("100000.00"), decimal_places=2, max_digits=20)
    total_value: Decimal = Field(default=Decimal("100000.00"), decimal_places=2, max_digits=20)
    unrealized_pnl: Decimal = Field(default=Decimal("0.00"), decimal_places=2, max_digits=20)
    realized_pnl: Decimal = Field(default=Decimal("0.00"), decimal_places=2, max_digits=20)
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="portfolios")
    holdings: List["Holding"] = Relationship(back_populates="portfolio")
    orders: List["Order"] = Relationship(back_populates="portfolio")


class Holding(SQLModel, table=True):
    __tablename__ = "holdings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolios.id")
    asset_id: Optional[int] = Field(default=None, foreign_key="assets.id")
    option_id: Optional[int] = Field(default=None, foreign_key="options.id")
    quantity: Decimal = Field(decimal_places=8, max_digits=20)
    average_cost: Decimal = Field(decimal_places=8, max_digits=20)
    current_value: Decimal = Field(decimal_places=2, max_digits=20)
    unrealized_pnl: Decimal = Field(decimal_places=2, max_digits=20)
    unrealized_pnl_percent: Decimal = Field(decimal_places=4, max_digits=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    portfolio: Portfolio = Relationship(back_populates="holdings")
    asset: Optional[Asset] = Relationship(back_populates="holdings")
    option: Optional[Option] = Relationship(back_populates="holdings")


class Watchlist(SQLModel, table=True):
    __tablename__ = "watchlists"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="watchlists")
    items: List["WatchlistItem"] = Relationship(back_populates="watchlist")


class WatchlistItem(SQLModel, table=True):
    __tablename__ = "watchlist_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    watchlist_id: int = Field(foreign_key="watchlists.id")
    asset_id: int = Field(foreign_key="assets.id")
    notes: str = Field(default="", max_length=500)
    price_alert_high: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    price_alert_low: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    added_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    watchlist: Watchlist = Relationship(back_populates="items")
    asset: Asset = Relationship(back_populates="watchlist_items")


class Order(SQLModel, table=True):
    __tablename__ = "orders"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    portfolio_id: int = Field(foreign_key="portfolios.id")
    asset_id: Optional[int] = Field(default=None, foreign_key="assets.id")
    option_id: Optional[int] = Field(default=None, foreign_key="options.id")
    order_type: OrderType
    side: OrderSide
    quantity: Decimal = Field(decimal_places=8, max_digits=20)
    price: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    stop_price: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    filled_quantity: Decimal = Field(default=Decimal("0"), decimal_places=8, max_digits=20)
    average_fill_price: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    status: OrderStatus = Field(default=OrderStatus.PENDING, index=True)
    time_in_force: str = Field(default="GTC", max_length=10)  # GTC, DAY, IOC, FOK
    notes: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    filled_at: Optional[datetime] = Field(default=None)
    cancelled_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="orders")
    portfolio: Portfolio = Relationship(back_populates="orders")
    asset: Optional[Asset] = Relationship(back_populates="orders")
    option: Optional[Option] = Relationship(back_populates="orders")
    executions: List["OrderExecution"] = Relationship(back_populates="order")


class OrderExecution(SQLModel, table=True):
    __tablename__ = "order_executions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    execution_price: Decimal = Field(decimal_places=8, max_digits=20)
    execution_quantity: Decimal = Field(decimal_places=8, max_digits=20)
    commission: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=10)
    fees: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=10)
    executed_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    order: Order = Relationship(back_populates="executions")


class PriceHistory(SQLModel, table=True):
    __tablename__ = "price_history"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="assets.id", index=True)
    timestamp: datetime = Field(index=True)
    open_price: Decimal = Field(decimal_places=8, max_digits=20)
    high_price: Decimal = Field(decimal_places=8, max_digits=20)
    low_price: Decimal = Field(decimal_places=8, max_digits=20)
    close_price: Decimal = Field(decimal_places=8, max_digits=20)
    volume: Decimal = Field(decimal_places=2, max_digits=20)
    timeframe: str = Field(max_length=10, index=True)  # 1m, 5m, 15m, 1h, 4h, 1d

    # Relationships
    asset: Asset = Relationship(back_populates="price_history")


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    full_name: str = Field(max_length=100)


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)


class AssetCreate(SQLModel, table=False):
    symbol: str = Field(max_length=20)
    name: str = Field(max_length=200)
    asset_type: AssetType
    exchange: str = Field(max_length=50)
    current_price: Decimal = Field(decimal_places=8, max_digits=20)
    market_cap: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=20)
    asset_metadata: Dict[str, Any] = Field(default={})


class AssetUpdate(SQLModel, table=False):
    current_price: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    market_cap: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=20)
    volume_24h: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=20)
    price_change_24h: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    price_change_percent_24h: Optional[Decimal] = Field(default=None, decimal_places=4, max_digits=10)
    is_active: Optional[bool] = Field(default=None)


class OptionCreate(SQLModel, table=False):
    symbol: str = Field(max_length=50)
    underlying_asset_id: int
    option_type: OptionType
    strike_price: Decimal = Field(decimal_places=8, max_digits=20)
    expiration_date: datetime
    current_price: Decimal = Field(decimal_places=8, max_digits=20)


class PortfolioCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    cash_balance: Decimal = Field(default=Decimal("100000.00"), decimal_places=2, max_digits=20)


class PortfolioUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    cash_balance: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=20)


class WatchlistCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)


class WatchlistItemCreate(SQLModel, table=False):
    asset_id: int
    notes: str = Field(default="", max_length=500)
    price_alert_high: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    price_alert_low: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)


class OrderCreate(SQLModel, table=False):
    portfolio_id: int
    asset_id: Optional[int] = Field(default=None)
    option_id: Optional[int] = Field(default=None)
    order_type: OrderType
    side: OrderSide
    quantity: Decimal = Field(decimal_places=8, max_digits=20)
    price: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    stop_price: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    time_in_force: str = Field(default="GTC", max_length=10)
    notes: str = Field(default="", max_length=500)


class OrderUpdate(SQLModel, table=False):
    quantity: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    price: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    stop_price: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20)
    status: Optional[OrderStatus] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)


class QuickTradeRequest(SQLModel, table=False):
    portfolio_id: int
    asset_id: Optional[int] = Field(default=None)
    option_id: Optional[int] = Field(default=None)
    side: OrderSide
    quantity: Decimal = Field(decimal_places=8, max_digits=20)
    order_type: OrderType = Field(default=OrderType.MARKET)


class PortfolioSummary(SQLModel, table=False):
    total_value: Decimal
    cash_balance: Decimal
    invested_value: Decimal
    unrealized_pnl: Decimal
    unrealized_pnl_percent: Decimal
    realized_pnl: Decimal
    day_change: Decimal
    day_change_percent: Decimal
    holdings_count: int
