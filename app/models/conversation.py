from pydantic import BaseModel


class ConversationContinueRequest(BaseModel):
    """Body for POST /api/ai/conversations/{conversation_id}"""
    user_input: str
    stream: bool = True
    debug: bool = False
