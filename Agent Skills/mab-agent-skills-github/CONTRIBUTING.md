# Contributing to MAB AI Strategies Agent Skills Platform

Thank you for your interest in contributing to the MAB AI Agent Skills Platform!

## 🤝 Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Collaborate openly
- Maintain confidentiality of proprietary business logic

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork:** `git clone https://github.com/yourusername/mab-agent-skills.git`
3. **Set up development environment:** Follow README.md
4. **Create a branch:** `git checkout -b feature/your-feature-name`

## 📋 Development Workflow

### Before Starting
- Check existing issues and pull requests
- Open an issue to discuss major changes
- Ensure you understand the skill architecture

### Making Changes
1. Follow the existing code patterns (see Skill 01 & 02)
2. Write tests for new features
3. Update documentation
4. Follow Python style guide (PEP 8)
5. Use Black for code formatting

### Code Standards

```python
# ✅ Good: Follows our patterns
async def calculate_score(account_id: str) -> float:
    """
    Calculate score with clear docstring
    
    Args:
        account_id: Account identifier
        
    Returns:
        Calculated score
    """
    logger.info(f"Calculating score for {account_id}")
    # ... implementation
    return score

# ❌ Bad: No typing, no docs, no logging
def calc(id):
    # ... implementation
    return score
```

### Testing Requirements

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_health_service.py

# Check coverage (must be >80%)
pytest --cov=skills --cov=shared --cov-report=html
```

### Documentation Requirements
- Docstrings for all functions
- Update SKILL.md if changing behavior
- Add examples for complex features
- Update README if adding dependencies

## 🔧 Pull Request Process

1. **Update your branch:**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run quality checks:**
   ```bash
   # Format code
   black shared/ skills/
   
   # Lint
   flake8 shared/ skills/
   
   # Security scan
   bandit -r shared/ skills/
   
   # Tests
   pytest tests/
   ```

3. **Commit with conventional commits:**
   ```
   feat: add email sentiment analysis to health scoring
   fix: correct churn probability calculation
   docs: update README with deployment instructions
   test: add unit tests for battlecard generation
   refactor: optimize database queries in health service
   ```

4. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Fill out the PR template
   - Link related issues
   - Request review

5. **Address review feedback**

6. **Wait for CI to pass**

## 🎯 Contribution Areas

### High Priority
- Complete Skills 3-10 implementations
- Add integration tests
- Improve error handling
- Optimize LLM costs
- Add monitoring dashboards

### Medium Priority
- Add more test coverage
- Improve documentation
- Create usage examples
- Optimize database queries

### Low Priority
- Code refactoring
- Performance optimizations
- UI improvements (if applicable)

## 🐛 Bug Reports

**Use this template:**

```markdown
**Bug Description:**
Clear description of the issue

**To Reproduce:**
1. Step 1
2. Step 2
3. Error occurs

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: macOS/Linux/Windows
- Python version: 3.11
- Skill: 01-competitive-intelligence

**Logs:**
```
Paste relevant logs
```

**Additional Context:**
Screenshots, error messages, etc.
```

## 💡 Feature Requests

**Use this template:**

```markdown
**Feature Description:**
Clear description of proposed feature

**Use Case:**
Why is this needed? What problem does it solve?

**Proposed Implementation:**
How could this work?

**Alternatives Considered:**
Other approaches you've thought about

**Priority:**
High/Medium/Low
```

## 🏗️ Adding a New Skill

Follow this checklist:

- [ ] Create skill directory: `skills/XX-skill-name/`
- [ ] Write SKILL.md documentation
- [ ] Implement handler.py (copy from Skill 01)
- [ ] Implement service.py
- [ ] Create models.py for Pydantic schemas
- [ ] Add integrations.py if needed
- [ ] Create Dockerfile
- [ ] Add requirements.txt (skill-specific deps)
- [ ] Write tests (handler + service)
- [ ] Update main README.md
- [ ] Update docker-compose.yml
- [ ] Test locally
- [ ] Create PR

## 📝 Style Guide

### Python
- Use type hints
- Max line length: 127 characters
- Use Black for formatting
- Docstrings for all public functions
- Descriptive variable names

### Git Commits
- Use conventional commits format
- Keep commits atomic
- Write clear commit messages
- Reference issues when applicable

### Documentation
- Use Markdown for docs
- Include code examples
- Keep README up to date
- Document breaking changes

## 🔐 Security

**DO NOT commit:**
- API keys or secrets
- `.env` files with real credentials
- Private keys or certificates
- Customer data
- Proprietary business logic (if applicable)

**If you find a security vulnerability:**
1. **DO NOT** open a public issue
2. Email: security@mabstrategies.com
3. Include detailed description
4. We'll respond within 48 hours

## 📦 Dependency Management

### Adding Dependencies
1. Add to `requirements.txt`
2. Update Docker images
3. Test with `pip install -r requirements.txt`
4. Document why dependency is needed

### Updating Dependencies
1. Check for breaking changes
2. Update version in requirements.txt
3. Run full test suite
4. Update documentation if needed

## ✅ Merge Criteria

PRs will be merged when:
- ✅ All CI checks pass
- ✅ Code coverage >80%
- ✅ Code review approved
- ✅ Documentation updated
- ✅ No merge conflicts
- ✅ Follows style guide
- ✅ Tests included

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📬 Questions?

- Open an issue with `question` label
- Email: dev@mabstrategies.com
- Check documentation first

---

**Thank you for contributing to MAB AI Strategies!** 🚀
