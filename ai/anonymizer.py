import json
from typing import Optional, Dict, Any, List
from rich.pretty import pretty_repr

from pydantic import BaseModel, Field
from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
from phi.storage.assistant.postgres import PgAssistantStorage  # noqa: F401

from ai.settings import ai_settings
from utils.log import logger


class SensitiveHeadersAndCookies(BaseModel):
    headers: List[str] = Field(
        ...,
        description="A list of header names from the original request that contain sensitive information and should be removed",
    )
    cookies: List[str] = Field(
        ...,
        description="A list of cookie names from the original request that contain sensitive information and should be removed",
    )


def get_sensitive_headers_cookies(
    request: Dict[str, Any],
    run_id: Optional[str] = None,
    user_id: Optional[str] = None,
    team_id: Optional[str] = None,
    debug_mode: bool = False,
) -> SensitiveHeadersAndCookies:
    """Sniff sensitive information from requests"""

    sniff_sensitive_info = Assistant(
        name="sniff_sensitive_info",
        run_id=run_id,
        user_id=user_id,
        llm=OpenAIChat(
            model=ai_settings.gpt_4,
            max_tokens=ai_settings.default_max_tokens,
            temperature=ai_settings.default_temperature,
        ),
        output_model=SensitiveHeadersAndCookies,
        debug_mode=debug_mode,
        # monitoring=True,
        # tool_calls=True,
        # show_tool_calls=True,
        # storage=PgAssistantStorage(
        #     schema="ai",
        #     db_url=db_url,
        #     table_name="sniff_sensitive_info",
        # ),
        description="You are a security expert designed to detect sensitive information in HTTP requests.",
        instructions=[
            "You will be provided with a request and you need to identify the headers and cookies that contain sensitive information.",
            "Each header or cookie that contains sensitive information should be returned so it can be anonymized.",
            "Each header contains a name and a value. The name is the name of the header and the value is the value of the header.",
            "Each cookie contains a name and a value. The name is the name of the cookie and the value is the value of the cookie.",
            "If the header or cookie contains sensitive information like passwords, tokens, or other secrets, then it should be returned.",
            "Make sure to return the headers in the headers list and the cookies in the cookies list.",
        ],
        user_data={"team_id": team_id},
    )

    return sniff_sensitive_info.run(json.dumps(request))  # type: ignore


class CleanHeadersAndCookies(BaseModel):
    headers: List[Dict[str, str]] = Field(
        ...,
        description="A list of headers from the original request with sensitive information replaced with anonymized values matching the original format and length",
    )
    cookies: List[Dict[str, str]] = Field(
        ...,
        description="A list of cookies from the original request with sensitive information replaced with anonymized values matching the original format and length",
    )


def clean_sensitive_headers_cookies(
    request: Dict[str, Any],
    run_id: Optional[str] = None,
    user_id: Optional[str] = None,
    team_id: Optional[str] = None,
    debug_mode: bool = False,
) -> CleanHeadersAndCookies:
    """Clean sensitive information from requests"""

    clean_sensitive_info = Assistant(
        name="clean_sensitive_info",
        run_id=run_id,
        user_id=user_id,
        llm=OpenAIChat(
            model=ai_settings.gpt_4,
            max_tokens=ai_settings.default_max_tokens,
            temperature=ai_settings.default_temperature,
        ),
        output_model=CleanHeadersAndCookies,
        debug_mode=debug_mode,
        # monitoring=True,
        # tool_calls=True,
        # show_tool_calls=True,
        # storage=PgAssistantStorage(
        #     schema="ai",
        #     db_url=db_url,
        #     table_name="sniff_sensitive_info",
        # ),
        description="You are a security expert designed to clean sensitive information in HTTP requests.",
        instructions=[
            "You will be provided with a request and you need to replace the values of headers and cookies",
            "Each header or cookie contains sensitive information and should be replaced with an anonymized value of similar lenth and format.",
            "Each header contains a name and a value. Replace only the value.",
            "Each cookie contains a name and a value. Replace only the value.",
            "Make sure the anonymized value is the same length and format as the original value.",
        ],
        user_data={"team_id": team_id},
    )

    return clean_sensitive_info.run(json.dumps(request))  # type: ignore


def clean_headers_cookies(
    request: Dict[str, Any],
    filter_values_over_length: int = 500,
    run_id: Optional[str] = None,
    user_id: Optional[str] = None,
    team_id: Optional[str] = None,
    debug_mode: bool = False,
) -> CleanHeadersAndCookies:
    logger.info("**************** Anonymizing Request ****************")
    # logger.info(f"Request: {request}")

    headers_to_anonymize = []
    headers = request.get("headers", [])
    if len(headers) > 0:
        for header in headers:
            header_name = header.get("name", "")
            header_value = header.get("value", "")

            if len(header_value) < filter_values_over_length:
                headers_to_anonymize.append({"name": header_name, "value": header_value})

    cookies_to_anonymize = []
    cookies = request.get("cookies", [])
    if len(cookies) > 0:
        for cookie in cookies:
            cookie_name = cookie.get("name", "")
            cookie_value = cookie.get("value", "")

            if len(cookie_value) < filter_values_over_length:
                cookies_to_anonymize.append({"name": cookie_name, "value": cookie_value})

    # Build request to anonymize
    request_to_anonymize = {}
    request_to_anonymize["headers"] = headers_to_anonymize
    request_to_anonymize["cookies"] = cookies_to_anonymize
    # logger.info(f"Request to Anonymize: {request_to_anonymize}")

    # Get sensitive info to anonymize
    sensitive_info: SensitiveHeadersAndCookies = get_sensitive_headers_cookies(
        request=request_to_anonymize, run_id=run_id, user_id=user_id, team_id=team_id, debug_mode=debug_mode
    )
    logger.info(f"Sensitive Info: {sensitive_info}")

    headers_to_clean = []
    for header_name in sensitive_info.headers:
        _header_value = None
        for header in headers_to_anonymize:
            if header.get("name", "") == header_name:
                _header_value = header
                break
        if _header_value is not None:
            headers_to_clean.append(_header_value)

    cookies_to_clean = []
    for cookie_name in sensitive_info.cookies:
        _cookie_value = None
        for cookie in cookies_to_anonymize:
            if cookie.get("name", "") == cookie_name:
                _cookie_value = cookie
                break
        if _cookie_value is not None:
            cookies_to_clean.append(_cookie_value)

    request_to_clean = {}
    request_to_clean["headers"] = headers_to_clean
    request_to_clean["cookies"] = cookies_to_clean

    clean_request: CleanHeadersAndCookies = clean_sensitive_headers_cookies(
        request=request_to_clean, run_id=run_id, user_id=user_id, team_id=team_id, debug_mode=debug_mode
    )
    logger.info(f"Clean Request: {pretty_repr(clean_request)}")

    return clean_request
