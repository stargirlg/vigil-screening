import io
from datetime import date
import pandas as pd
from app.schemas.customer import CustomerCreate
from app.utils.exceptions import InvalidCSV
from app.utils.logger import get_logger

log = get_logger(__name__)

REQUIRED_COLUMNS = {"full_name"}
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"]


def parse_date(value) -> date | None:
    if not value or str(value).strip() in ("", "nan", "None"):
        return None
    for fmt in DATE_FORMATS:
        try:
            from datetime import datetime
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    return None


def safe_str(value) -> str | None:
    if value is None or str(value).strip() in ("", "nan", "None"):
        return None
    return str(value).strip()


def parse_csv(file_bytes: bytes, source: str = "CSV"):
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        raise InvalidCSV(f"Cannot read file: {e}")

    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise InvalidCSV(f"Missing required columns: {missing}")

    if df.empty:
        raise InvalidCSV("File is empty")

    customers = []
    errors = []

    for idx, row in df.iterrows():
        try:
            customer = CustomerCreate(
                full_name=row["full_name"],
                external_id=safe_str(row.get("external_id") or row.get("id")),
                dob=parse_date(row.get("dob") or row.get("date_of_birth")),
                pan=safe_str(row.get("pan")),
                aadhaar=safe_str(row.get("aadhaar")),
                passport=safe_str(row.get("passport")),
                din=safe_str(row.get("din")),
                uin=safe_str(row.get("uin")),
                nationality=safe_str(row.get("nationality")),
                occupation=safe_str(row.get("occupation")),
                email=safe_str(row.get("email")),
                phone=safe_str(row.get("phone")),
                address=safe_str(row.get("address")),
                source=source,
            )
            customers.append(customer)
        except Exception as e:
            errors.append({"row": idx + 2, "error": str(e)})

    log.info(f"CSV parsed: {len(customers)} valid, {len(errors)} errors")
    return customers, errors