#!/usr/bin/env python3
"""
Credential helpers for API access
"""
import json
import os
import sys


def get_dataforseo_credentials() -> tuple:
    """Get DataForSEO login and password from environment"""
    login = os.environ.get("DATAFORSEO_LOGIN")
    password = os.environ.get("DATAFORSEO_PASSWORD")
    return login, password


def get_google_credentials(scopes: list):
    """Build Google credentials from GOOGLE_APPLICATION_CREDENTIALS.

    Auto-detects credential type from the JSON file:
    - Service account key ("type": "service_account") → direct API access
    - OAuth client secret ("installed" or "web" key) → user consent flow with token caching

    Returns a credentials object usable with Google API clients.
    """
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        print("error: GOOGLE_APPLICATION_CREDENTIALS not set", file=sys.stderr)
        print("Add to .env.seo: GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json", file=sys.stderr)
        print("Accepts either a service account key or an OAuth client secret.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(cred_path):
        print(f"error: credential file not found: {cred_path}", file=sys.stderr)
        sys.exit(1)

    with open(cred_path) as f:
        cred_data = json.load(f)

    # Service account key
    if cred_data.get("type") == "service_account":
        from google.oauth2 import service_account
        return service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)

    # OAuth client secret (installed app or web app)
    if "installed" in cred_data or "web" in cred_data:
        return _oauth_flow(cred_path, scopes)

    print(f"error: unrecognized credential format in {cred_path}", file=sys.stderr)
    print("Expected a service account key or OAuth client secret JSON.", file=sys.stderr)
    sys.exit(1)


def _oauth_flow(client_secret_path: str, scopes: list):
    """Run OAuth installed-app flow with token caching.

    Stores the token next to the client secret file as .seo-token.json
    so subsequent runs don't need browser auth.
    """
    token_path = os.path.join(
        os.path.dirname(client_secret_path) or ".",
        ".seo-token.json"
    )

    from google.oauth2.credentials import Credentials

    creds = None
    if os.path.isfile(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
    else:
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes)
        creds = flow.run_local_server(port=0)

    with open(token_path, "w") as f:
        f.write(creds.to_json())

    return creds


def get_gsc_site_url() -> str:
    """Get the GSC site URL from GSC_SITE_URL env var.

    Returns the site property string (e.g. 'https://example.com' or 'sc-domain:example.com').
    """
    site_url = os.environ.get("GSC_SITE_URL")
    if not site_url:
        print("error: GSC_SITE_URL not set", file=sys.stderr)
        print("Add to .env.seo: GSC_SITE_URL=https://example.com", file=sys.stderr)
        print("Use your exact Search Console property URL (URL-prefix or sc-domain:example.com).", file=sys.stderr)
        sys.exit(1)
    return site_url
