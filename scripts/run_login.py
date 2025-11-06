"""CLI entrypoint that performs the login flow using environment variables."""
from __future__ import annotations

import asyncio
from argparse import ArgumentParser

from dotenv import load_dotenv

from automation.login_flow import Selectors, login_from_env

DEFAULT_SELECTORS = Selectors()


async def main() -> None:
    parser = ArgumentParser(description="Run the automated login flow with Playwright")
    parser.add_argument(
        "--slow-mo",
        type=int,
        default=100,
        help="Delay (in ms) injected between Playwright operations to observe the UI",
    )
    parser.add_argument(
        "--username-selector",
        default=DEFAULT_SELECTORS.username,
        help="CSS selector for the username field",
    )
    parser.add_argument(
        "--password-selector",
        default=DEFAULT_SELECTORS.password,
        help="CSS selector for the password field",
    )
    parser.add_argument(
        "--submit-selector",
        default=DEFAULT_SELECTORS.submit,
        help="CSS selector for the primary submit/login button",
    )
    parser.add_argument(
        "--mfa-selector",
        default=DEFAULT_SELECTORS.mfa,
        help="CSS selector for the MFA/OTP input field",
    )
    parser.add_argument(
        "--mfa-submit-selector",
        default=DEFAULT_SELECTORS.mfa_submit,
        help="CSS selector for an optional MFA submit button",
    )

    args = parser.parse_args()

    load_dotenv()

    selectors = Selectors(
        username=args.username_selector,
        password=args.password_selector,
        submit=args.submit_selector,
        mfa=args.mfa_selector,
        mfa_submit=args.mfa_submit_selector,
    )

    await login_from_env(selectors=selectors, slow_mo=args.slow_mo)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
