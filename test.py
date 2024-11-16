import re
import httpx
import json


def extract_apollo_state(html):
    """Extract apollo graphql state data from HTML source"""
    data = re.findall('apolloState":\s*({.+})};', html)[0]
    return json.loads(data)


def scrape_overview(company_name: str, company_id: int) -> dict:
    url = f"https://www.glassdoor.com/Overview/Worksgr-at-{company_name}-EI_IE{company_id}.htm"
    response = httpx.get(url, cookies={"tldp": "1"}, follow_redirects=True) 
    apollo_state = extract_apollo_state(response.text)
    return next(v for k, v in apollo_state.items() if k.startswith("Employer:"))



print(json.dumps(scrape_overview("eBay","7853"), indent=2))
