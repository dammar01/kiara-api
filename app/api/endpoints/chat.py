from fastapi import APIRouter, Depends
from app.core.settings import settings
from app.schemas.chat_schemas import Ask
from app.models.chat import Chat
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from datetime import datetime

router = APIRouter()


async def save_chat(db: AsyncSession, questions: str, answers: str):
    dates = datetime.now()
    data = Chat(
        date=dates,
        questions=questions,
        answers=answers,
    )
    db.add(data)
    await db.commit()
    await db.refresh(data)


@router.post("/ask")
async def ask(data: Ask, db: AsyncSession = Depends(get_db("kiara"))):
    model = settings.model_loader
    response = model.predict(data.message)
    await save_chat(db, data.message, response)
    return {
        "code": 200,
        "message": response,
        "data": [],
        "error": False,
    }
