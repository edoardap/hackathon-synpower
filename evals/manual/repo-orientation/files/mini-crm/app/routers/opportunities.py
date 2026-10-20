from fastapi import APIRouter

router = APIRouter(prefix="/opportunities")


@router.get("")
def list_opportunities():
    return []
