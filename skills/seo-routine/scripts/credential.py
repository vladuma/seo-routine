#!/usr/bin/env python3
"""
Credential helpers for API access
"""
import os
import sys


def get_dataforseo_credentials() -> tuple:
    """Get DataForSEO login and password from environment"""
    login = os.environ.get("DATAFORSEO_LOGIN")
    password = os.environ.get("DATAFORSEO_PASSWORD")
    return login, password


def get_google_credentials(scopes: list):
    """Build Google service account credentials from GOOGLE_APPLICATION_CREDENTIALS.

    Returns a google.oauth2.service_account.Credentials object.
    Exits with setup instructions if the env var is missing or the file is unreadable.
    """
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        print("error: GOOGLE_APPLICATION_CREDENTIALS not set", file=sys.stderr)
        print("Add to .env.seo: GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json", file=sys.stderr)
        print("The service account needs Search Console and/or Analytics read access.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(cred_path):
        print(f"error: credential file not found: {cred_path}", file=sys.stderr)
        sys.exit(1)

    from google.oauth2 import service_account
    return service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)


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
