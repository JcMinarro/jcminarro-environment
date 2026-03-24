# jcminarro-environment

Ansible role to manage my laptop setup. Works on both **Linux (Ubuntu/Debian)** and **macOS**.

Feel free to reference or re-use (at your own risk).

## Requirements

- Ansible 2.9 or higher
- Supported operating systems:
  - **Linux**: Ubuntu/Debian (tested on Ubuntu 22.04+)
  - **macOS**: Apple Silicon (M1/M2/M3) or Intel

## Installation

```bash
ansible-playbook -K provision.yml
```

The `-K` flag prompts for sudo password (needed for Linux package installation).

## What Gets Installed

The role automatically detects your OS and installs appropriate packages.

### Common (Both Linux & macOS)

**Development Tools:**
- Git with custom configuration
- SDKMAN (Java/Kotlin/Gradle version manager)
- Node.js LTS (via `n` version manager) + npm + pnpm
- Docker & Docker Compose
- OpenCode (AI coding agent)
- OpenSpec (API specification tool)

**CLI Utilities:**
- vim, jq, htop, btop, colordiff, tree
- ssh tools, nmap, iperf3, mtr

### Linux Only (Ubuntu/Debian)

**System Packages:**
- APT repositories: Sublime Text, Tailscale, Docker
- System utilities: guake, wireguard, flameshot, peek, VLC, GIMP

**Applications:**
- Sublime Text, 1Password
- AppImages: Nextcloud, Obsidian, rquickshare
- Snap packages: Slack, Telegram, Zoom, Discord
- Anki (via tarball)

**Development:**
- Chrome & VSCode (via darkwizard242 Galaxy roles)

### macOS Only

**Homebrew Packages:**
- Homebrew itself (auto-installed)
- Formulas: All common CLI tools
- Casks: Chrome, VSCode, Docker Desktop, iTerm2
- GUI Apps: Slack, Telegram, Zoom, Discord, Obsidian, 1Password, Nextcloud
- Multimedia: VLC, GIMP, licecap
- Development: Sublime Text, Anki

**System Configuration:**
- macOS system tweaks (disabled by default, enable with `apply_macos_tweaks: true`)

## Configuration

All variables are defined in `defaults/main.yml` and can be overridden.

### Key Variables

```yaml
# Feature toggles
configure_git: true
configure_ssh: true
install_nodejs: true
install_sdkman: true
install_opencode: true
install_openspec: true
apply_macos_tweaks: false  # macOS system preferences

# Versions
anki_version: "25.02.5"
nodejs_version: "24.14.0"
sdkman_default_java_version: "21.0.2-tem"

# Git
git_user_name: "Jc Miñarro"
git_user_email: "josecarlos.minarro@gmail.com"

# System packages (Linux)
system_packages:
  - vim
  - git
  - htop
  # ...

# Homebrew (macOS)
brew_formulas:
  - git
  - vim
  - htop
  # ...

brew_casks:
  - google-chrome
  - visual-studio-code
  - docker
  # ...
```

## Usage Examples

### Run everything
```bash
ansible-playbook -K provision.yml
```

### Run only specific tags
```bash
ansible-playbook -K provision.yml --tags "development"
ansible-playbook -K provision.yml --tags "anki"
ansible-playbook -K provision.yml --tags "communication"
```

### Skip specific tags
```bash
ansible-playbook -K provision.yml --skip-tags "macos"
```

## Tags Available

- `anki` - Anki flashcards
- `opencode` - OpenCode AI agent
- `openspec` - OpenSpec tool
- `development` - SDKMAN, Node.js, Docker
- `communication` - Slack, Telegram, Zoom, Discord
- `browsers` - Chrome
- `system` - System utilities
- `packages` - APT/brew packages
- `appimages` - AppImage applications (Linux)
- `snaps` - Snap packages (Linux)
- `linux` - All Linux-specific tasks
- `macos` - All macOS-specific tasks

## Project Structure

```
jcminarro-environment/
├── defaults/
│   └── main.yml            # All default variables
├── tasks/
│   ├── main.yml            # Entry point (OS routing)
│   ├── common.yml          # OS-agnostic tasks
│   ├── git.yml, ssh.yml    # Configuration tasks
│   ├── sdkman.yml          # SDKMAN installation
│   ├── nodejs.yml          # Node.js via n
│   ├── opencode.yml        # OpenCode installation
│   ├── openspec.yml        # OpenSpec installation
│   ├── dotfiles.yml        # Dotfiles (placeholder)
│   ├── linux.yml           # Linux task dispatcher
│   ├── linux/              # Linux-specific tasks
│   ├── macos.yml           # macOS task dispatcher
│   └── macos/              # macOS-specific tasks
├── handlers/
│   └── main.yml            # Service restart handlers
├── templates/
│   └── appimage-wrapper.j2 # AppImage launcher script
├── requirements/
│   ├── common.yml          # Shared Galaxy roles
│   ├── linux.yml           # Linux Galaxy roles
│   └── macos.yml           # macOS Galaxy roles (empty)
├── provision.yml           # Main playbook
└── AGENTS.md               # LLM/agent context
```

## Notes

### Shell Configuration

This role does NOT manage `.bashrc` or `.zshrc` directly. It only adds specific PATH entries (for n, SDKMAN, OpenCode) using `blockinfile`. Your other shell customizations are preserved.

### Docker

After installation, log out and back in for docker group membership to take effect.

### macOS System Tweaks

Disabled by default. To enable Finder/Dock/keyboard tweaks:

```bash
ansible-playbook -K provision.yml --tags "macos,system" -e apply_macos_tweaks=true
```

## Testing

Tested on:
- Ubuntu 22.04/24.04 (x86_64)
- macOS Sonoma/Sequoia (Apple Silicon M1/M2/M3)

## License

BSD

## Author

[Jc Miñarro](https://github.com/JcMinarro)
