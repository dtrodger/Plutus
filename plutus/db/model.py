"""
SQLAlchemy models
"""

from sqlalchemy import Column, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from plutus.db import util as db_util


class Price(db_util.SQLModel):
    """
    Price SQLAlchemy model
    """

    __tablename__ = "price"

    instant = Column(DateTime)
    symbol = Column(String)
    exchange = Column(String)
    price = Column(Float)
    bid = Column(Float)
    ask = Column(Float)
    trade_prices = relationship("TradePrice", backref="price")

    def __str__(self):
        return f"{self.exchange} price for {self.symbol} at {self.instant}"


class Trade(db_util.SQLModel):
    """
    Trade SQLAlchemy model
    """

    __tablename__ = "trade"

    event_instant = Column(DateTime)
    symbol = Column(String)
    exchange = Column(String)
    trade_prices = relationship("TradePrice", backref="trade")

    def __str__(self):
        return f"{self.exchange} trade for {self.symbol} at {self.instant}"


class TradePrice(db_util.SQLModel):
    """
    TradePrice SQLAlchemy model
    """

    __tablename__ = "trade_price"

    price_id = Column(ForeignKey("price.id"), nullable=False)
    trade_id = Column(ForeignKey("trade.id"), nullable=False)

    def __str__(self):
        return f"{self.trade.exchange} trade price for {self.trade.symbol}"
