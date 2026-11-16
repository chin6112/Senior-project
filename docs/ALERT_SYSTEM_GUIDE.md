# Alert System Documentation

## Overview

The Alert System automatically notifies you when data quality issues or anomalies are detected. Supports Email, Slack, and Discord.

## Supported Channels

### 1. Email Alerts
- **Provider**: Gmail SMTP
- **Format**: HTML email with detailed report
- **Best for**: Critical alerts, permanent records

### 2. Slack Alerts
- **Format**: Rich formatted Slack messages
- **Features**: Thread replies, file uploads
- **Best for**: Team notifications, quick visibility

### 3. Discord Alerts
- **Format**: Embed messages with color coding
- **Features**: Role mentions, webhook integration
- **Best for**: Development teams, real-time monitoring

## Configuration

### File: `config/alert_config.yaml`

```yaml
alert_system:
  enabled: true
  debug: false  # Print alert details to console

email:
  enabled: true
  smtp_server: smtp.gmail.com
  smtp_port: 587
  sender_email: "your-email@gmail.com"
  sender_password: "${GMAIL_PASSWORD}"  # Set via environment variable
  
  recipients:
    - admin@company.com
    - data-team@company.com
  
  # Alert threshold
  min_severity: "WARN"  # PASS, INFO, WARN, FAIL, CRITICAL
  
  # Settings
  include_failed_rows: true
  include_anomalies: true
  max_rows_in_email: 50
  
  # Template
  subject: "[Data Quality] {status} - {file_name}"
  html_template: "templates/email_template.html"

slack:
  enabled: false
  webhook_url: "${SLACK_WEBHOOK_URL}"  # Set via environment variable
  
  channel: "#data-quality"
  username: "Data Quality Bot"
  icon_emoji: ":bar_chart:"
  
  min_severity: "WARN"
  include_details: true
  mention_on_fail: false
  mention_users: []  # List of Slack user IDs

discord:
  enabled: false
  webhook_url: "${DISCORD_WEBHOOK_URL}"  # Set via environment variable
  
  username: "Data Quality Bot"
  avatar_url: "https://example.com/icon.png"
  
  min_severity: "WARN"
  color_scheme:
    PASS: 65280      # Green
    WARN: 16776960   # Yellow
    FAIL: 16711680   # Red
    CRITICAL: 8711680  # Dark red
  
  include_attachments: true

# Alert triggers
triggers:
  validation_failure:
    enabled: true
    severity: "FAIL"
  
  anomaly_detected:
    enabled: true
    severity: "WARN"
    min_confidence: 0.8  # Only alert if confidence > 80%
    min_count: 5         # Alert if >5 anomalies found
  
  high_failure_rate:
    enabled: true
    threshold: 0.20      # >20% rows failed
    severity: "CRITICAL"
  
  schema_mismatch:
    enabled: true
    severity: "FAIL"

# Rate limiting
rate_limiting:
  enabled: true
  max_alerts_per_hour: 10
  min_interval_seconds: 300  # Min 5 min between alerts

# Retry policy
retry_policy:
  enabled: true
  max_retries: 3
  retry_delay_seconds: 60
  backoff_multiplier: 2.0  # Exponential backoff
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Gmail Setup
GMAIL_PASSWORD=your-app-specific-password

# Slack Setup
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Discord Setup
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK/URL
```

**Important:** Use app-specific passwords, not your main password!

## Setup Guide

### Gmail (Email Alerts)

1. **Enable 2-Factor Authentication**
   ```
   Gmail Settings → Security → 2-Step Verification
   ```

2. **Create App-Specific Password**
   ```
   Gmail Settings → Security → App passwords
   - Select "Mail"
   - Select "Windows Computer" (or your device)
   - Copy the 16-character password
   ```

3. **Store in `.env`**
   ```
   GMAIL_PASSWORD=xxxx xxxx xxxx xxxx
   ```

### Slack (Slack Alerts)

1. **Create Incoming Webhook**
   ```
   Slack Workspace → Settings → App & integrations
   → Incoming Webhooks → Add New Webhook
   → Select channel → Allow
   → Copy Webhook URL
   ```

2. **Store in `.env`**
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
   ```

3. **Configure in `alert_config.yaml`**
   ```yaml
   slack:
     enabled: true
     webhook_url: "${SLACK_WEBHOOK_URL}"
   ```

### Discord (Discord Alerts)

1. **Create Webhook**
   ```
   Server Settings → Integrations → Webhooks → New Webhook
   → Customize name and channel → Copy Webhook URL
   ```

2. **Store in `.env`**
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```

3. **Configure in `alert_config.yaml`**
   ```yaml
   discord:
     enabled: true
     webhook_url: "${DISCORD_WEBHOOK_URL}"
   ```

## Alert Messages

### Email Alert Example

```
Subject: [Data Quality] FAIL - sales_data.csv

From: data-quality@company.com
Date: 2026-11-16 21:15:32

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DATA QUALITY REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File: sales_data.csv
Time: 2026-11-16T21:15:32+07:00
Status: FAIL ❌

SUMMARY
-------
Total Rows: 1,000
Rows Failed: 234 (23.4%)
Validation Status: FAIL

VALIDATION FAILURES
-------------------
✗ Missing Values: 150 rows
  Columns affected: customer_id, email, phone
  
✗ Schema Mismatch: 50 rows
  Expected numeric, got text: amount
  
✗ Invalid Dates: 34 rows
  Column: order_date
  Format expected: YYYY-MM-DD

ANOMALIES DETECTED
------------------
🔴 47 anomalies found (confidence > 80%)

Top 5:
  Row 5:    price=999.99 (confidence: 96%)
  Row 17:   quantity=-100 (confidence: 89%)
  Row 42:   date=2099-01-01 (confidence: 85%)
  Row 88:   amount=1000000 (confidence: 82%)
  Row 103:  discount=-50% (confidence: 81%)

ACTION REQUIRED
---------------
1. Review failed rows in the system
2. Correct missing values
3. Investigate anomalous records
4. Re-upload corrected file

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Need help? Contact: data-team@company.com
```

### Slack Alert Example

```
📊 Data Quality Alert

FAIL - sales_data.csv

Rows checked: 1,000
Rows failed: 234 (23.4%)

Validation Failures:
  • Missing Values: 150
  • Schema Mismatch: 50
  • Invalid Dates: 34

Anomalies: 47 detected

👉 View details: http://localhost:8501
```

### Discord Alert Example

```
[Yellow Embed]
Title: ⚠️ Data Quality Warning
Description: Anomalies detected in dataset

Fields:
  File: sales_data.csv
  Rows: 1,000
  Failed: 234 (23.4%)
  Anomalies: 47
  Confidence: 80%+

Color: #FFFF00 (Yellow)
```

## Alert Triggers

### 1. Validation Failure
Triggered when any validation check fails.
```yaml
triggers:
  validation_failure:
    enabled: true
    severity: "FAIL"
```

### 2. Anomaly Detection
Triggered when anomalies are found.
```yaml
triggers:
  anomaly_detected:
    enabled: true
    min_confidence: 0.8  # Only if confident
    min_count: 5         # Only if >5 found
```

### 3. High Failure Rate
Triggered when >20% of rows fail.
```yaml
triggers:
  high_failure_rate:
    enabled: true
    threshold: 0.20
    severity: "CRITICAL"
```

### 4. Schema Mismatch
Triggered when dataset structure doesn't match expected schema.
```yaml
triggers:
  schema_mismatch:
    enabled: true
    severity: "FAIL"
```

## Rate Limiting

Prevent alert spam:

```yaml
rate_limiting:
  enabled: true
  max_alerts_per_hour: 10
  min_interval_seconds: 300  # 5 minutes
```

**Example:**
- If >10 alerts in 1 hour → remaining alerts queued
- Minimum 5 minutes between alerts for same file

## Testing Alerts

### Test Email
```python
from dq.alert import AlertService

alert = AlertService.from_config('config/alert_config.yaml')
alert.test_email_connection()
```

### Test Slack
```python
alert.send_alert(
    file_name="test.csv",
    status="WARN",
    summary="Test alert message"
)
```

### Test Discord
```python
alert.send_to_discord({
    'title': 'Test Alert',
    'message': 'Discord webhook working!'
})
```

## Troubleshooting

### Issue: Emails not sending

**Solutions:**
1. Check `.env` file for `GMAIL_PASSWORD`
2. Verify app-specific password (not regular password)
3. Enable "Less secure apps" (temporary workaround)
4. Check SMTP logs: Set `debug: true` in config
5. Verify firewall/network allows SMTP port 587

### Issue: Slack connection fails

**Solutions:**
1. Verify webhook URL is correct (no extra spaces)
2. Test webhook: `curl -X POST -H 'Content-type: application/json' --data '{"text":"test"}' YOUR_WEBHOOK_URL`
3. Check webhook hasn't expired (regenerate if needed)
4. Verify network/firewall allows HTTPS

### Issue: Discord webhook not working

**Solutions:**
1. Regenerate webhook URL
2. Verify channel permissions for bot
3. Test with cURL before debugging code
4. Check message format is valid JSON

### Issue: Too many alerts

**Solutions:**
1. Increase `max_alerts_per_hour` threshold
2. Increase `min_interval_seconds`
3. Disable less critical triggers
4. Implement custom filtering

## Best Practices

1. **Use different channels for different severity**
   - CRITICAL → Email + Slack + Discord
   - WARN → Slack only
   - INFO → Discord only

2. **Set appropriate thresholds**
   - Don't alert on every small failure
   - Focus on important issues
   - Avoid "alert fatigue"

3. **Monitor alert system**
   - Check alert logs regularly
   - Verify emails/messages are reaching recipients
   - Track false positives

4. **Secure credentials**
   - Never commit `.env` to Git
   - Use environment variables
   - Rotate passwords regularly
   - Use app-specific passwords

## Support

Having issues? Check:
1. Configuration syntax (YAML format)
2. Environment variables set correctly
3. Webhook URLs valid and active
4. Network connectivity
5. Email/messaging provider logs
