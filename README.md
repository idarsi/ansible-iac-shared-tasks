# ansible-iac-shared-tasks

Shared task snippets for IDARSI Ansible roles.

This repository is intended to be consumed as a git submodule under a role's
`tasks/shared/` path. The snippets here must stay service-agnostic and rely
only on shared variables such as `iac_fs_directories`, `iac_fs_files`, and
`iac_cron`.
