from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.retrieval_service import retrieve_chunks
from app.services.generation_service import generate_answer
from app.core.limiter import limiter
from fastapi import Request
router = APIRouter(prefix="/query", tags=["query"])

class QueryRequest(BaseModel):
    question: str
    top_k: int = 8  # kitne chunks retrieve karein

@limiter.limit("10/minute") 
@router.post("/")
async def query_documents(
    request: Request,
    query_req: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not query_req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Step 1: Relevant chunks dhundo
    chunks = retrieve_chunks(
        query=query_req.question,
        tenant_id=str(current_user.tenant_id),
        db=db,
        top_k=query_req.top_k
    )

    # Step 2: Groq se answer generate karo
    result = generate_answer(
        query=query_req.question,
        chunks=chunks
    )

    return {
        "question": query_req.question,
        "answer": result["answer"],
        "citations": result["citations"],
        "chunks_retrieved": len(chunks),
        "top_chunks": [
            {
                "filename": c["filename"],
                "similarity_score": c["similarity_score"],
                "preview": c["content"][:150] + "..."
            }
            for c in chunks
        ]
    }