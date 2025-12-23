# Contributing to Discord.py Masterclass

Thank you for your interest in contributing to Discord.py Masterclass. This guide will help you understand how to contribute effectively to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation Guidelines](#documentation-guidelines)

## Code of Conduct

This project is governed by our [Code of Conduct](CODE-OF-CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. Include these details in your bug report:

- Clear and descriptive title
- Steps to reproduce the problem
- Specific examples and code snippets
- Expected vs. actual behavior
- Python version, discord.py version, and OS information

### Suggesting Features

Feature suggestions should include:

- Clear title and detailed description
- Explanation of why the feature would be useful
- Examples of how it would be used

### Improving Documentation

Documentation improvements include:

- Fixing typos or grammatical errors
- Adding missing documentation
- Improving existing explanations
- Adding more examples

### Contributing Code

Code contributions are welcome in these areas:

- Adding new examples
- Improving existing examples
- Fixing bugs
- Implementing new features
- Improving code quality and performance

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- uv (package manager)

### Setup Steps

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/discord.py-masterclass.git
   cd discord.py-masterclass
   ```

2. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/FallenDeity/discord.py-masterclass.git
   ```

3. Install dependencies:
   ```bash
   uv sync --locked --all-extras --dev
   ```

4. Set up pre-commit hooks (recommended):
   ```bash
   uv run pre-commit install
   ```

## Coding Guidelines

### Style Requirements

- Follow PEP 8 with 120 character line length
- Use Black for code formatting
- Use isort for import sorting  
- Code must pass Ruff linting checks
- Include type hints where applicable

### Code Quality Checks

Run these commands before submitting:

```bash
uv run black .
uv run isort .
uv run ruff check .
```

Or use pre-commit hooks:

```bash
uv run pre-commit run --all-files
```

### Best Practices

1. **Naming Conventions**
   - snake_case for functions and variables
   - PascalCase for class names
   - UPPER_CASE for constants

2. **Documentation**
   - Add docstrings to functions and classes
   - Include type hints in function signatures
   - Comment complex logic

3. **Discord.py Standards**
   - Use application commands where appropriate
   - Implement proper error handling
   - Use cogs for command organization
   - Follow existing example patterns

4. **Example Requirements**
   - Self-contained and runnable
   - Well-commented
   - Beginner-friendly when possible

## Pull Request Process

### Before Submitting

1. Update your fork:
   ```bash
   git fetch upstream
   git checkout master
   git merge upstream/master
   ```

2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes and run quality checks:
   ```bash
   uv run pre-commit run --all-files
   ```

4. Test documentation build (if applicable):
   ```bash
   uv run mkdocs build
   ```

5. Commit and push:
   ```bash
   git add .
   git commit -m "feat: your descriptive commit message"
   git push origin feature/your-feature-name
   ```

### Submitting the PR

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template with:
   - Clear description of changes
   - Related issue numbers (if applicable)
   - Testing steps

## Documentation Guidelines

### Writing Documentation

- Use clear, concise language
- Include practical code examples
- Maintain consistent formatting
- Test all code examples
- Link to relevant discord.py documentation

### Adding New Documentation Pages

1. Create a new `.md` file in the `docs/` directory
2. Add it to `mkdocs.yml` in the `nav` section
3. Follow existing documentation structure
4. Include practical examples

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/FallenDeity/discord.py-masterclass/discussions)
- **Bugs**: Open an [Issue](https://github.com/FallenDeity/discord.py-masterclass/issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
