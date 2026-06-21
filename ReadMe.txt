Debate Champion
===============

Overview
--------
Debate Champion is a simple CLI application that runs a structured debate between two AI agents on a user-provided motion. The application:

- prompts the user for a debate motion
- runs multiple rounds of debate arguments
- saves the full debate session as a JSON file in `results/`
- sends an email containing only the serialized round transcripts

Requirements
------------
- Python 3.10+ (or compatible)
- dependencies listed in `requirements.txt`

Dependencies
------------
- `pydantic-ai` for data modeling
- `python-dotenv` for environment variable loading
- `wikipedia` for external knowledge retrieval
- `nest-asyncio` for async support in notebook or interactive environments

Environment Variables
---------------------
The application reads SMTP and mail configuration from environment variables. Create a `.env` file or export these variables in your shell.

Required variables:
- `SMTP_USER` - email address used to send messages
- `SMTP_PASS` - SMTP password or app password

Optional but recommended:
- `MAIL_RECEPIENT` - recipient email address for debate results

If `MAIL_RECEPIENT` is not set, email is not sent and a warning is logged.

Usage
-----
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create or update `.env` with SMTP credentials and recipient:
   ```
   SMTP_USER=youremail@example.com
   SMTP_PASS=your_smtp_password
   MAIL_RECEPIENT=recipient@example.com
   ```

3. Run the app:
   ```
   python app.py
   ```

4. Enter a motion when prompted. Leave the input blank and press Enter to quit.

Output
------
- Full debate session JSON is saved to `results/debate_<sanitized_motion>.json`
- The full session JSON is printed to the console
- A formatted transcript for only `rounds` is sent by email
- Logs are stored in `logs/`

Implementation Notes
--------------------
- `app.py` uses `DebateEngine` to create a `DebateSession` and run rounds
- `utils/json_to_text.py` formats only the round transcripts into human-readable text for email
- `utils/mail_service.py` sends the email via Gmail SMTP
- `results/` and `logs/` directories are created automatically if missing

Ignored Files
-------------
The repository includes a `.gitignore` that excludes:
- Python bytecode and virtual environments
- editor directories like `.vscode/` and `.idea/`
- `logs/`, `results/`, and `.env`
