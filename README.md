# jcminarro-environment

Ansible role to manage my laptop setup. Works on both **Linux (Ubuntu/Debian)** and **macOS**.

Feel free to reference or re-use (at your own risk).

## Requirements

- Ansible 2.9 or higher
- Supported operating systems:
  - **Linux**: Ubuntu/Debian (tested on Ubuntu 22.04+)
  - **macOS**: Apple Silicon (M1/M2/M3) or Intel

## Installation

Run the playbook:

```bash
ansible-playbook -K provision.yml
```

The `-K` flag prompts for sudo password.

## What Gets Installed

The role automatically detects your OS and installs appropriate packages:

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
- Screenshot/recording tools

**Applications:**
- Sublime Text
- 1Password
- AppImages: Nextcloud, Obsidian, rquickshare
- Snap packages: Slack, Telegram, Zoom, Discord
- Anki (via tarball)

**Development:**
- Chrome & VSCode (via darkwizard242 roles)

### macOS Only (Apple Silicon)

**Homebrew Packages:**
- Homebrew itself (auto-installed)
- Formulas: All common CLI tools
- Casks: Chrome, VSCode, Docker Desktop, iTerm2
- GUI Apps: Slack, Telegram, Zoom, Discord, Obsidian, 1Password
- Multimedia: VLC, GIMP
- Development: Sublime Text, Anki
- Screenshot: flameshot replacement

**System Configuration:**
- macOS-specific tweaks (optional, via `apply_macos_tweaks: true`)

## Configuration

Variables are split by OS in `group_vars/`:

```
group_vars/
├── all.yml       # Common variables (versions, etc.)
├── linux.yml     # Linux-specific (packages, repos)
└── macos.yml     # macOS-specific (brew formulas, casks)
```

### Key Variables

```yaml
# In group_vars/all.yml
anki_version: "25.02.5"
nodejs_version: "24.14.0"

# In group_vars/linux.yml
system_packages:
  - vim
  - git
  - htop
  # ...

# In group_vars/macos.yml
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
# Install only development tools
ansible-playbook -K provision.yml --tags "development"

# Install only Anki
ansible-playbook -K provision.yml --tags "anki"

# Install only communication apps
ansible-playbook -K provision.yml --tags "communication"
```

### Run only for specific OS (though it auto-detects)
```bash
# This happens automatically, but you can skip tasks with --skip-tags
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

## Notes

### Shell Configuration

**Important:** This role does NOT manage your `.bashrc` or `.zshrc` files to avoid overwriting your manual changes. These files are managed manually by you.

If you want automated dotfiles management, consider creating a separate dotfiles repository.

### OpenCode

OpenCode is installed as a standalone binary:
- Location: `~/.opencode/bin/opencode`
- Added to PATH automatically via `.bashrc` or `.zshrc` (if managed manually)

### Node.js

Node.js is managed via `n` (version manager):
- Update to latest LTS: `n lts`
- Install specific version: `n <version>`
- List versions: `n ls`

### Docker

After installation, you need to **log out and log back in** for the docker group membership to take effect.

## Testing

Tested on:
- ✅ Ubuntu 22.04/24.04 (x86_64)
- ✅ macOS Sonoma/Sequoia (Apple Silicon M1/M2/M3)

## License

BSD

## Author

[Jc Miñarro](https://github.com/JcMinarro)

---

**Note:** This is a personal configuration role. Feel free to fork and adapt to your needs!