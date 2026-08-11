# Agent Instructions

## Mandatory interface-change workflow

These instructions apply to the entire repository.

For any task that adds, changes, deletes, reviews, commits, pushes, or opens a pull request for
cross-domain interfaces, the agent must follow
[`docs/robot_interfaces_ai_change_playbook.md`](docs/robot_interfaces_ai_change_playbook.md).

Required behavior:

1. Read the playbook at the start of the task before deciding which files to modify.
2. Treat `contract/endpoints.yaml` and the IDL files as authoritative; generated contract views must
   be updated through the repository generator.
3. Before `git commit`, `git push`, or creating/updating a pull request, reopen the playbook and run
   its pre-submission review, validation, and definition-of-done checks against the current diff.
4. Do not claim an unrun check passed. Report each check as passed, failed, or not run with a reason.
5. Preserve unrelated user changes and do not use destructive Git commands to discard work.
6. In the final response, proactively state the immediate next operation and the remaining review,
   release, downstream-SHA-update, smoke-test, or deployment actions. Do not stop at “done.”
7. Do not perform push, PR creation, merge, tag, downstream repository changes, or deployment beyond
   the authority explicitly granted by the user.

Repository state and higher-priority user/system instructions override examples in the playbook. If
the live repository conflicts with an example, inspect the current files and report the discrepancy.
