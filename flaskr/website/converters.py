"""
This module maps every field defined in the data-contract to
the SQLAlchemy models in models.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import re

from .models import (
    db,
    Patient,
    Prescriber,
    Prescription,
    ASLStatus,
    PrescriptionStatus,
)

DATE_FMT = "%d/%m/%Y"  # DD/MM/YYYY format

ASL_STATUS_ALLOWED = {
    "NO CONSENT": ASLStatus.NO_CONSENT,
    "NO_CONSENT": ASLStatus.NO_CONSENT,
    "PENDING": ASLStatus.PENDING,
    "GRANTED": ASLStatus.GRANTED,
    "REJECTED": ASLStatus.REJECTED,
}

TOP_LEVEL_REQUIRED = [
    "medicare",
    "pharmaceut-ben-entitlement-no",
    "sfty-net-entitlement-cardholder",
    "rpbs-ben-entitlement-cardholder",
    "name",
    "dob",
    "preferred-contact",
    "address-1",
    "address-2",
    "script-date",
    "consent-status",
    "asl-data",
    "alr-data",
]

PRESCRIBER_REQUIRED = [
    "fname",
    "lname",
    "address-1",
    "address-2",
    "id",
    "hpii",
    "hpio",
    "phone",
]

ASL_ITEM_REQUIRED = [
    "DSPID",
    "status",
    "drug-name",
    "drug-code",
    "dose-instr",
    "dose-qty",
    "dose-rpt",
    "prescribed-date",
    "paperless",
    "brand-sub-not-prmt",
    "prescriber",
]

ALR_ITEM_REQUIRED = [
    "drug-name",
    "drug-code",
    "dose-instr",
    "dose-qty",
    "dose-rpt",
    "prescribed-date",
    "dispensed-date",
    "paperless",
    "brand-sub-not-prmt",
    "remaining-repeats",
    "prescriber",
]

_MEDICARE_RE = re.compile(r"^\d{11}$")
_16_DIGIT_RE = re.compile(r"^\d{16}$")
_DRUG_CODE_RE = re.compile(r"^[A-Z0-9]{4,6}$", re.I)


class ContractValidationError(ValueError):
    pass


def _require_keys(obj: Dict[str, Any], keys: List[str], where: str):
    missing = [k for k in keys if k not in obj]
    if missing:
        raise ContractValidationError(f"Missing {missing} in {where}")


def _to_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        if val.strip().lower() in {"true", "1", "yes", "y"}:
            return True
        if val.strip().lower() in {"false", "0", "no", "n"}:
            return False
    if isinstance(val, (int, float)):
        return bool(val)
    raise ContractValidationError(f"Cannot convert {val!r} to bool")


def _digits_only_int(val: Any, digits: int | None = None, field="") -> int:
    s = re.sub(r"\D", "", str(val))
    if not s:
        raise ContractValidationError(f"{field or 'value'} must be numeric")
    if digits and len(s) != digits:
        raise ContractValidationError(f"{field} must be {digits} digits")
    return int(s)


def _validate_date(s: Any, field: str) -> str:
    try:
        datetime.strptime(str(s), DATE_FMT)
        return str(s)
    except Exception:
        raise ContractValidationError(f"{field} must be DD/MM/YYYY")


def _validate_drug_code(code: Any) -> str:
    c = str(code)
    if not _DRUG_CODE_RE.match(c):
        raise ContractValidationError(f"Invalid drug-code: {code}")
    return c


def _asl_status_from_str(status: str) -> ASLStatus:
    key = status.strip().upper().replace("_", " ")
    if key not in ASL_STATUS_ALLOWED:
        raise ContractValidationError(f"Invalid ASL status {status}")
    return ASL_STATUS_ALLOWED[key]


def _get_or_create_prescriber(p: Dict[str, Any]) -> Prescriber:
    _require_keys(p, PRESCRIBER_REQUIRED, where="prescriber")
    pid = _digits_only_int(p["id"], field="prescriber.id")
    existing = Prescriber.query.filter_by(prescriber_id=pid).first()
    if existing:
        existing.fname = p.get("fname", existing.fname)
        existing.lname = p.get("lname", existing.lname)
        existing.title = p.get("title", existing.title)
        existing.address_1 = p.get("address-1", existing.address_1)
        existing.address_2 = p.get("address-2", existing.address_2)
        existing.hpii = _digits_only_int(p["hpii"], digits=16, field="hpii")
        existing.hpio = _digits_only_int(p["hpio"], digits=16, field="hpio")
        existing.phone = str(p["phone"])
        existing.fax = p.get("fax", existing.fax)
        return existing
    prescriber = Prescriber(
        fname=p["fname"],
        lname=p["lname"],
        title=p.get("title"),
        address_1=p["address-1"],
        address_2=p["address-2"],
        prescriber_id=pid,
        hpii=_digits_only_int(p["hpii"], digits=16, field="hpii"),
        hpio=_digits_only_int(p["hpio"], digits=16, field="hpio"),
        phone=str(p["phone"]),
        fax=p.get("fax"),
    )
    db.session.add(prescriber)
    return prescriber


@dataclass
class IngestResult:
    patient: Patient
    prescribers: List[Prescriber]
    prescriptions: List[Prescription]
    created_prescribers: int
    created_prescriptions: int
    is_new_patient: bool


def _build_patient(contract: Dict[str, Any]) -> Patient:
    _require_keys(contract, TOP_LEVEL_REQUIRED, where="pt_data")
    patient = Patient(
        medicare=_digits_only_int(contract["medicare"], digits=11, field="medicare"),
        pharmaceut_ben_entitlement_no=contract["pharmaceut-ben-entitlement-no"],
        sfty_net_entitlement_cardholder=_to_bool(
            contract["sfty-net-entitlement-cardholder"]
        ),
        rpbs_ben_entitlement_cardholder=_to_bool(
            contract["rpbs-ben-entitlement-cardholder"]
        ),
        name=contract["name"],
        dob=_validate_date(contract["dob"], field="dob"),
        preferred_contact=_digits_only_int(
            contract["preferred-contact"], field="preferred-contact"
        ),
        address_1=contract["address-1"],
        address_2=contract["address-2"],
        script_date=_validate_date(contract["script-date"], field="script-date"),
        pbs=contract.get("pbs"),
        rpbs=contract.get("rpbs"),
        asl_status=_asl_status_from_str(contract["consent-status"]["status"]).value,
        is_registered=_to_bool(contract["consent-status"]["is-registered"]),
    )
    if contract["consent-status"].get("last-updated"):
        patient.consent_last_updated = str(contract["consent-status"]["last-updated"])
    return patient


def _build_prescription_from_asl(item, patient, prescriber):
    _require_keys(item, ASL_ITEM_REQUIRED, where="asl-data item")
    return Prescription(
        patient=patient,
        prescriber=prescriber,
        DSPID=item.get("DSPID"),
        status=PrescriptionStatus.AVAILABLE.value,
        drug_name=item["drug-name"],
        drug_code=_validate_drug_code(item["drug-code"]),
        dose_instr=item["dose-instr"],
        dose_qty=_digits_only_int(item["dose-qty"], field="dose-qty"),
        dose_rpt=_digits_only_int(item["dose-rpt"], field="dose-rpt"),
        prescribed_date=_validate_date(
            item["prescribed-date"], field="prescribed-date"
        ),
        paperless=_to_bool(item["paperless"]),
        brand_sub_not_prmt=_to_bool(item["brand-sub-not-prmt"]),
    )


def _build_prescription_from_alr(item, patient, prescriber):
    _require_keys(item, ALR_ITEM_REQUIRED, where="alr-data item")
    remaining = _digits_only_int(item["remaining-repeats"], field="remaining-repeats")
    if remaining <= 0:
        raise ContractValidationError("remaining-repeats must be > 0")
    return Prescription(
        patient=patient,
        prescriber=prescriber,
        DSPID=item.get("DSPID"),
        status=PrescriptionStatus.DISPENSED.value,
        drug_name=item["drug-name"],
        drug_code=_validate_drug_code(item["drug-code"]),
        dose_instr=item["dose-instr"],
        dose_qty=_digits_only_int(item["dose-qty"], field="dose-qty"),
        dose_rpt=_digits_only_int(item["dose-rpt"], field="dose-rpt"),
        prescribed_date=_validate_date(
            item["prescribed-date"], field="prescribed-date"
        ),
        dispensed_date=_validate_date(item["dispensed-date"], field="dispensed-date"),
        paperless=_to_bool(item["paperless"]),
        brand_sub_not_prmt=_to_bool(item["brand-sub-not-prmt"]),
        remaining_repeats=remaining,
        dispensed_at_this_pharmacy=True,
    )


def ingest_pt_data_contract(
    pt_data: Dict[str, Any], session, commit=False, overwrite_patient=False
) -> IngestResult:
    patient_tmp = _build_patient(pt_data)
    existing = Patient.query.filter_by(medicare=patient_tmp.medicare).first()
    is_new = existing is None
    patient = patient_tmp if is_new else existing
    if not is_new and overwrite_patient:
        for field in [
            "pharmaceut_ben_entitlement_no",
            "sfty_net_entitlement_cardholder",
            "rpbs_ben_entitlement_cardholder",
            "name",
            "dob",
            "preferred_contact",
            "address_1",
            "address_2",
            "script_date",
            "pbs",
            "rpbs",
            "asl_status",
            "is_registered",
            "consent_last_updated",
        ]:
            setattr(patient, field, getattr(patient_tmp, field))
    if is_new:
        session.add(patient)
    prescribers, prescriptions = [], []
    created_prescribers = 0

    def prescriber_for(item):
        nonlocal created_prescribers
        pr = _get_or_create_prescriber(item["prescriber"])
        if pr not in prescribers:
            prescribers.append(pr)
            if pr.id is None:
                created_prescribers += 1
        return pr

    for item in pt_data.get("asl-data", []) or []:
        p = _build_prescription_from_asl(item, patient, prescriber_for(item))
        session.add(p)
        prescriptions.append(p)
    for item in pt_data.get("alr-data", []) or []:
        p = _build_prescription_from_alr(item, patient, prescriber_for(item))
        session.add(p)
        prescriptions.append(p)
    if commit:
        session.commit()
    else:
        session.flush()
    return IngestResult(
        patient,
        prescribers,
        prescriptions,
        created_prescribers,
        len(prescriptions),
        is_new,
    )
