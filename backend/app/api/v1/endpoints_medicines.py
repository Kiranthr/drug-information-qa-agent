"""
Medicines catalog endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.sql_models import Medicine
from app.models.schemas import MedicineResponse, MedicineCreate

router = APIRouter(prefix="/medicines", tags=["Medicines"])


@router.get("", response_model=List[MedicineResponse])
def list_medicines(db: Session = Depends(get_db)):
    """
    List all registered medicines with their ingested document counts.
    """
    medicines = db.query(Medicine).order_by(Medicine.generic_name).all()
    results = []
    for med in medicines:
        res = MedicineResponse.model_validate(med)
        res.document_count = len(med.documents)
        results.append(res)
    return results


@router.get("/{medicine_id}", response_model=MedicineResponse)
def get_medicine(medicine_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific medicine by its slug/ID.
    """
    med = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not med:
        raise HTTPException(status_code=404, detail=f"Medicine '{medicine_id}' not found")
    res = MedicineResponse.model_validate(med)
    res.document_count = len(med.documents)
    return res


@router.post("", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(payload: MedicineCreate, db: Session = Depends(get_db)):
    """
    Register a new medicine into the catalog.
    """
    existing = db.query(Medicine).filter(Medicine.id == payload.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Medicine with ID '{payload.id}' already exists")

    new_med = Medicine(
        id=payload.id.lower().strip(),
        generic_name=payload.generic_name.strip(),
        brand_names=payload.brand_names,
        drug_class=payload.drug_class,
        description=payload.description
    )
    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    res = MedicineResponse.model_validate(new_med)
    res.document_count = 0
    return res
