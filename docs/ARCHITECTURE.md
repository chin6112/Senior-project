# Architecture Overview

## System Components

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────┐         ┌──────────────────────┐    │
│  │  Streamlit Dashboard │         │  FastAPI REST API    │    │
│  │   (app.py)           │         │  (api.py)            │    │
│  │                      │         │                      │    │
│  │  • File Upload       │         │  • POST /validate    │    │
│  │  • Config UI         │         │  • GET /history      │    │
│  │  • Results Display   │         │  • GET /anomaly/     │    │
│  │  • Alerts Setup      │         │    config            │    │
│  │                      │         │  • API Docs (Swagger)│    │
│  └──────────────────────┘         └──────────────────────┘    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
              │                            │
              └────────────┬───────────────┘
                           │
┌────────────────────────────────────────────────────────────────┐
│                      Service Layer                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │      ValidationService (dq/service.py)                │  │
│  │  • Orchestrates data quality pipeline                 │  │
│  │  • Coordinates validation checks                      │  │
│  │  • Triggers anomaly detection                         │  │
│  │  • Manages alerts                                     │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│          ┌────────────────┼────────────────┐                 │
│          │                │                │                 │
│          ▼                ▼                ▼                 │
│    ┌──────────┐    ┌────────────┐    ┌──────────┐           │
│    │  Engine  │    │  Anomaly   │    │  Alert   │           │
│    │  Checks  │    │ Detector   │    │ Service  │           │
│    │          │    │            │    │          │           │
│    └──────────┘    └────────────┘    └──────────┘           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
              │                   │              │
              │                   │              │
┌─────────────▼──────────────────▼─────────────▼─────────────────┐
│                      Storage Layer                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────┐  ┌──────────────────────────────┐  │
│  │  dq_history.db       │  │  anomaly_results.db          │  │
│  │  (SQLite)            │  │  (SQLite)                    │  │
│  │                      │  │                              │  │
│  │  • Runs table        │  │  • Anomaly records           │  │
│  │  • Rule results      │  │  • Detection methods         │  │
│  │  • Failure history   │  │  • Confidence scores         │  │
│  │  • Trend analysis    │  │  • Feature analysis          │  │
│  │                      │  │                              │  │
│  └──────────────────────┘  └──────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
              │                              │
              │                              │
┌─────────────▼──────────────────────────────▼──────────────────┐
│                    External Services                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────┐    ┌────────────┐    ┌────────────┐            │
│  │   Gmail  │    │   Slack    │    │  Discord   │            │
│  │  (SMTP)  │    │  (Webhook) │    │  (Webhook) │            │
│  └──────────┘    └────────────┘    └────────────┘            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Module Breakdown

### 1. Frontend Layer

#### `app.py` - Streamlit Dashboard
```
Responsibilities:
✓ File upload interface
✓ Real-time validation results display
✓ Anomaly detection configuration UI
✓ Alert system setup
✓ History and trend visualization
✓ Configuration management

Technology: Streamlit 1.57+
Port: 8501
```

#### `api.py` - FastAPI REST API
```
Responsibilities:
✓ Programmatic validation endpoint
✓ Batch processing support
✓ History retrieval
✓ Configuration management via API
✓ Swagger/OpenAPI documentation

Technology: FastAPI 0.100+
Port: 8000
Docs: /docs (Swagger), /redoc (ReDoc)
```

### 2. Service Layer

#### `dq/service.py` - ValidationService
```
Core Orchestrator

Main Methods:
├── __init__(config_path)
│   └── Load configuration, initialize DB
├── process_file(file_bytes, file_name)
│   ├── Parse CSV
│   ├── Run validation checks
│   ├── Detect anomalies
│   ├── Evaluate policy
│   ├── Send alerts
│   └── Save to history
├── get_history(limit)
│   └── Retrieve past validations
└── get_rule_trend(rule_name, limit)
    └── Analyze rule violation trends

Configuration: config/rules.yaml
Database: dq_history.db
```

#### `dq/engine.py` - Validation Engine
```
Validation Logic

Functions:
├── load_config(config_path)
│   └── Parse rules from YAML
├── run_checks(df, config)
│   ├── Check missing values
│   ├── Validate schema
│   ├── Check data types
│   ├── Run custom rules
│   └── Return failures DataFrame
└── [Custom validators]
    ├── check_missing_values()
    ├── check_schema_mismatch()
    ├── check_data_types()
    └── check_range_constraints()

Supported Rules:
• missing_values: Columns that must not be null
• schema: Expected columns and types
• data_type: Type validation
• range: Min/max value constraints
• pattern: Regex validation
• custom_rules: User-defined checks
```

#### `dq/anomaly.py` - AnomalyDetector
```
Machine Learning-based Anomaly Detection

Main Methods:
├── __init__(contamination=0.1)
│   └── Initialize Isolation Forest
├── detect(df)
│   ├── Clean and prepare data
│   ├── Run Isolation Forest
│   ├── Run IQR method
│   ├── Combine results
│   └── Return anomalies DataFrame
└── get_anomaly_report(anomalies)
    └── Format results for display

Algorithms:
✓ Isolation Forest (ML-based)
✓ IQR Method (Statistical)
✓ Optional Z-Score

Configuration: config/anomaly_config.yaml
Database: anomaly_results.db
```

#### `dq/alert.py` - AlertService
```
Automated Alert Notifications

Main Methods:
├── __init__(config_path)
│   └── Load alert configuration
├── send_alert(file_name, status, summary)
│   ├── Check alert triggers
│   ├── Format message
│   ├── Send via email
│   ├── Send via Slack
│   └── Send via Discord
├── test_email_connection()
│   └── Verify SMTP credentials
└── [Alert formatters]
    ├── format_email()
    ├── format_slack()
    └── format_discord()

Supported Channels:
✓ Email (Gmail SMTP)
✓ Slack (Webhooks)
✓ Discord (Webhooks)

Configuration: config/alert_config.yaml
```

### 3. Configuration Layer

#### `config/rules.yaml` - Validation Rules
```yaml
Defines:
✓ Expected columns and types
✓ Required fields (non-nullable)
✓ Value ranges
✓ Regex patterns
✓ Custom validation functions

Example:
validation_rules:
  missing_values:
    - customer_id
    - email
  schema:
    customer_id: int
    email: string
    amount: float
  ranges:
    amount: [0, 1000000]
```

#### `config/anomaly_config.yaml` - Anomaly Settings
```yaml
Defines:
✓ Detection methods (IF, IQR, Z-Score)
✓ Contamination rate
✓ Algorithm parameters
✓ Alert thresholds
✓ Sensitivity presets

Example:
isolation_forest:
  contamination: 0.1
  n_estimators: 100
alert_thresholds:
  anomaly_count: 50
  anomaly_rate: 0.15
```

#### `config/alert_config.yaml` - Alert Settings
```yaml
Defines:
✓ Email configuration (SMTP)
✓ Slack webhook URL
✓ Discord webhook URL
✓ Alert triggers and severity
✓ Rate limiting

Example:
email:
  enabled: true
  smtp_server: smtp.gmail.com
  recipients: [admin@example.com]
slack:
  enabled: false
  webhook_url: ${SLACK_WEBHOOK_URL}
```

### 4. Storage Layer

#### `dq_history.db` - Validation History
```
Tables:
├── runs
│   ├── run_id (PK)
│   ├── run_at (timestamp)
│   ├── file_name
│   ├── file_hash (sha256)
│   ├── dataset (CSV content hash)
│   ├── rows_checked
│   ├── rows_failed
│   ├── pass_rate
│   └── status (PASS/WARN/FAIL)
│
└── rule_results
    ├── run_id (FK)
    ├── rule (rule name)
    ├── severity
    └── failed_count
```

#### `anomaly_results.db` - Anomaly Records
```
Tables:
├── detections
│   ├── detection_id (PK)
│   ├── run_id (FK)
│   ├── row_id
│   ├── isolation_forest_score
│   ├── iqr_flag
│   ├── combined_score
│   └── confidence
│
└── affected_features
    ├── detection_id (FK)
    ├── feature_name
    └── feature_value
```

### 5. External Services

#### Email (Gmail SMTP)
```
Protocol: SMTP over TLS
Server: smtp.gmail.com:587
Authentication: App-specific password
Functionality:
✓ Send HTML-formatted alerts
✓ Include failure details
✓ Attach anomaly summaries
✓ Retry on failure
```

#### Slack Webhooks
```
Protocol: HTTP POST to Webhook URL
Format: Rich JSON messages
Functionality:
✓ Formatted text messages
✓ Color-coded status
✓ Thread replies
✓ File uploads
```

#### Discord Webhooks
```
Protocol: HTTP POST to Webhook URL
Format: Embeds with colors
Functionality:
✓ Rich embed messages
✓ Color-coded by severity
✓ User mentions
✓ File attachments
```

## Data Flow

### Typical Validation Process

```
User uploads CSV
       ↓
app.py receives file
       ↓
ValidationService.process_file()
       ├─→ Parse CSV
       ├─→ Compute file hash
       ├─→ engine.run_checks()
       │   └─→ Check rules against data
       │       └─→ Return failures DataFrame
       ├─→ AnomalyDetector.detect()
       │   ├─→ Run Isolation Forest
       │   ├─→ Run IQR method
       │   └─→ Return anomalies
       ├─→ AlertService.send_alert()
       │   ├─→ Email (if enabled)
       │   ├─→ Slack (if enabled)
       │   └─→ Discord (if enabled)
       └─→ Store in dq_history.db
       
       ↓
Return results to UI
       ├─→ Validation summary
       ├─→ Anomaly details
       └─→ Alert status
```

## Configuration Hierarchy

```
Default Config
     ↓
System env vars (override defaults)
     ↓
.env file (override system)
     ↓
YAML config files (override all)
     ↓
UI Configuration (runtime override)
```

## Error Handling

```
CSV Parse Error
├─→ Log error
├─→ Alert: Invalid file format
└─→ Return error to user

Validation Failure
├─→ Record failures
├─→ Check alert threshold
├─→ Send alert (if needed)
└─→ Save to history

Anomaly Detection Error
├─→ Log exception
├─→ Continue without anomalies
└─→ Note in results

Alert Send Failure
├─→ Retry up to 3 times
├─→ Log failure
└─→ Continue processing
```

## Scalability Considerations

### Current Design
- Single-threaded processing
- In-memory dataframes
- Local SQLite databases
- Suitable for files < 500MB

### For Scaling
1. **Large Files**
   - Use chunked processing
   - Stream CSV reading
   - Pandas' `chunksize` parameter

2. **High Volume**
   - Implement job queue (Celery)
   - Distribute across workers
   - Use cloud object storage

3. **Databases**
   - Migrate to PostgreSQL
   - Implement connection pooling
   - Add partitioning for large tables

4. **Alerts**
   - Implement message queue (RabbitMQ)
   - Batch alert processing
   - Add delivery confirmation

## Security Considerations

```
✓ Credentials in environment variables
✓ File hash validation (prevent duplicates)
✓ SQL injection prevention (parameterized queries)
✓ XSS protection in Streamlit (built-in)
✓ CORS configuration for API
✓ Rate limiting on API endpoints
✓ Input validation on all endpoints
✓ Secure credential handling (never log)
```
