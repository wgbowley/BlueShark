# blueshark/__init__.py

import os
import logging
from pathlib import Path


def _setup_logging(path: Path = None) -> None:
    """
    Sets up logging configuration for the package.

    Args:
        path (pathlib.Path, optional): The log file location.
            Defaults to 'blueshark.log' in the current working directory.
    """

    # Use the provided path or a default path
    if path is None:
        path = Path(os.getcwd()) / "blueshark.log"

    # Only configure logging if no handlers are present
    if not logging.getLogger().handlers:
        logging.basicConfig(
            filename=path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='a'
        )

    logging.info("Logging has been configured at %s", path)


_setup_logging()
