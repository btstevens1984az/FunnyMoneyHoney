import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SimulationRun
from app.schemas import SimulateRequest, SimulateResponse
from app.services.simulator import run_simulation

router = APIRouter(prefix="/api", tags=["simulate"])


@router.post("/simulate", response_model=SimulateResponse)
def simulate(body: SimulateRequest, db: Session = Depends(get_db)) -> SimulateResponse:
    result = run_simulation(body)
    db.add(
        SimulationRun(
            daily_stake=body.daily_stake,
            days=body.days,
            selections_json=json.dumps([s.model_dump() for s in (body.selections or [])]),
            result_json=result.model_dump_json(),
        )
    )
    db.commit()
    return result
