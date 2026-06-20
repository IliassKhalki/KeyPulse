# Maintenance Checklist

Use this checklist for small KeyPulse maintenance updates:

1. Confirm the working tree is clean before editing.
2. Keep changes focused on the native Windows desktop application.
3. Run `python -m compileall src tests` after Python changes.
4. Review the staged diff for secrets, generated files, and unrelated edits.
5. Use a descriptive commit message and push only verified changes.

Do not create empty commits solely to simulate project activity.
