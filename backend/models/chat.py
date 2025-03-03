from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional,Dict, Any

# class ChatMessage(BaseModel):
#     id: Optional[str] = None
#     text: str
#     sender: str = "user"
#     timestamp: datetime = Field(default_factory=datetime.utcnow)
#     session_id: Optional[str] = None

class ChatMessage(BaseModel):
    id: Optional[str] = None
    text: str
    sender: str = "user"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    #response_type:str
    table_data: Optional[Dict] = None
    summary: Optional[str] = None
    next_question:List[str]=Field(default_factory=list)


class ChatResponse(BaseModel):
    id: str
    text: str
    sender: str = "bot"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str
    response_type:str
    table_data: Optional[Dict] = None
    summary: Optional[str] = None
    next_question:List[str]=Field(default_factory=list)
    df_parent: Optional[str] = None
    

class ChatSession(BaseModel):
    id: str
    title: str
    last_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    messages: List[ChatMessage] = []


class Dataset(BaseModel):
    records: List[Dict[str, Any]]  # Array of objects representing rows
    columns: List[str]  # Column names
    shape: Optional[dict] = Field(
        default=None, 
        description="Optional shape of the dataset",
        alias="shape"
    )


class ChatDataFrame(BaseModel):
    id: Optional[str] = None
    text: str
    sender: str = "bot"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None