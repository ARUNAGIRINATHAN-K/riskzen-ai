# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in RiskZen, **please do not open a public GitHub issue.**

Instead, please report it responsibly by emailing:

**security@riskzen.ai** (or submit a GitHub Security Advisory)

Include the following in your report:

- A description of the vulnerability.
- Steps to reproduce the issue.
- The potential impact.
- Any suggested fix (if you have one).

### Response Timeline

| Action | Target |
|---|---|
| Acknowledgment of report | Within 48 hours |
| Initial assessment | Within 5 business days |
| Fix or mitigation plan | Within 15 business days |
| Public disclosure (if applicable) | After fix is deployed |

We will credit reporters in the changelog unless they prefer to remain anonymous.

---

## Supported Versions

| Version | Supported |
|---|---|
| Latest release on `main` | ✅ |
| Older releases | ❌ |

Only the latest release receives security updates.

---

## Security Design

RiskZen is designed with the following security principles:

### Credential Management

- All secrets (API tokens, database passwords, encryption keys) are stored in environment variables, never in source code.
- GitHub tokens stored in the database are encrypted at rest using Fernet symmetric encryption.

### Data Privacy

- The system collects only project-level data required for risk detection.
- No private messages, browsing activity, keystrokes, or personal communications are collected.
- The system explicitly does not evaluate individual employee performance.
- LLM prompts contain only project metadata (task titles, statuses, dates, dependencies), never personal employee data.

### API Security

- All API inputs are validated using Pydantic schemas.
- SQL injection is prevented through SQLAlchemy parameterized queries.
- File uploads (CSV) are validated for content type and parsed safely.

### Infrastructure

- Docker containers run as non-root users.
- Internal services (PostgreSQL, Ollama) are not exposed to the host network in production configurations.

### Audit Trail

- All risk-related decisions (detections, recommendations, approvals, dismissals, actions) are recorded in an immutable audit log.

---

## Known Limitations

The following are known security limitations in the current MVP:

- **Authentication:** The MVP uses simple API-key authentication. Enterprise authentication (OAuth, SSO) is planned for future versions.
- **Authorization:** The MVP is a single-user system. Role-based access control (RBAC) is planned for future versions.
- **Encryption in transit:** HTTPS is expected to be handled by a reverse proxy in production. The application itself does not terminate TLS.

---

## Dependencies

We monitor dependencies for known vulnerabilities using:

- `pip audit` for Python dependencies.
- `npm audit` for Node.js dependencies.

If you notice a vulnerable dependency, please report it using the process above.
