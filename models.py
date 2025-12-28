from pydantic import BaseModel, Field, constr, validator
from typing import Optional
from datetime import datetime
import re

E164 = re.compile(r"^\+\d+$")

class WebhookMessage(BaseModel):
    message_id: constr(min_length=1)
    from_msisdn: str = Field(..., alias="from")
    to_msisdn: str = Field(..., alias="to")
    ts: str
    text: Optional[constr(max_length=4096)] = None

    @validator("from_msisdn", "to_msisdn")
    def e164(cls, v):
        if not E164.match(v):
            raise ValueError("invalid E164")
        return v

    @validator("ts")
    def iso_utc(cls, v):
        if not v.endswith("Z"):
            raise ValueError("must end with Z")
        datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v
