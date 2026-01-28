# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| 2.0.x   | :x:                |
| < 2.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Caesar Cipher Breaker, please report it responsibly:

### What qualifies as a security issue?

- Remote code execution vulnerabilities
- Authentication or authorization bypass
- Data exposure or privacy concerns
- Denial of service attacks
- Dependency vulnerabilities with known exploits

### How to report

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead:
1. Email the maintainer directly (check README for contact)
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)

### What to expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 1-4 weeks
  - Medium: 1-3 months
  - Low: Best effort

### Disclosure Policy

- We will coordinate disclosure with you
- We prefer coordinated disclosure after a fix is available
- We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices for Users

1. **Keep Updated**: Always use the latest version
2. **Verify Downloads**: Only download from official sources
3. **Check Dependencies**: Run `pip list` to audit installed packages
4. **Report Issues**: If you see something suspicious, report it

## Out of Scope

The following are generally out of scope:
- Cipher algorithm weaknesses (this is educational software)
- Social engineering attacks
- Physical access attacks
- Issues in dependencies (report to the dependency maintainers)

Thank you for helping keep Caesar Cipher Breaker secure!
