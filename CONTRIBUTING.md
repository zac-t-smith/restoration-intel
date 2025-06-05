# Contributing to Restoration-Intel

## Welcome Contributors! 🚀

Restoration-Intel is an open-source business intelligence platform designed to help restoration businesses optimize their operations and financial performance.

## Getting Started

### Prerequisites
- Docker Desktop
- Node.js (v18+)
- Python (v3.11+)
- Git

### Development Setup

1. **Clone the Repository**
```bash
git clone https://github.com/your-org/restoration-intel.git
cd restoration-intel
```

2. **Environment Configuration**
- Copy `.env.docker.example` to `.env.docker`
- Fill in the required environment variables
- NEVER commit sensitive information to the repository

3. **Install Dependencies**
```bash
# Install Node.js dependencies
npm install
cd next-app && npm install
cd ..

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Development Workflow

### Branch Strategy
- `main`: Stable production-ready code
- `develop`: Active development branch
- `feature/`: New feature branches
- `bugfix/`: Bug fix branches
- `hotfix/`: Critical production bug fixes

### Commit Guidelines
- Use conventional commits: 
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation updates
  - `refactor:` for code refactoring
  - `test:` for test-related changes
  - `chore:` for maintenance tasks

### Pull Request Process
1. Fork the repository
2. Create a feature/bugfix branch
3. Make your changes
4. Write/update tests
5. Ensure all tests pass
6. Submit a pull request to `develop`

## Code Quality

### Linting
- Python: `flake8`, `black`
- TypeScript/React: ESLint, Prettier
- Run `npm run lint` before committing

### Testing
- Python: `pytest`
- JavaScript/React: Jest
- Run `npm test` and `python -m pytest`

## Performance and Security

### Performance Considerations
- Optimize database queries
- Use caching mechanisms
- Profile and benchmark new features

### Security Guidelines
- Never commit secrets or sensitive data
- Use environment variables for configuration
- Follow OWASP security best practices
- Conduct regular security audits

## Metrics and Monitoring

### Adding New Metrics
1. Update `leading_indicator_engine.py`
2. Add SQL/RPC functions in Supabase
3. Create corresponding frontend components
4. Write comprehensive tests

## Documentation

### Updating Docs
- Keep README.md updated
- Document new features and setup steps
- Update inline code comments
- Create/update architectural diagrams

## Community

### Reporting Issues
- Use GitHub Issues
- Provide detailed reproduction steps
- Include environment details
- Be respectful and collaborative

### Feature Requests
- Open an issue with `[Feature Request]` prefix
- Describe the proposed feature
- Explain its business value
- Discuss potential implementation approaches

## Legal

By contributing, you agree to:
- Apache 2.0 License terms
- Code of Conduct
- Developer Certificate of Origin

---

**Happy Coding! 💻🚒**