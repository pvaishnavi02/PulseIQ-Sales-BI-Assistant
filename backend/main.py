
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.interpreter import interpret_question

app = FastAPI(
    title="Sales BI Assistant API",
    description=(
        "Answers business questions using validated analytics "
        "over sales data stored in SQLite."
    ),
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="A supported natural-language sales question",
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "Sales BI Assistant"}


@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question must not be empty.",
        )

    try:
        result = interpret_question(question)
        return {"success": True, **result}

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Log the actual error on the server, but don't expose
        # database details or stack traces to the client.
        print(f"Unexpected error while answering question: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process the question. Please try again.",
        ) from exc
