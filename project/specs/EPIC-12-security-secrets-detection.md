# Epic 12: Security & Secrets Detection

**Status:** Not Started  
**Priority:** P0 - CRITICAL (Blocker for any serious adoption)  
**Estimated Effort:** 2 weeks  
**Dependencies:** None  
**Source:** Red Team Analysis (context/research/Red Team Analysis_ (REVISED) (1).md)

---

## Epic Goal

Prevent AI assistants from leaking secrets (passwords, API keys, PII, credentials) into git history through CHANGELOG and DEVLOG entries.

**Problem Statement:** AI assistants are literal and will document exactly what they see unless explicitly told not to. Without security rules and validation, the system becomes a "secrets-leaking machine" that creates SEV-1 security incidents.

**Inspiration:** Red Team Analysis identified this as "Critical Failure #1" - a disqualifying gap for enterprise and team adoption.

---

## Success Criteria

- [ ] AI rules explicitly forbid secrets in logs (passwords, API keys, PII, credentials)
- [ ] Pre-commit hook blocks commits containing detected secrets
- [ ] Security policy documented in SECURITY.md
- [ ] Redaction patterns provided for common secret formats
- [ ] AI assistants ask user before including potentially sensitive data
- [ ] Zero secrets leaked in test scenarios

---

## Task List

### Task 12.1: Add Security Rules to AI Assistant Rules
- [ ] Update `log-file-maintenance.md` with security section
- [ ] Add explicit "NEVER include" list (passwords, API keys, tokens, PII, etc.)
- [ ] Add redaction guidance (use placeholders, reference by name)
- [ ] Add pre-write security checklist for AI
- [ ] Update both starter packs with security rules

### Task 12.2: Create SECURITY.md Policy
- [ ] Create `product/SECURITY.md` with security policy
- [ ] Document what data should never be in logs
- [ ] Provide redaction examples
- [ ] Add incident response procedure (if secret is committed)
- [ ] Link to security rules in AI assistant documentation

### Task 12.3: Build Secrets Detection Script
- [ ] Create `product/scripts/detect-secrets.ps1` (PowerShell)
- [ ] Create `product/scripts/detect-secrets.sh` (Bash)
- [ ] Implement pattern matching for common secrets:
  - Passwords (password=, pwd=, pass:)
  - API keys (api_key=, apikey:, key:)
  - Tokens (token=, bearer, jwt)
  - Email addresses (PII)
  - IP addresses (infrastructure details)
  - Connection strings with credentials
- [ ] Return clear error messages with line numbers
- [ ] Provide fix suggestions (use <REDACTED>, reference by name)

### Task 12.4: Integrate with Pre-Commit Hook
- [ ] Update `.git-hooks/pre-commit` to run secrets detection
- [ ] Block commit if secrets detected
- [ ] Show clear error message with remediation steps
- [ ] Test with various secret patterns

### Task 12.5: Create Redaction Patterns Guide
- [ ] Create `product/docs/security-redaction-guide.md`
- [ ] Provide examples of safe vs. unsafe documentation
- [ ] Show redaction patterns for common scenarios:
  - Database connection strings
  - API authentication
  - Environment variables
  - Error messages with credentials
- [ ] Add to starter pack documentation

### Task 12.6: Add Security Validation Examples
- [ ] Create `product/examples/security/` directory
- [ ] Add example of UNSAFE DEVLOG entry (with secrets)
- [ ] Add example of SAFE DEVLOG entry (redacted)
- [ ] Add test cases for secrets detection script
- [ ] Document in validation guide

### Task 12.7: Update Starter Packs
- [ ] Add secrets detection scripts to both starter packs
- [ ] Update pre-commit hooks with secrets detection
- [ ] Update READMEs with security setup instructions
- [ ] Add SECURITY.md to both starter packs

### Task 12.8: Test Security System
- [ ] Test with real-world secret patterns
- [ ] Verify AI rules prevent secret inclusion
- [ ] Verify pre-commit hook blocks secrets
- [ ] Test redaction patterns
- [ ] Document test results

---

## Deliverables

1. **Security Rules:**
   - Updated `log-file-maintenance.md` with security section
   - Security rules in both starter packs

2. **Security Policy:**
   - `product/SECURITY.md`

3. **Detection Scripts:**
   - `product/scripts/detect-secrets.ps1`
   - `product/scripts/detect-secrets.sh`

4. **Documentation:**
   - `product/docs/security-redaction-guide.md`
   - Updated validation guide with security section

5. **Examples:**
   - `product/examples/security/` with safe/unsafe examples

6. **Starter Pack Integration:**
   - Scripts and hooks in both starter packs
   - Updated READMEs

---

## Technical Notes

### Secret Detection Patterns

**High-confidence patterns (block immediately):**
- `password\s*[:=]\s*[^\s]+`
- `api[_-]?key\s*[:=]\s*[A-Za-z0-9]{20,}`
- `token\s*[:=]\s*[A-Za-z0-9]{20,}`
- `bearer\s+[A-Za-z0-9\-._~+/]+=*`
- Email addresses in DEVLOG entries
- Connection strings with embedded credentials

**Medium-confidence patterns (warn, ask user):**
- IP addresses (could be examples or real infrastructure)
- Environment variable values (could be safe or sensitive)
- Error messages (could contain credentials)

### Redaction Examples

**UNSAFE:**
```md
**The Problem:** Database connection failing with error: 
`postgresql://admin:P@ssw0rd123@prod-db.example.com:5432/app`
```

**SAFE:**
```md
**The Problem:** Database connection failing. Root cause: Invalid credentials 
in connection string (see vault: `DB_PROD_CREDENTIALS`).
```

---

## Testing Strategy

1. **Pattern Testing:** Test detection script with 50+ real-world secret patterns
2. **AI Rule Testing:** Verify AI assistants follow security rules in practice
3. **Integration Testing:** Test pre-commit hook blocks secrets
4. **False Positive Testing:** Ensure legitimate content isn't blocked
5. **User Testing:** Have developers test with real projects

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positives block legitimate commits | High | Provide clear override mechanism, improve patterns |
| AI assistants ignore security rules | Critical | Add validation, test extensively, improve rule clarity |
| Secrets detection misses new patterns | Medium | Regular pattern updates, community contributions |
| Users disable security checks | Medium | Make it easy to use, show value, educate on risks |

---

## Dependencies

- Epic 7 (Verification System) - Pre-commit hooks already exist
- Epic 13 (Validation) - Security validation integrates with overall validation

---

## Notes

**Why This is P0 Critical:**

From Red Team Analysis:
> "This tool is a **secrets-leaking machine**. It encourages detailed narrative logs written by AI agents that don't understand data classification. **Banned.**"

Without this epic, Log File Genius cannot be used safely in any professional environment. This is the #1 blocker for adoption.

**Target Users:**
- Solo developers working on real projects (not just demos)
- Teams with security policies
- Anyone who can't afford a SEV-1 security incident

**Success Metric:**
Zero secrets leaked in 100 test commits with AI assistants.

