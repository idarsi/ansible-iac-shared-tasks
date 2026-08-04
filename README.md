# ansible-iac-shared-tasks

Shared task snippets for IDARSI Ansible roles.

This repository is intended to be consumed as a git submodule under a role's
`tasks/shared/` path. The snippets here must stay service-agnostic and rely
only on shared variables such as `iac_fs_directories`, `iac_fs_files`,
`iac_git_repos`, and `iac_cron`.

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
