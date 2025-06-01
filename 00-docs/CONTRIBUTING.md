# Contributing to auto-devops

Thank you for your interest in contributing to auto-devops! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to uphold our Code of Conduct (to be developed).

## How Can I Contribute?

### Reporting Bugs

Before submitting a bug report:
- Check the issue tracker to see if the bug has already been reported.
- If you're unable to find an open issue addressing the problem, open a new one.

When submitting a bug report, please include:
- A clear and descriptive title
- Steps to reproduce the behavior
- What you expected to happen
- What actually happened
- Any relevant logs or error messages
- Your environment details (OS, K8s version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:
- A clear and descriptive title
- A detailed description of the proposed functionality
- Any potential implementation ideas you have
- Why this enhancement would be useful to auto-devops users

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (if applicable)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

### Local Development Environment

1. Install prerequisites:
   - Kubernetes cluster (can be minikube, kind, or k3s for local development)
   - kubectl
   - Pulumi
   - Go (v1.18+)

2. Clone the repository:
   ```
   git clone https://github.com/yourusername/auto-devops.git
   cd auto-devops
   ```

3. Bootstrap a local development environment:
   ```
   cd 40-bootstrap
   pulumi up --stack dev
   ```

### Project Structure

- `00-docs/`: Documentation files
- `10-tools/`: Development and utility tools
- `20-platform/`: Core platform services and components
- `30-tests/`: Testing framework and test cases
- `40-bootstrap/`: Infrastructure bootstrap scripts

## Coding Standards

- Follow standard Go coding conventions
- Use meaningful variable and function names
- Comment your code where necessary
- Write tests for new functionality

## Testing

- Write unit tests for any new functionality
- Ensure all tests pass before submitting a PR
- Include integration tests where appropriate

## Documentation

- Update documentation to reflect any changes you make
- Document new features, options, and behaviors
- Keep the README and other docs up to date

## Releasing

The maintainers will handle the release process, which includes:
1. Version bumping
2. Changelog updates
3. Tag creation
4. Release publishing

## Questions?

If you have any questions or need assistance with contributing, please open an issue with the "question" label or contact the maintainers directly.

Thank you for contributing to auto-devops! 