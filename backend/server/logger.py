
# backend/server/logger.py

import logging

# ---------------------------------------------------
# LOGGER CONFIG
# ---------------------------------------------------
log = logging.getLogger("suraj-ai-chat")
log.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

console = logging.StreamHandler()
console.setFormatter(formatter)

if not log.handlers:
    log.addHandler(console)
