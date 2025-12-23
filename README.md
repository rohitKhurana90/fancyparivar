# fancyparivar

A Playwright project for automating login, multifactor authentication, browsing
after login, and interacting with the target DOM that is downloaded through an
API call.

## Getting started

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. Install dependencies and the Playwright browsers:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```
3. Copy `.env.example` to `.env` and update the values with your credentials and
   target URL. The script reads `LOGIN_URL`, `LOGIN_USERNAME`, `LOGIN_PASSWORD`,
   and (optionally) `LOGIN_MFA_CODE` from the environment. Keep secrets out of
   version control by ignoring the `.env` file.
4. Run the automated login flow:
   ```bash
   python -m scripts.run_login --slow-mo 250 \
       --username-selector "input[name='email']" \
       --password-selector "input[name='pass']" \
       --submit-selector "button#login"
   ```
   Override the selectors to match the fields in your application. During the
   run the browser stays open until you close the window or press `Ctrl+C` in
   the terminal.

## Customising the flow

- Update `automation/login_flow.py` if your MFA form needs special handling,
  additional waits, or if you want to capture traces/screenshots.
- Use `slow_mo` to slow down the automation while developing new steps.
- Import `automation.login_flow.login` in your own scripts to embed the login
  behaviour inside larger end-to-end scenarios.

## MFA strategies

If the second factor is delivered outside of the app (email/SMS), integrate the
retrieval inside `_handle_mfa`. For example, fetch the OTP from an API or
mailbox and pass it to `Credentials`. For TOTP-based flows, compute the token on
the fly and assign it to `mfa_code` before calling `login`.

## Troubleshooting

- **Browser closes immediately**: The new script waits forever after login until
  you close the browser manually or interrupt execution, so you can inspect the
  page.
- **Selector timeouts**: Double-check CSS selectors with the browser dev tools
  (`Inspect Element`) or `page.locator(<selector>).highlight()` when debugging.
- **Missing dependencies**: Ensure the virtual environment is active before
  installing packages or running the script.

