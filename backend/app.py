from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from .retriever import get_answer, get_audit_logs, flag_audit_entry
except ImportError:
    from retriever import get_answer, get_audit_logs, flag_audit_entry

app = FastAPI(title="SparkAI – AS/NZS 3000 Assistant")

class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask(query: Query):
    result = get_answer(query.question)
    if isinstance(result, dict):
        return result
    return {"answer": result, "confidence": None}

@app.get("/admin/logs")
async def list_logs(limit: int = 50):
    return {"logs": get_audit_logs(limit)}

@app.post("/admin/logs/{log_id}/flag")
async def flag_log(log_id: str, flagged: bool = True):
    try:
        entry = flag_audit_entry(log_id, flagged)
        return entry
    except KeyError:
        raise HTTPException(status_code=404, detail="Log entry not found")
