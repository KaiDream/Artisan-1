# Contributing to Artisan-1

Thank you for your interest in contributing to the Artisan-1 project! This document provides guidelines and information for contributors.

---

## 🌟 Ways to Contribute

### Code Contributions
- **Bug fixes** - Fix issues in existing code
- **New features** - Implement new capabilities
- **Optimizations** - Improve performance
- **Tests** - Add or improve test coverage
- **Documentation** - Improve code comments

### Hardware Contributions
- **CAD designs** - Improved 3D printable parts
- **Circuit designs** - Better electronics layouts
- **Assembly guides** - Build documentation
- **Modifications** - Alternative component choices

### Documentation
- **Tutorials** - Step-by-step guides
- **Examples** - Sample applications
- **Translations** - Non-English documentation
- **Videos** - Build logs, demos

### Community
- **Bug reports** - Help identify issues
- **Feature requests** - Suggest improvements
- **Support** - Help other builders
- **Showcase** - Share your build

---

## 🚀 Getting Started

### 1. Fork the Repository

Click "Fork" on GitHub to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/Artisan-1.git
cd Artisan-1
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test additions

### 4. Set Up Development Environment

```bash
# On Raspberry Pi
./setup.sh

# On other systems (for development)
pip install -r requirements.txt
```

---

## 💻 Development Guidelines

### Code Style

**Python:**
- Follow [PEP 8](https://pep8.org/)
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

**Example:**
```python
def calculate_inverse_kinematics(
    target_x: float,
    target_y: float,
    target_z: float
) -> Optional[JointAngles]:
    """
    Calculate inverse kinematics for target position.
    
    Args:
        target_x: X coordinate in meters
        target_y: Y coordinate in meters
        target_z: Z coordinate in meters
        
    Returns:
        Joint angles or None if unreachable
    """
    # Implementation here
    pass
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting
- `refactor` - Code restructuring
- `test` - Tests
- `chore` - Maintenance

**Examples:**
```
feat(vision): add custom fabric corner detection model

fix(servo): correct PWM timing for MG996R servos

docs(README): update installation instructions
```

### Testing

Always add tests for new features:

```bash
# Run all tests
python3 tests/test_subsystems.py

# Run specific test
python3 tests/test_subsystems.py ik
```

**Test Requirements:**
- Unit tests for new functions
- Integration tests for subsystems
- Document expected vs actual behavior

### Documentation

Update documentation for code changes:
- Docstrings in code
- README.md for user-facing changes
- docs/ for detailed guides
- config/ for configuration changes

---

## 📝 Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts with main

### 2. Submit Pull Request

1. Push to your fork
2. Open PR on GitHub
3. Fill out PR template
4. Link related issues

**PR Title Format:**
```
[Type] Brief description

Examples:
[Feature] Add IMU support for balance control
[Fix] Correct I2C address conflict
[Docs] Add wiring diagram
```

**PR Description Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes
```

### 3. Code Review

- Respond to review comments
- Make requested changes
- Push updates to same branch
- Request re-review when ready

### 4. Merge

Once approved, maintainers will merge your PR.

---

## 🐛 Bug Reports

### Before Submitting

1. **Search existing issues** - May already be reported
2. **Test on latest version** - May be fixed
3. **Isolate the problem** - Minimal reproduction

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. Connect servo '...'
3. Observe error '...'

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Hardware: Raspberry Pi 5
- OS: Raspberry Pi OS 64-bit
- Python: 3.11.2
- Version: 0.1.0

**Logs**
```
Paste relevant logs here
```

**Additional Context**
Photos, videos, etc.
```

---

## 💡 Feature Requests

### Template

```markdown
**Feature Description**
What feature would you like?

**Use Case**
Why is this needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches?

**Additional Context**
Mockups, examples, etc.
```

### Evaluation Criteria

Features are evaluated on:
1. **Alignment** - Fits project goals
2. **Feasibility** - Can be implemented
3. **Impact** - Benefits users
4. **Maintenance** - Sustainable to support

---

## 🎨 Hardware Contributions

### CAD Files

- Provide source files (STEP, Fusion 360, etc.)
- Include STL exports
- Document print settings
- Add assembly instructions

### Circuit Designs

- Schematic (PDF + source)
- PCB layout if applicable
- BOM with part numbers
- Testing instructions

### Wiring Diagrams

- Use Fritzing or similar
- Include pin mappings
- Document wire gauges
- Show power distribution

---

## 📚 Documentation Standards

### Markdown

- Use proper heading hierarchy
- Include code blocks with syntax highlighting
- Add images/diagrams where helpful
- Link to related documents

### Code Comments

```python
# Good: Explains WHY
# Convert to radians because math functions expect it
angle_rad = np.radians(angle_deg)

# Bad: Explains WHAT (obvious from code)
# Convert angle to radians
angle_rad = np.radians(angle_deg)
```

### Diagrams

- ASCII art for simple flow
- Mermaid for complex diagrams
- Images for circuit/wiring

---

## 🏆 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

Significant contributions may earn:
- Collaborator status
- Project credits
- Feature naming rights

---

## ❓ Questions?

- **General questions:** GitHub Discussions
- **Bug reports:** GitHub Issues
- **Security issues:** Email kaidream78@gmail.com
- **Other:** Email kaidream78@gmail.com

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Thank You!

Every contribution, no matter how small, helps make Artisan-1 better for everyone. We appreciate your time and effort!

---

**Happy Building! 🤖**
