from fastapi import FastAPI
from app.routers import opportunities

app = FastAPI(title="mini-crm")
app.include_router(opportunities.router)


@app.get("/health")
def health():
    return {"ok": True}
