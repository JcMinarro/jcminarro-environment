# AGENTS.md

This file provides context for LLMs and automated agents working with this repository.

## What This Is

A personal Ansible role (`jcminarro-environment`) that provisions development laptops. It supports **Linux (Ubuntu/Debian)** and **macOS** with automatic OS detection.

## Architecture

**Role-based Ansible structure** following standard conventions:

- `defaults/main.yml` - All variables (versions, feature toggles, package lists)
- `tasks/main.yml` - Entry point, routes to OS-specific task files
- `tasks/common.yml` - OS-agnostic tasks (git, ssh, sdkman, nodejs, opencode, android-cli)
- `tasks/linux.yml` / `tasks/linux/` - Linux-specific tasks
- `tasks/macos.yml` / `tasks/macos/` - macOS-specific tasks
- `handlers/main.yml` - Service restart handlers
- `provision.yml` - Top-level playbook that invokes the role

## Key Conventions

### OS Detection
Uses `ansible_os_family` for routing:
- `["Debian", "RedHat"]` → Linux tasks
- `"Darwin"` → macOS tasks

### Feature Toggles
Boolean variables in `defaults/main.yml` control what gets installed:
- `configure_git`, `configure_ssh`, `install_nodejs`, `install_sdkman`, `install_android_cli`, etc.

### Variable Naming
- Linux-specific vars: `system_packages`, `apt_repositories`, `docker_packages`, `appimages`, `snap_packages`
- macOS-specific vars: `brew_formulas`, `brew_casks`, `macos_system_tweaks`
- Common vars: `current_user`, `home_directory`, `common_directories`

### Privilege Escalation
- No play-level `become` — each task declares `become: true` individually when needed
- Only Linux tasks that write to system paths (`/opt`, `/usr/local/bin`, `/etc/apt`) use `become`
- macOS tasks should NOT use `become`

### Module Usage
- Use `ansible.builtin.*` FQCN for all built-in modules
- Use `community.general.*` for Galaxy collection modules (snap, homebrew, git_config, osx_defaults)
- Avoid deprecated modules (e.g., use `get_url` instead of `apt_key`)

### Task Files
- `import_tasks` for static includes (evaluated at parse time)
- `include_tasks` for dynamic includes (evaluated at runtime, e.g., with loops/conditionals)
- Use `tags` on every task block for selective execution

### Idempotency
- Use `creates` on shell/command tasks where possible
- Use `stat` + `when` guards for conditional installation
- Use `changed_when: false` for read-only commands

## Common Operations

### Adding a new Linux package
Add to `system_packages` list in `defaults/main.yml`.

### Adding a new macOS cask
Add to `brew_casks` list in `defaults/main.yml`.

### Adding a new Galaxy role
Add the `include_role` call directly in `tasks/linux/galaxy_roles.yml`.

### Adding a new feature
1. Add a feature toggle variable to `defaults/main.yml`
2. Create task file(s) under `tasks/`
3. Include from `tasks/common.yml`, `tasks/linux.yml`, or `tasks/macos.yml` with `when` guard

## Dependencies

### Galaxy Roles (Linux)
- `gantsign.sdkman` (v2.2.0) - SDKMAN installation
- `darkwizard242.googlechrome` (v3.1.0) - Chrome via apt
- `darkwizard242.vscode` (v1.5.0) - VS Code via apt
- `darkwizard242.onepassword` (v2.5.1) - 1Password via apt

### Collections
- `community.general` - snap, homebrew, homebrew_cask, git_config, osx_defaults

## Running

```bash
ansible-playbook -K provision.yml          # Full setup
ansible-playbook -K provision.yml --tags "development"  # Dev tools only
ansible-playbook -K provision.yml --list-tags           # List available tags
```

## Testing

No automated test framework currently. Test manually on target machines.
