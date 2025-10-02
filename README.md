# Discord.py Masterclass

[![Code formatter and linter](https://github.com/FallenDeity/discord.py-masterclass/actions/workflows/format-and-lint.yml/badge.svg)](https://github.com/FallenDeity/discord.py-masterclass/actions/workflows/format-and-lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![discord.py](https://img.shields.io/badge/discord.py-master-blue.svg)](https://github.com/Rapptz/discord.py)

A comprehensive guide and example collection for building Discord bots with discord.py. This repository serves as a masterclass for both beginners and experienced developers looking to create feature-rich Discord bots.

## Documentation

Visit our [comprehensive documentation](https://fallendeity.github.io/discord.py-masterclass/) to learn about:

- Creating your first Discord bot
- Understanding slash commands and hybrid commands
- Working with views, buttons, and interactive components
- Implementing cogs for better code organization
- Creating custom converters and checks
- Building pagination systems
- Error handling best practices
- Audio playback functionality
- Custom help commands
- And much more! ✨

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Git
- A Discord account and a bot token ([Get one here](https://discord.com/developers/applications))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/FallenDeity/discord.py-masterclass.git
   cd discord.py-masterclass
   ```

2. **Install Poetry** (if you don't have it)
   ```bash
   pip install poetry
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

4. **Windows users only**: Extra step for Cairo (required for documentation), use if cairo is giving you issues
   ```bash
   pipwin install cairocffi
   ```

5. **Set up your bot token**

   Create a `.env` file in the root directory:
   ```env
   TOKEN=your_bot_token_here
   ```

6. **Run an example**
   ```bash
   poetry run python examples/creating-a-bot/main.py
   ```

## Contributing

We love contributions! Whether you're fixing a bug, adding a new example, improving documentation, or suggesting new features, your help is appreciated.

Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started. We welcome contributions of all kinds:

- Bug fixes
- New features and examples
- Documentation improvements
- Feature suggestions

## Development

### Running the Documentation Locally

```bash
poetry run mkdocs serve
```

Visit `http://127.0.0.1:8000/discord.py-masterclass/` to view the documentation.

### Code Quality

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Fast Python linter

Run all checks:
```bash
poetry run black .
poetry run isort .
poetry run ruff check .
```

or use the pre-commit hooks:
```bash
poetry run pre-commit run --all-files
```

## Contributors

We appreciate all contributions from the community! A big thank you to everyone who has contributed to this project.

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://triyan.dev/"><img src="https://avatars.githubusercontent.com/u/61227305?v=4?s=100" width="100px;" alt="Triyan Mukherjee"/><br /><sub><b>Triyan Mukherjee</b></sub></a><br /><a href="https://github.com/FallenDeity/discord.py-masterclass/commits?author=FallenDeity" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/aVitness"><img src="https://avatars.githubusercontent.com/u/64283289?v=4?s=100" width="100px;" alt="Vitness"/><br /><sub><b>Vitness</b></sub></a><br /><a href="https://github.com/FallenDeity/discord.py-masterclass/commits?author=aVitness" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/DownDev"><img src="https://avatars.githubusercontent.com/u/52790953?v=4?s=100" width="100px;" alt="Mikołaj Kruczek"/><br /><sub><b>Mikołaj Kruczek</b></sub></a><br /><a href="https://github.com/FallenDeity/discord.py-masterclass/commits?author=DownDev" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://blog.thegamecracks.xyz/"><img src="https://avatars.githubusercontent.com/u/61257169?v=4?s=100" width="100px;" alt="thegamecracks"/><br /><sub><b>thegamecracks</b></sub></a><br /><a href="https://github.com/FallenDeity/discord.py-masterclass/commits?author=thegamecracks" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/enriquebos"><img src="https://avatars.githubusercontent.com/u/54767698?v=4?s=100" width="100px;" alt="Enrique Bos"/><br /><sub><b>Enrique Bos</b></sub></a><br /><a href="https://github.com/FallenDeity/discord.py-masterclass/commits?author=enriquebos" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Snipy7374"><img src="https://avatars.githubusercontent.com/u/100313469?v=4?s=100" width="100px;" alt="Snipy7374"/><br /><sub><b>Snipy7374</b></sub></a><br /><a href="https://github.com/FallenDeity/discord.py-masterclass/commits?author=Snipy7374" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://externref.duckdns.org/"><img src="https://avatars.githubusercontent.com/u/70657005?v=4?s=100" width="100px;" alt="sarthak"/><br /><sub><b>sarthak</b></sub></a><br /><a href="https://github.com/FallenDeity/discord.py-masterclass/commits?author=externref" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://krypton.ninja/"><img src="https://avatars.githubusercontent.com/u/43011723?v=4?s=100" width="100px;" alt="Krypton"/><br /><sub><b>Krypton</b></sub></a><br /><a href="https://github.com/FallenDeity/discord.py-masterclass/commits?author=kkrypt0nn" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

If you find this repository helpful, please consider giving it a star ⭐! It helps others discover this resource.
