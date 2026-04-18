# Rule 0 : Mandatory Session Initialization

<mandate>
At the very beginning of EACH session (before reading code or making decisions), you MUST invoke the `AGboost_init` skill. This skill handles:
- Startup of the AGBoost pipeline (Watchdog).
- Synchronization of pending knowledge items (Cohomology).
- Initialization of the `.GCC` persistent context.
</mandate>

<consequence>
This rule is absolute and non-negotiable. Failure to initialize will lead to cognitive misalignment and loss of project context.
</consequence>
