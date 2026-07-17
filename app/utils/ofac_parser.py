import requests
from datetime import date, datetime
from lxml import etree
from app.models.sanction_entry import SanctionEntry
from app.utils.logger import get_logger

log = get_logger(__name__)


def _text(element, tag: str) -> str | None:
    el = element.find(tag)
    return el.text.strip() if el is not None and el.text else None


def _parse_dob(dob_str: str | None) -> date | None:
    if not dob_str:
        return None
    for fmt in ["%d %b %Y", "%Y-%m-%d", "%Y"]:
        try:
            return datetime.strptime(dob_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def parse_ofac_xml(xml_bytes: bytes) -> list[SanctionEntry]:
    try:
        root = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as e:
        log.error(f"OFAC XML parse error: {e}")
        return []

    entries = []

    for sdn in root.iter("{*}sdnEntry"):
        sdn_type = _text(sdn, "{*}sdnType") or ""
        if sdn_type.lower() not in ("individual", "entity"):
            continue

        last = _text(sdn, "{*}lastName") or ""
        first = _text(sdn, "{*}firstName") or ""
        full_name = f"{first} {last}".strip() or last

        if not full_name:
            continue

        aliases = []
        for aka in sdn.iter("{*}aka"):
            aka_last = _text(aka, "{*}lastName") or ""
            aka_first = _text(aka, "{*}firstName") or ""
            alias_name = f"{aka_first} {aka_last}".strip()
            if alias_name and alias_name != full_name:
                aliases.append(alias_name)

        dob = None
        for dob_item in sdn.iter("{*}dateOfBirthItem"):
            dob_str = _text(dob_item, "{*}dateOfBirth")
            dob = _parse_dob(dob_str)
            if dob:
                break

        programs = [p.text for p in sdn.iter("{*}program") if p.text]
        program_str = ", ".join(programs[:3])

        passport = None
        national_id = None
        for id_item in sdn.iter("{*}id"):
            id_type = (_text(id_item, "{*}idType") or "").lower()
            id_number = _text(id_item, "{*}idNumber")
            if not id_number:
                continue
            if "passport" in id_type and not passport:
                passport = id_number
            elif "national" in id_type and not national_id:
                national_id = id_number

        nationality = None
        for pob in sdn.iter("{*}placeOfBirthItem"):
            nationality = _text(pob, "{*}placeOfBirth")
            break

        entry = SanctionEntry(
            source="OFAC",
            source_id=_text(sdn, "{*}uid"),
            full_name=full_name,
            aliases=aliases,
            dob=dob,
            nationality=nationality,
            passport=passport,
            national_id=national_id,
            program=program_str,
            is_active="true",
        )
        entries.append(entry)

    log.info(f"Parsed {len(entries)} entries from OFAC XML")
    return entries


def download_and_parse_ofac(url: str) -> list[SanctionEntry]:
    """
    Download OFAC SDN list. Tries multiple known URLs.
    Falls back gracefully if all fail.
    """
    urls_to_try = [
        url,
        "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.XML",
        "https://www.treasury.gov/ofac/downloads/sdn.xml",
    ]

    for try_url in urls_to_try:
        log.info(f"Trying OFAC URL: {try_url}")
        try:
            resp = requests.get(try_url, timeout=60, headers={
                "User-Agent": "VIGIL-Compliance/1.0"
            })
            if resp.status_code == 200 and len(resp.content) > 1000:
                log.info(f"OFAC download success: {len(resp.content)} bytes")
                return parse_ofac_xml(resp.content)
        except requests.RequestException as e:
            log.warning(f"Failed {try_url}: {e}")
            continue

    log.error("All OFAC URLs failed — using local seed data")
    return []