# CI/CD Pipelines Guide

This document explains the comprehensive CI/CD pipelines implemented for the CLIP Toolkit project.

## Overview

The CLIP Toolkit uses GitHub Actions to provide automated testing, building, and publishing for both TypeScript and Python packages. The CI/CD system consists of three main workflows:

1. **TypeScript CI** - Tests and builds TypeScript packages
2. **Python CI** - Tests and builds Python packages  
3. **Publish** - Publishes packages to npm and PyPI

## Workflows

### 1. TypeScript CI (`typescript-ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Changes to TypeScript packages or workflow files

**Features:**
- ✅ **Multi-version testing** - Node.js 18.x, 20.x, 21.x
- ✅ **Comprehensive linting** - ESLint + TypeScript type checking
- ✅ **Full test coverage** - Jest with coverage reporting
- ✅ **Security scanning** - npm audit + dependency vulnerability checks
- ✅ **Build verification** - Compile and test CLI functionality
- ✅ **Integration tests** - Cross-package functionality testing
- ✅ **Publish readiness** - Package validation for npm
- ✅ **Caching** - Optimized dependency caching

**Jobs:**
1. **Setup** - Install dependencies and setup cache
2. **Lint** - ESLint and TypeScript type checking
3. **Test** - Run Jest tests across multiple Node.js versions
4. **Build** - Compile TypeScript and verify artifacts
5. **Security** - Run security scans and audits
6. **Integration** - Test cross-package functionality
7. **Publish Check** - Validate packages for publishing
8. **Summary** - Aggregate results and report status

### 2. Python CI (`python-ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Changes to Python packages or workflow files

**Features:**
- ✅ **Multi-version testing** - Python 3.8, 3.9, 3.10, 3.11, 3.12
- ✅ **Cross-platform testing** - Ubuntu, Windows, macOS
- ✅ **Code quality** - Black, isort, flake8, mypy
- ✅ **Security scanning** - Bandit, Safety, Semgrep
- ✅ **Full test coverage** - pytest with coverage reporting
- ✅ **Package building** - Build wheels and source distributions
- ✅ **Performance testing** - Basic performance benchmarks
- ✅ **Integration tests** - Cross-package functionality testing

**Jobs:**
1. **Setup** - Install dependencies and setup cache
2. **Lint** - Black, isort, flake8, mypy, bandit
3. **Test** - Run pytest across multiple Python versions and OS
4. **Security** - Run security scans (bandit, safety, semgrep)
5. **Build** - Build packages and test installation
6. **Integration** - Test cross-package functionality
7. **Publish Check** - Validate packages for PyPI
8. **Performance** - Run performance benchmarks
9. **Summary** - Aggregate results and report status

### 3. Publish (`publish.yml`)

**Triggers:**
- GitHub release created
- Manual workflow dispatch with options

**Features:**
- ✅ **Dual publishing** - npm and PyPI support
- ✅ **Version validation** - Semantic version checking
- ✅ **Duplicate prevention** - Check existing versions
- ✅ **Build verification** - Full test suite before publish
- ✅ **Dry run support** - Test publishing without actual release
- ✅ **Rollback safety** - Validation before publication
- ✅ **Auto-changelog** - Generate release notes
- ✅ **Notification** - Status reporting and PR comments

**Jobs:**
1. **Validate** - Version validation and duplicate checking
2. **Build TypeScript** - Build and test TypeScript packages
3. **Build Python** - Build and test Python packages
4. **Publish npm** - Publish to npm registry
5. **Publish PyPI** - Publish to PyPI
6. **Create Release** - Generate GitHub release with changelog
7. **Notify** - Report results and notify stakeholders

## Usage

### Running CI on Pull Requests

CI runs automatically on all pull requests. To ensure your changes pass CI:

1. **TypeScript changes:**
   ```bash
   # Run locally before pushing
   cd packages/your-package
   npm run lint
   npm test
   npm run build
   ```

2. **Python changes:**
   ```bash
   # Run locally before pushing
   cd packages/your-package
   black .
   isort .
   flake8 .
   pytest
   ```

### Publishing Packages

#### Option 1: GitHub Release (Recommended)

1. Create a new release on GitHub
2. Use semantic version tags (e.g., `v1.2.3`)
3. Publish workflow runs automatically
4. All packages published to both registries

#### Option 2: Manual Workflow Dispatch

1. Go to Actions → Publish Packages
2. Click "Run workflow"
3. Choose options:
   - **Version type**: major/minor/patch/prerelease
   - **Publish npm**: Enable/disable TypeScript packages
   - **Publish PyPI**: Enable/disable Python packages
   - **Dry run**: Test without actual publishing

### Monitoring CI Status

**Status Checks:**
- All workflows must pass for PR merging
- View detailed logs in Actions tab
- Coverage reports uploaded to Codecov
- Security reports available as artifacts

**Artifacts:**
- Build artifacts (7 days retention)
- Coverage reports (7 days retention)
- Security scan reports (30 days retention)
- Test results (7 days retention)

## Configuration

### Required Secrets

Configure these in repository settings:

```
# npm publishing
NPM_TOKEN=<npm-access-token>

# PyPI publishing  
PYPI_API_TOKEN=<pypi-api-token>

# GitHub (automatically available)
GITHUB_TOKEN=<github-token>
```

### Environment Setup

**npm production environment:**
- Required for npm publishing
- Add protection rules if needed

**pypi-production environment:**
- Required for PyPI publishing
- Add protection rules if needed

### Package Configuration

**TypeScript packages require:**
```json
{
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "lint": "eslint src --ext .ts",
    "test:coverage": "jest --coverage"
  }
}
```

**Python packages require:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0", 
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0"
]
```

## Troubleshooting

### Common Issues

**1. TypeScript CI failing:**
```bash
# Check linting
npm run lint

# Check types
npx tsc --noEmit

# Run tests
npm test
```

**2. Python CI failing:**
```bash
# Check formatting
black --check .
isort --check .

# Check linting
flake8 .

# Run tests
pytest
```

**3. Publishing failing:**
- Check version format (semantic versioning)
- Verify no duplicate versions exist
- Ensure all tests pass
- Check secret configuration

### Debug Tips

**View detailed logs:**
1. Go to Actions tab
2. Click on failed workflow
3. Expand job sections
4. Check step-by-step output

**Download artifacts:**
1. Go to workflow run
2. Scroll to Artifacts section
3. Download relevant reports
4. Analyze locally

**Test locally:**
```bash
# Simulate CI environment
export CI=true

# Run commands as CI would
npm ci  # Instead of npm install
python -m pytest  # Instead of pytest
```

## Monitoring and Metrics

### Coverage Reports
- Uploaded to Codecov automatically
- View at: https://codecov.io/gh/clip-organization/clip-toolkit
- Coverage targets: 80%+ for all packages

### Security Scanning
- **npm audit** - Dependency vulnerabilities
- **bandit** - Python security issues
- **safety** - Known vulnerability database
- **semgrep** - Code pattern analysis

### Performance Tracking
- Basic performance tests in Python CI
- Monitor for regressions
- Expand as needed

## Maintenance

### Dependency Updates
- **Dependabot** configured for automatic updates
- CI validates all dependency changes
- Security updates prioritized

### Workflow Updates
- Test changes in feature branches
- Use workflow_dispatch for testing
- Monitor for GitHub Actions updates

### Package Updates
- Follow semantic versioning
- Update CHANGELOG.md
- Test across all supported versions

## Best Practices

### Development Workflow
1. Create feature branch
2. Make changes with tests
3. Run local validation
4. Push and create PR
5. Address CI feedback
6. Merge after approval

### Release Workflow
1. Update version numbers
2. Update documentation
3. Create GitHub release
4. Verify package publication
5. Announce release

### Security Practices
- Regular dependency updates
- Security scan monitoring
- Secret rotation schedule
- Access control reviews

## Support

For CI/CD issues:
1. Check this guide
2. Review workflow logs
3. Test locally
4. Create issue with details
5. Tag @maintainers for urgent issues

---

**Last Updated:** January 2024  
**Next Review:** March 2024 
