# Contributing to CLIP Toolkit

Thank you for your interest in contributing to CLIP Toolkit! This guide will help you get started with contributing to our comprehensive collection of SDKs, validation tools, and utilities for working with the Context Link Interface Protocol (CLIP).

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Release Process](#release-process)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

## 🚀 Getting Started

### Ways to Contribute

- **Bug Reports**: Found a bug? Let us know!
- **Feature Requests**: Have an idea for improvement?
- **Code Contributions**: Fix bugs, add features, improve performance
- **Documentation**: Improve docs, add examples, write tutorials
- **Testing**: Add test cases, improve test coverage
- **Design**: UI/UX improvements, visual assets

### Before You Start

1. **Check existing issues** to avoid duplicating work
2. **Read the documentation** to understand the project
3. **Join our discussions** to get feedback on your ideas
4. **Start small** with good first issues

## 🛠️ Development Setup

### Prerequisites

- **Node.js** 18+ (for TypeScript packages)
- **Python** 3.8+ (for Python packages)
- **Git** for version control
- **npm** or **yarn** for JavaScript dependencies
- **pip** for Python dependencies

### Initial Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/clip-toolkit.git
cd clip-toolkit

# 3. Add upstream remote
git remote add upstream https://github.com/clip-organization/clip-toolkit.git

# 4. Install Node.js dependencies
npm install

# 5. Install Python dependencies
cd packages/sdk-python
pip install -e ".[dev]"
cd ../decoder-python
pip install -e ".[dev]"
cd ../..

# 6. Build all packages
npm run build

# 7. Run tests to ensure everything works
npm test
cd packages/sdk-python && pytest
```

### Development Workflow

```bash
# 1. Create a new branch for your feature
git checkout -b feature/your-feature-name

# 2. Make your changes
# ... edit files ...

# 3. Run tests
npm test
pytest packages/sdk-python

# 4. Run linting
npm run lint
cd packages/sdk-python && flake8 clip_sdk

# 5. Commit your changes
git add .
git commit -m "feat: add your feature description"

# 6. Push to your fork
git push origin feature/your-feature-name

# 7. Create a pull request
```

## 📝 Contributing Guidelines

### Issue Guidelines

**Bug Reports**
- Use the bug report template
- Include steps to reproduce
- Provide system information
- Include error messages and logs
- Add minimal reproduction example

**Feature Requests**
- Use the feature request template
- Explain the use case
- Describe the proposed solution
- Consider alternatives
- Check if it aligns with project goals

### Code Contributions

**Good First Issues**
- Look for issues labeled `good first issue`
- Start with documentation improvements
- Fix typos or improve error messages
- Add test cases for existing functionality

**Larger Contributions**
- Discuss in an issue before starting
- Break down into smaller PRs when possible
- Follow the existing code style
- Add comprehensive tests
- Update documentation

## 🔄 Pull Request Process

### Before Submitting

1. **Ensure tests pass**: All CI checks must be green
2. **Update documentation**: Add/update relevant docs
3. **Add tests**: New features need test coverage
4. **Follow conventions**: Use conventional commit messages
5. **Check compatibility**: Ensure backward compatibility

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated existing tests if needed

## Documentation
- [ ] Updated README if needed
- [ ] Added/updated API documentation
- [ ] Added examples if applicable

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] No new warnings introduced
```

### Review Process

1. **Automated checks**: CI must pass
2. **Code review**: At least one maintainer review
3. **Testing**: Reviewers may test functionality
4. **Documentation**: Ensure docs are updated
5. **Approval**: Maintainer approval required
6. **Merge**: Squash and merge preferred

## 🎨 Coding Standards

### TypeScript/JavaScript

```typescript
// Use TypeScript for all new code
interface CLIPData {
  type: string;
  version: string;
  name: string;
}

// Use meaningful names
const validateCLIPObject = (data: CLIPData): ValidationResult => {
  // Implementation
};

// Add JSDoc comments for public APIs
/**
 * Validates a CLIP object against the schema
 * @param data - The CLIP object to validate
 * @returns Validation result with errors if any
 */
export function validate(data: CLIPData): ValidationResult {
  // Implementation
}
```

**Style Guidelines**
- Use ESLint configuration
- 2 spaces for indentation
- Single quotes for strings
- Trailing commas in objects/arrays
- Semicolons required

### Python

```python
# Use type hints for all functions
from typing import Dict, List, Optional, Any

def validate_clip(data: Dict[str, Any]) -> ValidationResult:
    """Validate a CLIP object.
    
    Args:
        data: The CLIP object to validate
        
    Returns:
        ValidationResult with errors if any
        
    Raises:
        ValueError: If data is None or empty
    """
    if not data:
        raise ValueError("CLIP data is required")
    
    # Implementation
    return ValidationResult(is_valid=True, errors=[])

# Use dataclasses for structured data
from dataclasses import dataclass

@dataclass
class ValidationError:
    path: str
    message: str
    severity: str = "error"
```

**Style Guidelines**
- Follow PEP 8
- Use Black for formatting
- Use isort for import sorting
- Use type hints everywhere
- Maximum line length: 88 characters

### Documentation

```python
# Use Google-style docstrings
def fetch_clip(url: str, timeout: int = 30) -> Dict[str, Any]:
    """Fetch a CLIP object from a URL.
    
    Args:
        url: The URL to fetch from
        timeout: Request timeout in seconds
        
    Returns:
        The fetched CLIP object as a dictionary
        
    Raises:
        CLIPFetchError: If the fetch operation fails
        
    Example:
        >>> clip = fetch_clip('https://example.com/clip.json')
        >>> print(clip['name'])
        'Example Venue'
    """
```

## 🧪 Testing Requirements

### Test Coverage

- **Minimum coverage**: 80% for new code
- **Preferred coverage**: 90%+ for critical paths
- **Required tests**: All public APIs must have tests

### TypeScript Testing

```typescript
// Use Jest for testing
import { CLIPValidator } from '../src/validator';

describe('CLIPValidator', () => {
  let validator: CLIPValidator;
  
  beforeEach(() => {
    validator = new CLIPValidator();
  });
  
  it('should validate a valid CLIP object', () => {
    const validClip = {
      type: 'venue',
      version: '1.0.0',
      name: 'Test Venue'
    };
    
    const result = validator.validate(validClip);
    
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });
  
  it('should reject invalid CLIP objects', () => {
    const invalidClip = { type: 'venue' }; // Missing version
    
    const result = validator.validate(invalidClip);
    
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });
});
```

### Python Testing

```python
# Use pytest for testing
import pytest
from clip_sdk import CLIPValidator, ValidationError

class TestCLIPValidator:
    def setup_method(self):
        self.validator = CLIPValidator()
    
    def test_valid_clip_object(self):
        """Test validation of a valid CLIP object."""
        valid_clip = {
            'type': 'venue',
            'version': '1.0.0',
            'name': 'Test Venue'
        }
        
        result = self.validator.validate(valid_clip)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_invalid_clip_object(self):
        """Test validation of an invalid CLIP object."""
        invalid_clip = {'type': 'venue'}  # Missing version
        
        result = self.validator.validate(invalid_clip)
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any('version' in error.path for error in result.errors)
    
    @pytest.mark.parametrize("clip_type", ["venue", "event", "product"])
    def test_different_clip_types(self, clip_type):
        """Test validation for different CLIP types."""
        clip_data = {
            'type': clip_type,
            'version': '1.0.0',
            'name': f'Test {clip_type.title()}'
        }
        
        result = self.validator.validate(clip_data)
        assert result.is_valid
```

### Integration Tests

```bash
#!/bin/bash
# tests/integration/test_cli_python_integration.sh

# Test CLI and Python SDK work together
echo "Testing CLI and Python SDK integration..."

# Generate template with CLI
clip generate --type venue --output /tmp/test-venue.json

# Validate with Python SDK
python -c "
import json
from clip_sdk import CLIPValidator

with open('/tmp/test-venue.json') as f:
    data = json.load(f)

validator = CLIPValidator()
result = validator.validate(data)
assert result.is_valid, f'Integration test failed: {result.errors}'
print('✅ Integration test passed')
"

echo "Integration test completed successfully"
```

## 📚 Documentation

### README Updates

- Update package READMEs for new features
- Add usage examples
- Update installation instructions
- Keep feature lists current

### API Documentation

- Use JSDoc for TypeScript
- Use Google-style docstrings for Python
- Include examples in documentation
- Document all public APIs

### Examples

- Add examples for new features
- Update existing examples if APIs change
- Test all examples to ensure they work
- Include real-world use cases

## 🚀 Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update version numbers** in all packages
2. **Update CHANGELOG.md** with new features/fixes
3. **Run full test suite** on all platforms
4. **Update documentation** if needed
5. **Create release PR** for review
6. **Tag release** after merge
7. **Publish packages** to npm/PyPI
8. **Create GitHub release** with notes

### Changelog Format

```markdown
## [1.2.0] - 2024-01-15

### Added
- New feature for batch validation
- Support for custom validation rules

### Changed
- Improved error messages in CLI
- Updated Python SDK dependencies

### Fixed
- Fixed memory leak in large file processing
- Corrected timezone handling in timestamps

### Deprecated
- Old validation API (will be removed in v2.0)

### Security
- Updated dependencies with security fixes
```

## 🏷️ Issue Labels

We use labels to categorize issues:

- **Type**: `bug`, `feature`, `documentation`, `question`
- **Priority**: `critical`, `high`, `medium`, `low`
- **Difficulty**: `good first issue`, `help wanted`, `expert needed`
- **Component**: `cli`, `python-sdk`, `validator-core`, `decoder-lib`
- **Status**: `needs-triage`, `in-progress`, `blocked`, `ready-for-review`

## 🆘 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Discord**: Real-time chat (link in README)
- **Email**: maintainers@clipprotocol.org

### Maintainers

- **@maintainer1** - Project lead, architecture decisions
- **@maintainer2** - Python SDK, testing infrastructure
- **@maintainer3** - TypeScript packages, CI/CD

### Response Times

- **Bug reports**: 2-3 business days
- **Feature requests**: 1 week
- **Pull requests**: 3-5 business days
- **Security issues**: 24 hours

## 📄 License

By contributing to CLIP Toolkit, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to CLIP Toolkit! Your efforts help make CLIP more accessible and useful for developers worldwide. 🚀 
