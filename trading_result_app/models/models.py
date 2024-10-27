import datetime as dt

from sqlalchemy import BigInteger, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "spimex_trading_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_product_id: Mapped[str]
    exchange_product_name: Mapped[str]
    delivery_basis_name: Mapped[str]
    oil_id: Mapped[str]
    delivery_basis_id: Mapped[str]
    delivery_type_id: Mapped[str]
    volume: Mapped[int]
    total: Mapped[int] = mapped_column(BigInteger)
    count: Mapped[int]
    date: Mapped[dt.date] = mapped_column(index=True)

    __table_args__ = (
        UniqueConstraint("exchange_product_id", "date", name="uniq_idx_day"),
    )

   
