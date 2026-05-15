from typing import Optional
from pydantic import BaseModel

class URLDetailRequest(BaseModel):
    normalized_url: str

class NavigationItem(BaseModel):
    key: str
    label: str
    enabled: bool
    route: str
    icon: Optional[str] = None