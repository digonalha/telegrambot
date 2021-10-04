from src.repositories.models.tracked_sale_model import TrackedSale
from src.helpers.logging_helper import SystemLogging
from src.repositories import tracked_sale_repository
from src.schemas import tracked_sale_schema

tracked_sales = []
syslog = SystemLogging(__name__)


def get_all_tracked_sales() -> None:
    """Fill the global variable tracked_sales with all tracked_sales found in database."""
    global tracked_sales
    tracked_sales = tracked_sale_repository.get_all()


def add_tracked_sale_if_not_exists(tracked_sale: dict) -> TrackedSale:
    """Create a new tracked_sale on database if not exists."""
    try:
        db_tracked_sale = None

        if next(
            (u for u in tracked_sales if u.sale_id == tracked_sale["sale_id"]),
            None,
        ):
            return

        if not tracked_sale_repository.get_by_id(tracked_sale["sale_id"]):
            db_tracked_sale = tracked_sale_repository.add(
                tracked_sale_schema.TrackedSaleCreate(**tracked_sale)
            )

            if db_tracked_sale:
                tracked_sales.append(db_tracked_sale)

        return db_tracked_sale
    except Exception as ex:
        syslog.create_warning("add_tracked_sale_if_not_exists", ex)
