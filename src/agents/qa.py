"""
QA Agent - Quality assurance and specification review.
Generates comprehensive QA reports with security, performance, and consistency checks.
"""

from typing import List, Dict
import re

from src.agents.base import BaseAgent, AgentError
from src.schemas import QAReport, QAIssue, extract_json_object


class QAAgent(BaseAgent):
    """
    Quality Assurance agent responsible for:
    - Security vulnerability detection
    - Performance issue identification
    - Consistency checking between specs
    - Edge case identification
    - Best practice compliance
    """
    
    def __init__(self):
        super().__init__(playbook_name="qa")
    
    def get_agent_name(self) -> str:
        return "QAAgent"
    
    def analyze_specifications(
        self,
        backend_spec: str,
        frontend_spec: str,
        architecture: str,
        user_stories: List[dict]
    ) -> QAReport:
        """
        Phase 5: Analyze all specifications for issues.
        
        Args:
            backend_spec: Backend specification
            frontend_spec: Frontend specification
            architecture: Architecture document
            user_stories: List of user story dicts
        
        Returns:
            QAReport with categorized issues
        """
        self.log("Analyzing specifications for quality issues")
        
        base_system = """You are a senior QA engineer and security analyst performing thorough specification review.

## ISSUE CATEGORIES

1. **CRITICAL** (System crash, data loss, security breach):
   - SQL injection vulnerabilities
   - Authentication bypass
   - Data exposure
   - Missing critical error handling

2. **HIGH** (Major functionality broken, significant security risk):
   - Missing input validation
   - Broken API contracts
   - Race conditions
   - Insufficient authorization

3. **MEDIUM** (Degraded UX, minor security concern):
   - Missing loading states
   - Poor error messages
   - Missing pagination
   - Inconsistent naming

4. **LOW** (Cosmetic, optimization):
   - Code style issues
   - Missing documentation
   - Optimization opportunities

5. **SECURITY FLAGS**:
   - Any potential security weakness
   - Missing security headers
   - Credential handling issues

## EDGE CASE SIMULATION
You MUST analyze these edge cases and report issues:

### Load/Stress Scenarios
- What happens if 10,000 requests hit the API in 1 second? (DDoS simulation)
- What if 1,000 users log in simultaneously?
- What if a user submits a 100MB file when the limit is 25MB?
- What if the database connection pool is exhausted?

### Boundary Conditions
- Empty arrays/strings in API requests
- Maximum length inputs (e.g., 10,000 character name field)
- Unicode/emoji in text fields
- Negative numbers where positive expected
- Dates in the past/far future
- Timezone edge cases (DST transitions)

### Concurrent Operations
- Two users editing the same resource simultaneously
- Payment submitted twice in quick succession (double-charge risk)
- Session accessed from two devices at once
- Cache invalidation during high write volume

### Failure Modes
- Third-party API timeout (payment gateway, email service)
- Database failover during transaction
- Network partition between services
- Disk full during file upload

## ATTACK VECTOR ANALYSIS
Consider these attack patterns:

- **Injection Attacks**: SQL, NoSQL, Command, LDAP, XPath
- **Broken Authentication**: Credential stuffing, session fixation, token theft
- **Sensitive Data Exposure**: PII in logs, unencrypted storage, error message leakage
- **XML/JSON Attacks**: XXE, billion laughs, deeply nested payloads
- **Broken Access Control**: IDOR, privilege escalation, path traversal
- **Security Misconfiguration**: Default credentials, verbose errors, missing headers
- **XSS/CSRF**: Stored/reflected XSS, missing CSRF tokens
- **Insecure Deserialization**: Object injection, RCE via deserialization
- **Component Vulnerabilities**: Outdated dependencies with known CVEs

Be thorough. Flag missing mitigations even if not explicitly vulnerable.

## OWASP TOP 10 MAPPING
For each security issue found, map it to the relevant OWASP category:
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable & Outdated Components
- A07: Identification & Authentication Failures
- A08: Software & Data Integrity Failures
- A09: Security Logging & Monitoring Failures
- A10: Server-Side Request Forgery (SSRF)

Add the OWASP code in brackets next to each security_flag, e.g. "Missing CSRF token on payment form [A01]"

## ATTACK CHAIN ANALYSIS
For the TWO most dangerous issues you find, trace the full exploit chain:
  Entry point → vulnerability exploited → lateral movement → final impact
Example: "Public file upload → no MIME check → .php RCE → full server compromise"
Include this in the issue description for CRITICAL/HIGH items."""

        system_prompt = self.build_system_prompt(base_system)
        
        # Summarize user stories
        stories_summary = "\n".join([
            f"- {s.get('id', 'US-XXX')}: {s.get('title', 'Unknown')}"
            for s in user_stories[:10]
        ])
        
        user_prompt = f"""Analyze these MVP specifications for quality issues:

## Architecture
{architecture[:4000]}

## Backend Specification
{backend_spec[:4000]}

## Frontend Specification
{frontend_spec[:4000]}

## User Stories Being Implemented
{stories_summary}

Return JSON with your findings:
{{
    "critical": [
        {{"id": "C-001", "desc": "Description of critical issue", "location": "Backend/API/auth"}}
    ],
    "high": [
        {{"id": "H-001", "desc": "Description of high issue", "location": "Frontend/Login"}}
    ],
    "medium": [
        {{"id": "M-001", "desc": "Description of medium issue", "location": "Backend/Models"}}
    ],
    "low": [
        {{"id": "L-001", "desc": "Description of low issue", "location": "General"}}
    ],
    "security_flags": [
        "Any security concern to flag"
    ]
}}

Be thorough but realistic. Include location for each issue."""

        try:
            response = self.call_llm(system_prompt, user_prompt, temperature=0.3, max_tokens=4000)
            
            # Parse response
            report = self._parse_qa_response(response)
            
            total_issues = (
                len(report.critical) + 
                len(report.high) + 
                len(report.medium) + 
                len(report.low)
            )
            self.log(f"QA analysis complete: {total_issues} issues found ({len(report.critical)} critical)")
            
            return report
            
        except AgentError as e:
            self.log(f"QA analysis failed (API/network): {e}", "ERROR")
            return self._fallback_qa_report()
        except Exception:
            raise  # Let programming bugs surface
    
    def _parse_qa_response(self, response: str) -> QAReport:
        """Parse LLM response into QAReport."""
        data = extract_json_object(response)
        if data:
            return QAReport(
                critical=self._parse_issues(data.get('critical', [])),
                high=self._parse_issues(data.get('high', [])),
                medium=self._parse_issues(data.get('medium', [])),
                low=self._parse_issues(data.get('low', [])),
                security_flags=self._parse_security_flags(data.get('security_flags', []))
            )

        # Fallback: try to extract issues from text
        self.log("JSON parsing failed, using text extraction", "WARNING")
        return self._extract_issues_from_text(response)
    
    def _parse_issues(self, issues_data: list) -> List[QAIssue]:
        """Parse issue dicts into QAIssue objects."""
        issues = []
        for i, item in enumerate(issues_data):
            if isinstance(item, dict):
                issues.append(QAIssue(
                    id=item.get('id', f'I-{i+1:03d}'),
                    desc=item.get('desc', item.get('description', 'No description')),
                    location=item.get('location', 'Unspecified')
                ))
            elif isinstance(item, str):
                issues.append(QAIssue(
                    id=f'I-{i+1:03d}',
                    desc=item,
                    location='Unspecified'
                ))
        return issues
    
    def _parse_security_flags(self, flags_data: list) -> List[str]:
        """Normalise security_flags — LLM may return strings or dicts."""
        result = []
        for item in flags_data:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                # Build a readable string from whatever keys the LLM chose
                desc = item.get('desc') or item.get('description') or item.get('flag') or ''
                location = item.get('location') or item.get('endpoint') or item.get('id') or ''
                parts = [p for p in (desc, location) if p]
                result.append(' — '.join(parts) if parts else str(item))
        return result
    
    def _extract_issues_from_text(self, text: str) -> QAReport:
        """Extract issues from unstructured text."""
        critical = []
        high = []
        medium = []
        low = []
        security = []
        
        lines = text.split('\n')
        current_category = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect category headers
            if 'critical' in line_lower:
                current_category = 'critical'
            elif 'high' in line_lower:
                current_category = 'high'
            elif 'medium' in line_lower:
                current_category = 'medium'
            elif 'low' in line_lower:
                current_category = 'low'
            elif 'security' in line_lower:
                current_category = 'security'
            
            # Extract issue from bullet points
            elif line.strip().startswith(('-', '*', '•')):
                issue_text = line.strip().lstrip('-*• ')
                if issue_text and len(issue_text) > 10:
                    issue = QAIssue(
                        id=f"QA-{len(critical)+len(high)+len(medium)+len(low)+1:03d}",
                        desc=issue_text[:200],
                        location="Extracted from text"
                    )
                    
                    if current_category == 'critical':
                        critical.append(issue)
                    elif current_category == 'high':
                        high.append(issue)
                    elif current_category == 'medium':
                        medium.append(issue)
                    elif current_category == 'low':
                        low.append(issue)
                    elif current_category == 'security':
                        security.append(issue_text)
        
        return QAReport(
            critical=critical,
            high=high,
            medium=medium,
            low=low,
            security_flags=security
        )
    
    def _fallback_qa_report(self) -> QAReport:
        """Generate minimal QA report when analysis fails."""
        return QAReport(
            critical=[],
            high=[
                QAIssue(
                    id="H-001",
                    desc="QA analysis could not be completed - manual review required",
                    location="General"
                )
            ],
            medium=[],
            low=[],
            security_flags=["Manual security review recommended"]
        )
    
    def format_qa_report_markdown(self, report: QAReport) -> str:
        """Format QA report as Markdown document."""
        total = (
            len(report.critical) + 
            len(report.high) + 
            len(report.medium) + 
            len(report.low)
        )
        
        lines = [
            "# QA Report\n",
            f"*Total issues found: {total}*\n",
            f"- 🔴 Critical: {len(report.critical)}",
            f"- 🟠 High: {len(report.high)}",
            f"- 🟡 Medium: {len(report.medium)}",
            f"- 🟢 Low: {len(report.low)}",
            f"- 🔒 Security Flags: {len(report.security_flags)}\n"
        ]
        
        # Critical issues
        if report.critical:
            lines.append("\n## 🔴 Critical Issues\n")
            lines.append("*Must be fixed before deployment*\n")
            for issue in report.critical:
                lines.append(f"### {issue.id}: {issue.location}")
                lines.append(f"{issue.desc}\n")
        
        # High issues
        if report.high:
            lines.append("\n## 🟠 High Priority Issues\n")
            lines.append("*Should be fixed before deployment*\n")
            for issue in report.high:
                lines.append(f"### {issue.id}: {issue.location}")
                lines.append(f"{issue.desc}\n")
        
        # Security flags
        if report.security_flags:
            lines.append("\n## 🔒 Security Flags\n")
            for flag in report.security_flags:
                lines.append(f"- ⚠️ {flag}")
            lines.append("")
        
        # Medium issues
        if report.medium:
            lines.append("\n## 🟡 Medium Priority Issues\n")
            for issue in report.medium:
                lines.append(f"- **{issue.id}** ({issue.location}): {issue.desc}")
        
        # Low issues
        if report.low:
            lines.append("\n## 🟢 Low Priority Issues\n")
            for issue in report.low:
                lines.append(f"- **{issue.id}** ({issue.location}): {issue.desc}")
        
        lines.append("\n---")
        lines.append("*Report generated by QA Agent*")
        
        return "\n".join(lines)
    
    def has_critical_issues(self, report: QAReport) -> bool:
        """Check if report has any critical issues."""
        return len(report.critical) > 0
    
    def get_issues_summary(self, report: QAReport) -> Dict[str, int]:
        """Get summary counts of issues by severity."""
        return {
            "critical": len(report.critical),
            "high": len(report.high),
            "medium": len(report.medium),
            "low": len(report.low),
            "security_flags": len(report.security_flags),
            "total": (
                len(report.critical) + 
                len(report.high) + 
                len(report.medium) + 
                len(report.low)
            )
        }
