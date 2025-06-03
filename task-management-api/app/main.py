"""This file serves as the entry point for the Task Management API."""

import os
import sys
from pathlib import Path

import uvicorn


def main():
    """Main entry point for the Task Management API application."""

    file_path = Path(__file__).resolve()
    api_root = file_path.parent.parent
    os.chdir(api_root)
    sys.path.insert(0, str(api_root))
    uvicorn.run("app.api.api:app", reload=True)


if __name__ == "__main__":
    main()
