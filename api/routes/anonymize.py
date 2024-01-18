from typing import Dict, Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from api.routes.endpoints import endpoints
from ai.anonymizer import clean_headers_cookies, CleanHeadersAndCookies

######################################################
## Router for the AI Anonymizer
######################################################

anonymize_router = APIRouter(prefix=endpoints.ANONYMIZE, tags=["Anonymize"])


class AnonymizeRequest(BaseModel):
    request: Dict[str, Any]
    filter_values_over_length: int = 3000
    run_id: Optional[str] = None
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    debug_mode: bool = False


@anonymize_router.post("/request", response_model=CleanHeadersAndCookies)
def anonymize_request(body: AnonymizeRequest):
    """Anonymizes headers and cookies from a request
    and returns the clean headers and cookies
    """

    return clean_headers_cookies(
        request=body.request,
        filter_values_over_length=body.filter_values_over_length,
        run_id=body.run_id,
        user_id=body.user_id,
        team_id=body.team_id,
        debug_mode=body.debug_mode,
    )
