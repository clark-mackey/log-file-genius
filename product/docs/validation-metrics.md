# Validation Metrics Guide

**Version:** 1.0  
**Last Updated:** 2025-11-10

---

## Overview

This guide explains the validation metrics tracked by Log File Genius and how to interpret them for improving your documentation quality.

---

## Key Metrics

### 1. Health Score (0-100)

**What it measures:** Overall quality of your log files

**Calculation:**
- Start at 100 points
- Deduct 20 points per error
- Deduct 5 points per warning

**Interpretation:**
- **90-100:** 🟢 Excellent - Keep up the good work!
- **70-89:** 🟡 Good - Minor improvements needed
- **50-69:** 🟠 Needs Attention - Address warnings and errors
- **0-49:** 🔴 Critical - Immediate action required

**Example:**
```
Health Score: 85/100 🟡 Good
- 0 errors
- 3 warnings
```

### 2. Token Budget Status

**What it measures:** How close you are to token limits

**Tracked for:**
- CHANGELOG.md (target: 10,000 tokens)
- DEVLOG.md (target: 15,000 tokens)
- Combined (target: 25,000 tokens)

**Interpretation:**
- **0-60%:** 🟢 Healthy - Plenty of room
- **60-80%:** 🟡 Approaching limit - Plan archival soon
- **80-90%:** 🟠 Near limit - Archive old entries
- **90-100%:** 🔴 At limit - Archive immediately

**Example:**
```
CHANGELOG: 7,500 / 10,000 tokens (75%) 🟡
DEVLOG: 12,000 / 15,000 tokens (80%) 🟠
Combined: 19,500 / 25,000 tokens (78%) 🟡
```

### 3. Validation Pass Rate

**What it measures:** Percentage of commits that pass validation on first try

**Target:** 95%+ pass rate

**How to track:**
```bash
# Run validation report regularly
python product/scripts/validation-report.py --history
```

**Improving pass rate:**
1. Use pre-commit hooks to catch errors early
2. Review validation guide regularly
3. Use AI self-assessment checklist
4. Run validation before committing

### 4. Common Validation Errors

**What it tracks:** Most frequent validation issues

**Top errors to watch for:**
1. Missing commit hash in CHANGELOG entries
2. Missing "Files:" section in CHANGELOG
3. Missing period before "Files:"
4. Commit hash too short (< 7 characters)
5. Missing "Current Context" in DEVLOG
6. Token budget exceeded

**How to reduce errors:**
- Use templates from `product/templates/`
- Enable AI rules for automatic compliance
- Review examples in `product/examples/validation/`

### 5. Time to Fix Validation Errors

**What it measures:** How long it takes to fix validation issues

**Target:** < 5 minutes per error

**Improving fix time:**
1. Read error messages carefully - they include suggestions
2. Use validation examples as reference
3. Keep validation guide bookmarked
4. Use `--json` output for programmatic fixes

---

## Tracking Metrics Over Time

### Manual Tracking

Create a metrics log file:

```bash
# Append validation results to metrics log
python product/scripts/validation-report.py --json >> logs/metrics/validation-history.jsonl
```

### Automated Tracking (GitHub Actions)

The GitHub Actions workflow automatically tracks:
- Validation results for every PR
- Health scores over time
- Token budget trends

View in:
- PR comments
- GitHub Actions artifacts
- Job summaries

---

## Metrics Dashboard (Optional)

For teams wanting visual metrics, you can:

1. **Export metrics to CSV:**
```python
# Custom script to parse validation-history.jsonl
import json
import csv

with open('logs/metrics/validation-history.jsonl') as f:
    data = [json.loads(line) for line in f]

with open('metrics.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'health_score', 'errors', 'warnings'])
    writer.writeheader()
    for entry in data:
        writer.writerow({
            'timestamp': entry['timestamp'],
            'health_score': entry['health_score'],
            'errors': sum(r['errors'] for r in entry['validation_results']['results']),
            'warnings': sum(r['warnings'] for r in entry['validation_results']['results'])
        })
```

2. **Visualize in spreadsheet:**
- Import `metrics.csv` into Excel/Google Sheets
- Create line charts for health score trends
- Create bar charts for error/warning counts

3. **Use GitHub Insights:**
- View validation workflow runs
- Track success/failure rates
- Monitor trends over time

---

## Success Criteria

**Your validation system is working well if:**

✅ Health score consistently above 90  
✅ Validation pass rate above 95%  
✅ Token budgets stay below 80%  
✅ Errors fixed within 5 minutes  
✅ No validation failures in production  

**Red flags:**

🚩 Health score below 70 for multiple commits  
🚩 Validation pass rate below 80%  
🚩 Token budgets consistently above 90%  
🚩 Same errors recurring frequently  
🚩 Validation bypassed with `--no-verify`  

---

## Best Practices

1. **Review metrics weekly:** Check health scores and token budgets
2. **Archive proactively:** Don't wait until you hit token limits
3. **Fix errors immediately:** Don't let them accumulate
4. **Track trends:** Look for patterns in validation failures
5. **Share metrics:** Keep team informed of documentation health

---

## Example Metrics Report

```
=== Weekly Validation Metrics ===

Period: 2025-11-03 to 2025-11-10
Commits: 47

Health Score:
- Average: 92/100 🟢
- Lowest: 75/100 (2025-11-05)
- Current: 95/100 🟢

Validation Pass Rate: 96% (45/47) ✅

Token Budget:
- CHANGELOG: 8,200 / 10,000 (82%) 🟠
- DEVLOG: 11,500 / 15,000 (77%) 🟡
- Combined: 19,700 / 25,000 (79%) 🟡

Common Errors:
1. Missing commit hash (3 occurrences)
2. Commit hash too short (2 occurrences)

Recommendations:
- Archive CHANGELOG entries older than 2 weeks
- Review commit hash format in AI rules
```

---

## Related Documentation

- [Validation Guide](validation-guide.md) - How to run validation
- [Archival Guide](archival-guide.md) - How to archive old entries
- [Profile Selection Guide](profile-selection-guide.md) - Customize token targets

---

## Questions?

If you have questions about validation metrics:
1. Review this guide
2. Check [validation examples](../examples/validation/)
3. Open an issue on GitHub

