import json
from pathlib import Path
from rich.pretty import pprint

from ai.anonymizer import clean_headers_cookies, CleanHeadersAndCookies

test_request_file = Path(__file__).parent.joinpath("test_request.json")
request_to_anonymize = json.loads(test_request_file.read_text())

clean_request: CleanHeadersAndCookies = clean_headers_cookies(request=request_to_anonymize.get("request", {}))

pprint(clean_request)
