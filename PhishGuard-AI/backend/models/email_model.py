from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EmailModel(BaseModel):
    id: Optional[str] = None
    thread_id: Optional[str] = None
    sender: str = ""
    reply_to: str = ""
    recipient: str = ""
    subject: str = ""
    date: str = ""
    return_path: str = ""
    authentication_results: str = ""
    received_spf: str = ""
    dkim_signature: str = ""
    arc_authentication_results: str = ""
    snippet: str = ""
    body: str = ""
    urls: List[str] = Field(default_factory=list)
    links: List[Dict[str, Any]] = Field(default_factory=list)
