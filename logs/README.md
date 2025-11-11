# Logs

Application logs are stored here.

## Log Files
- `trial_balance.log` - Main application log
- `validation_{date}.log` - Validation run logs
- `reconciliation_{date}.log` - Reconciliation run logs
- `error_{date}.log` - Error-only logs

## Log Rotation
Logs are rotated when they reach 10MB (configurable in `config/logging_config.yml`).
Old logs are kept for 30 days then archived.

## Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages (normal operations)
- **WARNING**: Warning messages (potential issues)
- **ERROR**: Error messages (failures that don't stop execution)
- **CRITICAL**: Critical failures (system cannot continue)

## Viewing Logs
```bash
# View latest log
tail -f logs/trial_balance.log

# Search for errors
grep ERROR logs/trial_balance.log

# View logs from specific date
cat logs/trial_balance_20251104.log
```

## Notes
- Logs folder is gitignored (not committed to version control)
- Logs contain sensitive data - protect access appropriately
- Archive logs regularly for compliance and audit purposes
