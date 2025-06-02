# jcminarro-environment

Ansible role to manage my laptop setup. Feel free to reference or re-use (at your own risk).

## Requirements

This role requires Ansible 2.9 or higher and has been tested on Ubuntu.

The following roles are used:
- [gantsign.sdkman](https://galaxy.ansible.com/ui/standalone/roles/gantsign/sdkman/documentation/)
- [darkwizard242.googlechrome](https://galaxy.ansible.com/ui/standalone/roles/darkwizard242/googlechrome/)
- [darkwizard242.vscode](https://galaxy.ansible.com/ui/standalone/roles/darkwizard242/vscode/)

## Installation

Just run the playbook:
```bash
ansible-playbook -K provision.yml
```

The required roles will be installed automatically during the playbook execution.

## Role Variables

Default variables are defined in `defaults/main.yml`:

```yaml
# Anki
anki_version: "25.02"
```

You can override these variables by defining them in your playbook.

## Features

This role installs and configures:

### Development Tools
- Git
- SDKMAN (for Java development)
- Visual Studio Code (with darkwizard242.vscode)
- Sublime Text
- colordiff (Colored diff output)
- Node.js LTS & npm (managed with n version manager)
- Docker & Docker Compose

### System Utilities
- htop, btop
- vim
- zip/unzip
- nmap
- jq
- sshpass
- Flameshot (Screenshot tool)
- Obsidian

### Network Tools
- Tailscale
- iperf3
- nmap
- wireguard
- traceroute

### Applications
- Google Chrome
- Anki
- 1Password
- Nextcloud Desktop

### Communication
- Slack
- Telegram
- Zoom
- Discord

### Multimedia
- GIMP (GNU Image Manipulation Program)
- Peek
- VLC

## Usage Notes

### Node.js Management
Node.js is installed using `n` version manager. You can:
- Update to latest LTS: `n lts`
- Install specific version: `n <version>`
- List installed versions: `n ls`

### Docker
The installation:
- Installs Docker CE and Docker Compose
- Adds your user to the docker group (requires logout/login to take effect)
- Includes buildx and compose plugins

## Tags

You can use tags to run specific parts of the role:

```bash
# Install only Anki
ansible-playbook -K provision.yml --tags "anki"

# Install development tools
ansible-playbook -K provision.yml --tags "development"

# Install communication apps
ansible-playbook -K provision.yml --tags "communication"
```

Available tags:
- `anki`
- `development`
- `communication`
- `browsers`
- `system`
- `packages`
- `tarballs`
- `appimages`
- `snaps`

## Dependencies

Dependencies are managed through `requirements.yml`. Make sure to install them before running the playbook.

## License

BSD

## Author Information

[Jc Miñarro](https://github.com/JcMinarro)

