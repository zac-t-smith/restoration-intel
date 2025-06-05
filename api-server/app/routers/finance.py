from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..config import get_db_session
from ..services.unit_economics import calculate_job_contribution_margin
from ..services.working_capital import WorkingCapitalAnalyzer

router = APIRouter()

@router.get("/unit-economics")
async def get_unit_economics(db: Session = Depends(get_db_session)):
    try:
        metrics = calculate_job_contribution_margin()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/working-capital")
async def get_working_capital(db: Session = Depends(get_db_session)):
    try:
        analyzer = WorkingCapitalAnalyzer(db)
        metrics = analyzer.calculate_working_capital_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 