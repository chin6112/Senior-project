# Anomaly Detection Guide

## Overview
The Data Quality system includes advanced anomaly detection using multiple machine learning methods to identify unusual patterns and outliers in your data.

## What is Anomaly Detection?

Anomaly detection automatically identifies data points that deviate significantly from normal patterns. It helps you catch:
- **Outliers**: Extreme values that don't fit the normal distribution
- **Data entry errors**: Typos, wrong units, or incorrect values
- **Fraudulent records**: Suspicious patterns in transactions
- **System anomalies**: Unusual behavior or processing errors

## Detection Methods

### 1. Isolation Forest
**Method:** Machine Learning-based isolation
**Best for:** Complex multivariate patterns, non-linear relationships

```
Principle: Random trees isolate anomalies faster than normal points
Advantages:
  ✓ Works with high-dimensional data
  ✓ Handles mixed data types well
  ✓ Fast and scalable
  ✓ No need to define normal behavior first
```

**Configuration:**
```yaml
isolation_forest:
  enabled: true
  contamination: 0.1  # Expected % of anomalies (0-1)
  random_state: 42
  n_estimators: 100
```

### 2. Interquartile Range (IQR)
**Method:** Statistical quartile-based detection
**Best for:** Univariate outliers, quick detection

```
Principle: Identify values outside Q1 ± 1.5×IQR
Advantages:
  ✓ Simple and interpretable
  ✓ No machine learning needed
  ✓ Fast computation
  ✓ Good for numeric columns
```

**Configuration:**
```yaml
iqr:
  enabled: true
  multiplier: 1.5  # IQR threshold multiplier
  per_column: true  # Apply per column vs globally
```

### 3. Z-Score (Optional)
**Method:** Standard deviation-based detection
**Best for:** Normally distributed data

```
Principle: Mark points with |z-score| > threshold
Threshold typically 2.5-3 (2.5σ ≈ 98.8% of normal data)
```

## Configuration

### File: `config/anomaly_config.yaml`

```yaml
anomaly_detection:
  # Main settings
  enabled: true
  methods:
    - isolation_forest
    - iqr
  
  # Isolation Forest parameters
  isolation_forest:
    enabled: true
    contamination: 0.1      # 10% expected anomalies
    random_state: 42
    n_estimators: 100       # Number of trees
    max_samples: auto       # Max samples per tree
    max_features: 1.0       # Feature sampling ratio
  
  # IQR parameters
  iqr:
    enabled: true
    multiplier: 1.5         # Standard is 1.5
    per_column: true        # True = per column, False = global
  
  # Z-Score parameters
  zscore:
    enabled: false
    threshold: 2.5          # Number of std deviations
  
  # Filtering options
  filters:
    exclude_missing: true   # Don't flag NaN as anomaly
    numeric_only: false     # Apply to all vs only numeric
    min_records: 10         # Skip if fewer than N records
  
  # Output settings
  output:
    include_scores: true    # Include anomaly scores
    sort_by: score          # Sort: score, row_id, feature_count
    limit: null             # Max anomalies to report (null = all)

# Alert thresholds
alert_thresholds:
  anomaly_count: 50         # Alert if >50 anomalies found
  anomaly_rate: 0.15        # Alert if >15% are anomalies
  confidence_threshold: 0.8 # Only report confident anomalies

# Sensitivity levels (presets)
sensitivity_presets:
  low:
    contamination: 0.05
    iqr_multiplier: 2.0
    zscore_threshold: 3.0
  medium:
    contamination: 0.10
    iqr_multiplier: 1.5
    zscore_threshold: 2.5
  high:
    contamination: 0.20
    iqr_multiplier: 1.0
    zscore_threshold: 2.0
```

## UI Controls

### Streamlit Dashboard

Located in the **Anomaly Detection** tab:

```
┌─────────────────────────────────────────┐
│ Anomaly Detection Settings              │
├─────────────────────────────────────────┤
│                                         │
│ Contamination Rate (Sensitivity)   [🔘] │
│ ◄────●────────────────────────► 0.1    │
│ Expected % of anomalies in dataset      │
│                                         │
│ Detection Methods:                      │
│ ☑ Isolation Forest (ML-based)          │
│ ☑ IQR Method (Statistical)             │
│                                         │
│ [Update Configuration]                 │
│ [Run Detection]                        │
│                                         │
└─────────────────────────────────────────┘
```

**Controls Explained:**

- **Contamination Rate Slider**
  - **0.05 (Low)**: Very strict, few false positives
  - **0.10 (Medium)**: Balanced sensitivity
  - **0.20 (High)**: Sensitive, may catch more false positives

- **Detection Methods**
  - Enable/disable individual methods
  - Multiple methods = cross-validation

## Understanding Results

### Result Table Columns

| Column | Meaning |
|--------|---------|
| `row_id` | Row number in dataset |
| `isolation_forest` | Anomaly score (0-1, >0.5 = anomaly) |
| `iqr_method` | Whether flagged by IQR (True/False) |
| `combined_score` | Average score across methods |
| `anomaly_count` | Number of anomalous features |
| `affected_columns` | Which columns triggered anomaly |

### Example Output

```
Row ID  | Isolation Forest | IQR | Combined | Features
--------|------------------|-----|----------|------------------
5       | 0.92             | Yes | 0.96     | price, quantity
17      | 0.78             | Yes | 0.89     | date, amount
42      | 0.65             | No  | 0.65     | value
```

**Interpretation:**
- Row 5: **High confidence anomaly** (96% score, confirmed by IQR)
- Row 17: **Likely anomaly** (89% score, confirmed by IQR)
- Row 42: **Possible anomaly** (65% score, single method only)

## Best Practices

### 1. Tuning Contamination Rate

```
Start with: 0.1 (10%)
├─ If too many false positives → Lower to 0.05
└─ If missing real anomalies → Raise to 0.15-0.20
```

### 2. Combining Methods

```
✓ Isolation Forest + IQR = Good balance
  - Catches complex patterns (IF)
  - Plus obvious outliers (IQR)

✓ Enable multiple methods
  - Cross-validation of results
  - Increase confidence
```

### 3. Data Preparation

```
Before anomaly detection:
1. Handle missing values
2. Normalize numeric columns (optional)
3. Encode categorical columns
4. Remove duplicates
5. Filter time-sensitive data appropriately
```

### 4. Reviewing Results

```
✓ Check affected_columns
  - Understand why flagged as anomaly
  - Verify domain-specific context

✓ Inspect row_id directly
  - Look at original values
  - Determine if real issue or false positive

✓ Group by severity
  - Confidence > 0.9: Investigate first
  - 0.7-0.9: Review for patterns
  - < 0.7: Consider as edge cases
```

## Common Issues

### Issue: Too Many False Positives

**Solutions:**
1. Lower contamination rate (0.05-0.08)
2. Increase IQR multiplier (2.0-2.5)
3. Filter data first (remove obvious outliers)
4. Increase min_records threshold

### Issue: Missing Real Anomalies

**Solutions:**
1. Raise contamination rate (0.15-0.20)
2. Lower IQR multiplier (1.0-1.2)
3. Use multiple methods
4. Check data preprocessing

### Issue: Slow Processing

**Solutions:**
1. Reduce dataset size
2. Disable unnecessary methods
3. Increase max_samples limit
4. Use only Isolation Forest (faster)

## Advanced: Custom Scoring

Anomaly scores combine multiple methods:

```python
combined_score = (
    isolation_forest_score * 0.6 +  # Weight: 60%
    iqr_binary * 0.4                 # Weight: 40%
)
```

Adjust weights in code for your use case:
```python
# In dq/anomaly.py
IF_WEIGHT = 0.6
IQR_WEIGHT = 0.4
```

## Integration with Alerts

Anomalies trigger alerts based on:

```yaml
alert_thresholds:
  anomaly_count: 50      # Alert if >50 found
  anomaly_rate: 0.15     # Alert if >15% are anomalies
  confidence_threshold: 0.8  # Only report confident ones
```

**Alert Example:**
```
Subject: 🚨 Data Quality Alert: Anomalies Detected

Dataset: sales_data.csv
Rows Analyzed: 1,000
Anomalies Found: 47 (4.7%)

Top Anomalies:
- Row 5: price=999.99 (confidence: 96%)
- Row 17: quantity=-100 (confidence: 89%)
- Row 42: date=2099-01-01 (confidence: 85%)

Action: Review these records immediately.
```

## Learning More

- **Isolation Forest Paper**: Liu et al. (2008)
- **Interquartile Range**: Standard statistical method
- **Anomaly Detection Survey**: Goldstein & Uchida (2016)

## Support

For issues or questions:
1. Check configuration file syntax
2. Verify data format and content
3. Review logs in SQLite database
4. Enable debug logging in anomaly.py
