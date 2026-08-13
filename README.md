# ansible-iac-shared-tasks

Shared task snippets for IDARSI Ansible roles.

This repository is intended to be consumed as a git submodule under a role's
`tasks/shared/` path. The snippets here must stay service-agnostic and rely
only on shared variables such as `iac_fs_directories`, `iac_fs_files`,
`iac_fs_binds`, `iac_git_repos`, and `iac_cron`.

## Filesystem records

### `iac_fs_files`

`iac_fs_files` supports these mutually exclusive payload sources:

- `content`: inline file content
- `src`: absolute source path

Optional:

- `remote_src`: valid only together with `src`; when `true`, `src` points to
  a path already present on the target host
- `owner`
- `group`
- `mode`
- `selinux.setype`

Examples:

Inline content:

```yaml
iac_fs_files:
  - path: /etc/example/inline.conf
    content: |
      key=value
    owner: root
    group: root
    mode: "0644"
```

Copying a file from the controller host:

```yaml
iac_fs_files:
  - path: /etc/example/copied.conf
    src: /srv/idarsi/payloads/example/copied.conf
    owner: root
    group: root
    mode: "0640"
```

Copying a file already present on the target host:

```yaml
iac_fs_files:
  - path: /etc/example/from-target.conf
    src: /var/tmp/from-target.conf
    remote_src: true
    owner: root
    group: root
    mode: "0600"
```

Managing a file with SELinux context:

```yaml
iac_fs_files:
  - path: /srv/data/example/index.html
    content: |
      hello
    owner: root
    group: root
    mode: "0644"
    selinux:
      setype: httpd_sys_content_t
```

### `iac_fs_directories`

`iac_fs_directories` manages directory state, ownership, mode, and optional
SELinux context only.

Supported optional fields:

- `state`
- `owner`
- `group`
- `mode`
- `selinux.setype`
- `selinux.recursive`

Examples:

Ensuring a directory exists:

```yaml
iac_fs_directories:
  - path: /srv/data/example
    owner: root
    group: root
    mode: "0755"
```

Managing a directory with SELinux context recursively:

```yaml
iac_fs_directories:
  - path: /srv/data/example
    owner: root
    group: root
    mode: "0755"
    selinux:
      setype: httpd_sys_content_t
      recursive: true
```

Managing only the directory's own SELinux label:

```yaml
iac_fs_directories:
  - path: /etc/example
    owner: root
    group: root
    mode: "0755"
    selinux:
      setype: etc_t
      recursive: false
```

Removing a directory and its optional custom SELinux fcontext rule:

```yaml
iac_fs_directories:
  - path: /srv/data/example
    selinux:
      setype: httpd_sys_content_t
      recursive: true
```

Recursive directory copy is intentionally not overloaded onto
`iac_fs_directories`.

### `iac_fs_binds`

`iac_fs_binds` manages directory bind mounts and optional one-time migration of
existing data from the old target path into the new source path.

Required fields:

- `source`
- `target`

Common optional fields:

- `owner`
- `group`
- `mode`
- `move_from_target`
- `purge_on_absent`

Behavior:

- `source` is the new real directory location
- `target` is the legacy path that remains available through a bind mount
- when `move_from_target: true`, existing content is moved from `target` to
  `source` only before the first mount and only when `source` is empty
- when both `source` and `target` already contain data before the first mount,
  the task fails instead of trying to merge them automatically
- the task fails fast if `target` is already mounted from a different source
- when `purge_on_absent: true`, the `absent` flow removes the contents of
  `source` after unmounting; when omitted or `false`, `absent` fails if
  `source` still contains files
- the bind mount is persisted into `/etc/fstab`

Example: migrating PostgreSQL data under `/srv/data` while keeping the legacy
path available:

```yaml
iac_fs_binds:
  - source: /srv/data/pgsql
    target: /var/lib/pgsql
    owner: postgres
    group: postgres
    mode: "0700"
    move_from_target: true
```

Example: removing a bind mount and purging the backing directory contents:

```yaml
iac_fs_binds:
  - source: /srv/data/app-cache
    target: /var/cache/myapp
    purge_on_absent: true
```

Example: ensuring a bind mount without migration:

```yaml
iac_fs_binds:
  - source: /srv/data/app-cache
    target: /var/cache/myapp
    owner: root
    group: root
    mode: "0755"
```

## Cron jobs

### `iac_cron`

`iac_cron` manages cron entries with `ansible.builtin.cron`.

Required fields for present state:

- `name`
- `job`
- `cron_file`

Common optional fields for present state:

- `state`
- `user`
- `special_time`
- `month`
- `day`
- `weekday`
- `hour`
- `minute`

Behavior:

- when `user` is omitted, the task defaults to `root`
- the current shared task implementation writes cron entries via `cron_file`
- the absent flow removes entries by `name` from the given `cron_file`
- `special_time` can be used for shortcuts such as `reboot`, `daily`, or
  `monthly` instead of explicit schedule fields

Example: ensuring a root-owned heartbeat cron job:

```yaml
iac_cron:
  - name: idarsi-heartbeat
    user: root
    minute: "*/5"
    hour: "*"
    weekday: "*"
    job: "/usr/local/bin/idarsi-heartbeat"
    cron_file: idarsi-heartbeat
```

Example: ensuring a service user's nightly cron job:

```yaml
iac_cron:
  - name: postgres-backup
    user: postgres
    minute: "15"
    hour: "2"
    weekday: "*"
    job: "/usr/local/bin/postgres-backup"
    cron_file: postgres-backup
```

Example: ensuring a monthly cleanup job on the first day of the month:

```yaml
iac_cron:
  - name: idarsi-monthly-cleanup
    user: root
    minute: "30"
    hour: "3"
    day: "1"
    month: "*"
    job: "/usr/local/bin/idarsi-monthly-cleanup"
    cron_file: idarsi-monthly-cleanup
```

Example: ensuring a job runs on reboot:

```yaml
iac_cron:
  - name: idarsi-startup-check
    user: root
    special_time: reboot
    job: "/usr/local/bin/idarsi-startup-check"
    cron_file: idarsi-startup-check
```

Example: ensuring a job runs daily via `special_time`:

```yaml
iac_cron:
  - name: idarsi-daily-report
    user: root
    special_time: daily
    job: "/usr/local/bin/idarsi-daily-report"
    cron_file: idarsi-daily-report
```

Example: removing a cron entry:

```yaml
iac_cron:
  - name: idarsi-heartbeat
    cron_file: idarsi-heartbeat
```

## Git repositories

### `iac_git_repos`

`iac_git_repos` manages Git working trees with `ansible.builtin.git`.

Required fields:

- `repo`
- `dest`

Common optional fields:

- `version`
- `update`
- `force`
- `recursive`
- `single_branch`
- `remote`
- `accept_hostkey`
- `key_file`
- `depth`
- `refspec`

Optional task-level variable:

- `iac_git_become_user`: run Git checkout as a specific user

Examples:

Cloning a repository with default branch:

```yaml
iac_git_repos:
  - repo: https://github.com/example/project.git
    dest: /srv/data/project
```

Cloning a specific branch:

```yaml
iac_git_repos:
  - repo: https://github.com/example/project.git
    dest: /srv/data/project
    version: main
    single_branch: true
```

Running checkout as a service user:

```yaml
iac_git_become_user: postgres
iac_git_repos:
  - repo: /srv/git/app-config
    dest: /var/lib/pgsql/git/app-config
```

## Task-report logging

### `log_write.yml`

`log_write.yml` appends one standardized operational line to the task report.

Required variables when `iac_ansible_report: true`:

- `iac_service_name`
- `iac_log_write`
- `iac_ansible_report_tasks_path`

Behavior:

- writes the line in format `<iso8601> <ssh_user> <service> <message>`
- uses `ansible_facts['ssh_user']` and falls back to controller `USER`
- clears `iac_log_write` after writing so later tasks do not reuse it
- does nothing when `iac_ansible_report` is omitted or `false`

Example:

```yaml
- name: "Writing log"
  ansible.builtin.include_tasks: shared/log_write.yml
  vars:
    iac_log_write: "Ensured service nginx is started"
```
