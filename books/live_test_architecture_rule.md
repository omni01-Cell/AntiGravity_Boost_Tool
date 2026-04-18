# Naming Convention Rule for Antigravity

All internal utility functions that are not part of the public API must be prefixed with an underscore `_`.
Example: `def _internal_helper():` instead of `def internal_helper():`.

This improves readability and distinguishes between internal logic and public interfaces.
