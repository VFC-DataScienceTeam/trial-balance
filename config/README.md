# Configuration Files

This folder contains configuration files for the trial balance automation system.

## Files to Add

### `config.yml` or `settings.py`
Application settings:
- File paths (input/output directories)
- Validation rules and thresholds
- Report templates and formats
- Email notification settings
- Database connections (if applicable)

### `logging_config.yml`
Logging configuration:
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Log file locations
- Log rotation settings
- Log format templates

### `validation_rules.yml`
Business rules for validation:
- Account number formats
- Required fields
- Valid value ranges
- Balance check tolerances
- Entity-specific rules

### `account_mappings.yml`
Static account mappings (if not in database):
- Legacy to new chart of accounts
- Account rollup hierarchies
- Account categories/classifications

## Usage
Load config in scripts:
```python
import yaml
with open('config/config.yml') as f:
    config = yaml.safe_load(f)
```

## Security Notes
- **Do not commit** database passwords or API keys
- Use environment variables or secret management tools
- Provide `config.example.yml` with placeholders
- Add `config/secrets.yml` to `.gitignore`
