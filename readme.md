
# BeatrizProspectorFormFill

Automates data extraction and form-filling workflows used by the LNC Prospector project.

## Contents

- `lnc_bot.py`: main bot entrypoint that orchestrates browser automation.
- `excel_handler.py`: helpers to read and validate Excel input.
- `multi_lang.py`: localization utilities and resources in `Resources/`.

## Prerequisites

- Python 3.10 or newer
- Google Chrome

## Quick setup

1. Create and activate a virtual environment:

    ```bash
    python -m venv .venv
    .venv/Scripts/activate
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure `lnc_bot.ini` directives, that points authentication params, prospector report and prospector documents folder

## Configuration

- GOOGLE_CHROME: is optional and must be set manually on unusual chrome path installation
- WEBSITE: is required and must be set with specific URL to SharePoint to be automated
- USUARIO: is required and must be set with username credential to authentication.
- PALAVRA: is required and must be set with password credential to authentication.
- EVIDENCIAS: is required and must to be set with client documents to be send folder path.
- PLANILHA: is required and must be set to absolute path to prospector report worksheet.

## Run

From the repository root with activated virtual environment:

```bash
cd src
python.exe lnc_bot.py
```

## Notes

- Place input Excel files under `data/` or adjust the path used by `excel_handler.py`.
- Logs and temporary browser profiles are stored under `src/tmp/` during runs; you can clear that directory between sessions.
