# REST API Documentation

## Overview
FastAPI-based REST API for data quality validation and anomaly detection.

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required (can be added in production)

## Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### 2. Validate File
**POST** `/validate`

Upload and validate a CSV file for data quality issues and anomalies.

**Request:**
- Form parameter: `file` (multipart/form-data)
  - Accepted formats: CSV
  - Max size: 50MB

**Response:**
```json
{
  "file_name": "data.csv",
  "rows_checked": 1000,
  "rows_failed": 42,
  "pass_rate": 95.8,
  "status": "WARN",
  "timestamp": "2026-11-16T21:15:32.789+07:00",
  "validation_results": {
    "missing_values": 10,
    "schema_mismatch": 5,
    "outliers": 27
  },
  "anomalies_detected": [
    {
      "row_id": 5,
      "anomaly_type": "isolation_forest",
      "confidence": 0.95,
      "values": {"column1": 999.99}
    }
  ],
  "alerts_sent": ["email@example.com"],
  "recommendations": [...]
}
```

**Status Codes:**
- `200 OK` - Validation successful
- `400 Bad Request` - Invalid file format
- `422 Unprocessable Entity` - File processing error

---

### 3. Get Validation History
**GET** `/history`

Retrieve past validation results.

**Query Parameters:**
- `limit` (optional, default: 10) - Number of recent results to return
- `file_name` (optional) - Filter by filename

**Response:**
```json
{
  "results": [
    {
      "run_id": 123,
      "file_name": "data.csv",
      "run_at": "2026-11-16T21:15:32",
      "rows_checked": 1000,
      "pass_rate": 95.8,
      "status": "WARN"
    }
  ],
  "total_count": 50
}
```

---

### 4. Get Rule Trend
**GET** `/rule-trend/{rule_name}`

Get violation trend for a specific rule.

**Path Parameters:**
- `rule_name` - Name of the validation rule

**Query Parameters:**
- `limit` (optional, default: 30) - Number of historical points

**Response:**
```json
{
  "rule_name": "missing_values",
  "trend": [
    {
      "run_id": 120,
      "run_at": "2026-11-16T20:00:00",
      "failed_count": 5
    },
    {
      "run_id": 121,
      "run_at": "2026-11-16T21:00:00",
      "failed_count": 8
    }
  ]
}
```

---

### 5. Anomaly Detection Settings
**GET** `/anomaly/config`

Get current anomaly detection configuration.

**Response:**
```json
{
  "contamination_rate": 0.1,
  "enabled_methods": ["isolation_forest", "iqr"],
  "sensitivity": "medium"
}
```

**PUT** `/anomaly/config`

Update anomaly detection settings.

**Request Body:**
```json
{
  "contamination_rate": 0.15,
  "sensitivity": "high"
}
```

---

### 6. Alert Configuration
**GET** `/alerts/config`

Get current alert configuration.

**Response:**
```json
{
  "email": {
    "enabled": true,
    "recipients": ["admin@example.com"],
    "threshold": "WARN"
  },
  "slack": {
    "enabled": false,
    "webhook_url": "***",
    "threshold": "FAIL"
  },
  "discord": {
    "enabled": false,
    "webhook_url": "***",
    "threshold": "FAIL"
  }
}
```

**PUT** `/alerts/config`

Update alert settings.

---

### 7. Clear History
**DELETE** `/history`

Clear all validation history (use with caution).

**Response:**
```json
{
  "deleted_records": 150,
  "status": "success"
}
```

---

## Error Handling

All errors follow standard HTTP status codes:

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request / Invalid input |
| 404 | Resource not found |
| 422 | Unprocessable entity |
| 500 | Internal server error |

**Error Response Format:**
```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-11-16T21:15:32"
}
```

---

## Usage Examples

### Python
```python
import requests

# Validate a file
with open('data.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/validate',
        files={'file': f}
    )
    print(response.json())

# Get history
response = requests.get(
  'http://localhost:8000/history?limit=20'
)
print(response.json())
```

### cURL
```bash
# Validate file
curl -X POST -F "file=@data.csv" http://localhost:8000/validate

# Get history
curl http://localhost:8000/history?limit=20

# Health check
curl http://localhost:8000/health
```

### JavaScript/Node.js
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const formData = new FormData();
formData.append('file', fs.createReadStream('data.csv'));

axios.post('http://localhost:8000/validate', formData, {
  headers: formData.getHeaders()
})
.then(res => console.log(res.data))
.catch(err => console.error(err));
```

---

## Interactive API Documentation

Swagger UI available at: `http://localhost:8000/docs`
ReDoc available at: `http://localhost:8000/redoc`
