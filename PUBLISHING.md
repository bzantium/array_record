# Publishing ArrayRecord Python to PyPI

This guide walks you through publishing your customized ArrayRecord package to PyPI under the name `array-record-python`.

## Prerequisites

1. **PyPI Account**: Create accounts on both [PyPI](https://pypi.org/account/register/) and [Test PyPI](https://test.pypi.org/account/register/)

2. **API Tokens**: Generate API tokens for authentication:
   - Go to PyPI Account Settings → API tokens
   - Generate tokens for both PyPI and Test PyPI
   - Store them securely

3. **Configure Authentication**:
   ```bash
   # Install required tools
   pip install build twine keyring
   
   # Configure PyPI credentials
   keyring set https://upload.pypi.org/legacy/ __token__
   # Enter your PyPI API token when prompted
   
   # Configure Test PyPI credentials  
   keyring set https://test.pypi.org/legacy/ __token__
   # Enter your Test PyPI API token when prompted
   ```

## Step-by-Step Publishing Process

### 1. Prepare Your Repository

Ensure your repository is ready:

```bash
# Update version in setup.py if needed
# Update CHANGELOG.md with new features
# Commit all changes
git add .
git commit -m "Prepare for PyPI release v0.8.1"
git push origin main
```

### 2. Test Build Locally

```bash
# Clean and build
python publish_to_pypi.py --clean-only
python -m build

# Check the package
twine check dist/*
```

### 3. Upload to Test PyPI

Test your package first:

```bash
# Upload to Test PyPI
python publish_to_pypi.py --test
```

### 4. Test Installation from Test PyPI

```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ array-record-python

# Test basic functionality
python -c "
from array_record.python import array_record_module
print('ArrayRecord Python imported successfully!')
writer = array_record_module.ArrayRecordWriter('/tmp/test.array_record')
writer.write(b'test data')
writer.close()
print('Basic functionality works!')
"

# Clean up
deactivate
rm -rf test_env
```

### 5. Upload to Production PyPI

If testing passes:

```bash
# Upload to production PyPI
python publish_to_pypi.py
```

### 6. Verify Publication

```bash
# Check that your package is available
pip search array-record-python  # If search is available
# Or visit: https://pypi.org/project/array-record-python/

# Test installation
pip install array-record-python
```

## Read the Docs Setup

### 1. Connect Repository

1. Go to [Read the Docs](https://readthedocs.org/)
2. Sign in with your GitHub account
3. Import your project: `bzantium/array_record`
4. The project will be available at `https://array-record.readthedocs.io`

### 2. Configuration

The repository includes `.readthedocs.yaml` which configures:
- Python 3.11 build environment
- Sphinx documentation builder
- PDF and ePub export formats
- Automatic dependency installation

### 3. Build Documentation

Trigger a build:
- Push changes to trigger automatic builds
- Or manually trigger builds from the Read the Docs dashboard

## Package Structure

Your published package will include:

```
array-record-python/
├── array_record/
│   ├── python/           # Python bindings
│   ├── beam/            # Apache Beam integration
│   └── __init__.py
├── docs/                # Sphinx documentation
├── README.md           # Package description
├── LICENSE             # Apache 2.0 license
├── setup.py            # Package configuration
├── pyproject.toml      # Modern Python packaging
└── MANIFEST.in         # File inclusion rules
```

## Version Management

### Updating Versions

1. Update version in `setup.py`:
   ```python
   version='0.8.2',
   ```

2. Update version in `docs/conf.py`:
   ```python
   release = '0.8.2'
   version = '0.8.2'
   ```

3. Update `CHANGELOG.md` with new features

4. Create git tag:
   ```bash
   git tag -a v0.8.2 -m "Release version 0.8.2"
   git push origin v0.8.2
   ```

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.9.0): New features, backward compatible
- **PATCH** (0.8.1): Bug fixes, backward compatible

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   ```bash
   # Reconfigure credentials
   keyring set https://upload.pypi.org/legacy/ __token__
   ```

2. **Package Name Conflicts**:
   - Ensure `array-record-python` is available on PyPI
   - Consider alternative names if needed

3. **Build Failures**:
   ```bash
   # Clean everything and rebuild
   python publish_to_pypi.py --clean-only
   rm -rf build/ dist/ *.egg-info/
   python -m build
   ```

4. **Documentation Build Issues**:
   ```bash
   # Test documentation build locally
   cd docs
   pip install -r requirements.txt
   make html
   ```

### Getting Help

- **PyPI Issues**: [PyPI Help](https://pypi.org/help/)
- **Read the Docs**: [RTD Support](https://docs.readthedocs.io/)
- **Packaging**: [Python Packaging Guide](https://packaging.python.org/)

## Maintenance

### Regular Updates

1. **Monitor Dependencies**: Update requirements regularly
2. **Security Updates**: Watch for security advisories
3. **Documentation**: Keep docs updated with code changes
4. **Community**: Respond to issues and PRs

### Automated Publishing

Consider setting up GitHub Actions for automated publishing:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  release:
    types: [published]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Success Checklist

- [ ] Package builds without errors
- [ ] Tests pass on Test PyPI
- [ ] Documentation builds on Read the Docs
- [ ] Package installs correctly: `pip install array-record-python`
- [ ] Basic functionality works
- [ ] README displays correctly on PyPI
- [ ] Documentation is accessible at `array-record.readthedocs.io`

Your ArrayRecord Python package is now ready for the community! 🎉
