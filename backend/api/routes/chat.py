from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from backend.models.chat import ChatMessage, ChatResponse, ChatSession
from backend.services.generate_plan_summary import generate_plan_summary
from backend.services.chat import ChatService
from backend.core.security import get_current_user
# from backend.services.auth import get_current_user
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.services.prompt_next_question import PromptQuestion 
import logging

router = APIRouter()
chat_service = ChatService()

class AskDFRequest(BaseModel):
    question: str

class SimilarQuestionRequest(BaseModel):
    question: str
    persona: str

class ModuleFiles(BaseModel):
    module: str
    filename: List[str] 

from fastapi import APIRouter, Depends

# @router.get("/persona")
# async def some_endpoint(persona: str = Depends(get_current_persona)):
#     # You now have the dynamic persona string
#     return {"message": f"Your persona is {persona}"}

# @router.get("/planSummary")
# async def module_summary(module:str):
#     return await generate_plan_summary(module)
# @router.get("/planSummary")
# async def module_summary(module: str):
#     return await generate_plan_summary(module)

@router.post("/planSummary")
async def module_summary(module_files: ModuleFiles):
    return await generate_plan_summary(module_files.model_dump()) 

# @router.post("/sessions", response_model=ChatSession)
# async def create_session(current_user: dict = Depends(get_current_user)):
#     return await chat_service.create_session(str(current_user["_id"]))


@router.post("/sessions", response_model=ChatSession)
async def create_session(current_user: dict = Depends(get_current_user)):
    # Instead of just passing user_id, pass the entire current_user
    return await chat_service.create_session(current_user)


@router.get("/sessions", response_model=List[ChatSession])
async def get_sessions(current_user: dict = Depends(get_current_user)):
    return await chat_service.get_user_sessions(str(current_user["_id"]))

@router.post("/{session_id}/send", response_model=ChatResponse)
async def send_message(
    session_id: str,
    message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    return await chat_service.process_message(message.text, session_id, current_user)

@router.get("/{session_id}/messages", response_model=List[ChatMessage])
async def get_session_messages(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await chat_service.get_session_messages(session_id, str(current_user["_id"]))


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes a chat session and its associated messages.
    """
    try:
        # Use the chat service to delete the session
        await chat_service.delete_session(session_id, str(current_user["_id"]))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )
    












@router.post("/{session_id}/ask_on_df/{message_id}", response_model=ChatResponse)
async def ask_on_df(
    session_id: str,
    message_id: str,
    req: AskDFRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Handles the Ask-on-DF functionality. Fetches the DataFrame from the specified
    message in the session and processes the user's query.
    """
    try:
        # Delegate to ChatService to handle the logic
        response = await chat_service.ask_on_df(
            df_question=req.question,
            session_id=session_id,
            user_id=str(current_user["_id"]),
            parent_message_id=message_id
        )
        return response

    except HTTPException as e:
        # Handle expected errors (e.g., session or message not found)
        raise e
    except Exception as e:
        # Log unexpected errors
        logging.error(f"Failed to process Ask-on-DF: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your Ask-on-DF request."
        )