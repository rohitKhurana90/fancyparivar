"""Utilities for logging into the target application with Playwright.

The selectors used below are intended as sensible defaults. Update them to
match the actual DOM of the page you are automating. See the module level
README for guidance on discovering selectors.
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Optional

from playwright.async_api import Page, async_playwright


@dataclass
class Credentials:
    """Credentials and configuration required for the login flow."""

    login_url: str
    username: str
    password: str
    mfa_code: Optional[str] = None


@dataclass
class Selectors:
    """CSS selectors for all of the controls touched during login."""

    username: str = "input[name='username']"
    password: str = "input[name='password']"
    submit: str = "button[type='submit']"
    mfa: str = "input[name='otp']"
    mfa_submit: Optional[str] = None


async def _fill_login_form(page: Page, selectors: Selectors, creds: Credentials) -> None:
    await page.fill(selectors.username, creds.username)
    await page.fill(selectors.password, creds.password)
    await page.click(selectors.submit)


async def _handle_mfa(page: Page, selectors: Selectors, creds: Credentials) -> None:
    if creds.mfa_code is None:
        return

    await page.wait_for_selector(selectors.mfa)
    await page.fill(selectors.mfa, creds.mfa_code)

    if selectors.mfa_submit:
        await page.click(selectors.mfa_submit)
    else:
        # Retry submitting the original form when there is no dedicated MFA button.
        await page.click(selectors.submit)


async def login(creds: Credentials, selectors: Selectors = Selectors(), *, slow_mo: int = 0) -> None:
    """Launch a Chromium browser, perform login, and keep the page open."""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=slow_mo)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(creds.login_url)
        await _fill_login_form(page, selectors, creds)
        await _handle_mfa(page, selectors, creds)

        # Wait for the page to finish loading and give the operator time to observe.
        await page.wait_for_load_state("networkidle")
        print("Login completed. The browser will remain open until you close it manually.")

        # Block forever until the user interrupts the program.
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            await context.close()
            await browser.close()


def credentials_from_env() -> Credentials:
    """Create :class:`Credentials` from the process environment."""

    missing = [name for name in ("LOGIN_URL", "LOGIN_USERNAME", "LOGIN_PASSWORD") if name not in os.environ]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    return Credentials(
        login_url=os.environ["LOGIN_URL"],
        username=os.environ["LOGIN_USERNAME"],
        password=os.environ["LOGIN_PASSWORD"],
        mfa_code=os.getenv("LOGIN_MFA_CODE"),
    )


async def login_from_env(selectors: Selectors = Selectors(), *, slow_mo: int = 100) -> None:
    """Convenience wrapper that reads credentials from environment variables."""

    creds = credentials_from_env()
    await login(creds, selectors, slow_mo=slow_mo)


if __name__ == "__main__":
    asyncio.run(login_from_env())
