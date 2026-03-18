"""
Cost Estimation Utility - Detailed INR-based cost estimation for Indian market.
Covers development team, hosting, database, storage, CDN, monitoring, security,
third-party services, and ongoing operational costs.
"""

from typing import List, Dict, Tuple
from src.schemas import DocumentAnalysis, UserStory


# ---------------------------------------------------------------------------
# Constants — all monetary values in Indian Rupees (₹)
# ---------------------------------------------------------------------------

# Developer hourly rates (INR, Indian freelance/agency market 2026)
HOURLY_RATES = {
    "junior_developer":  500,
    "mid_developer":    1000,
    "senior_developer": 1500,
    "tech_lead":        2500,
    "qa_engineer":       800,
    "devops_engineer":  1300,
    "ui_ux_designer":   1100,
}

# Working hours: 8 hrs/day × 5 days × 4 weeks = 160 hrs/week-normalized
HOURS_PER_WEEK = 40


def _fmt(amount: int) -> str:
    """Format an integer rupee amount with ₹ and Indian comma grouping."""
    # Indian number system: last 3 digits, then groups of 2
    s = str(amount)
    if len(s) <= 3:
        return f"₹{s}"
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while rest:
        groups.append(rest[-2:])
        rest = rest[:-2]
    formatted = ",".join(reversed(groups)) + "," + last3
    return f"₹{formatted}"


def _fmt_range(low: int, high: int) -> str:
    return f"{_fmt(low)} – {_fmt(high)}"


# ---------------------------------------------------------------------------
# Tier classification
# ---------------------------------------------------------------------------

def _classify_tier(num_features: int) -> Dict:
    """Return project tier metadata based on feature count."""
    if num_features <= 5:
        return {
            "tier": "MVP",
            "complexity": "Low",
            "dev_weeks_low": 3,
            "dev_weeks_high": 5,
            "team": {"junior_developer": 1, "senior_developer": 1, "qa_engineer": 1},
            "infra_level": "basic",
        }
    elif num_features <= 12:
        return {
            "tier": "Standard",
            "complexity": "Medium",
            "dev_weeks_low": 6,
            "dev_weeks_high": 10,
            "team": {"junior_developer": 2, "mid_developer": 1, "senior_developer": 1, "qa_engineer": 1},
            "infra_level": "standard",
        }
    else:
        return {
            "tier": "Enterprise",
            "complexity": "High",
            "dev_weeks_low": 12,
            "dev_weeks_high": 20,
            "team": {
                "junior_developer": 2, "mid_developer": 2, "senior_developer": 2,
                "tech_lead": 1, "qa_engineer": 2, "devops_engineer": 1,
            },
            "infra_level": "premium",
        }


# ---------------------------------------------------------------------------
# Development cost breakdown
# ---------------------------------------------------------------------------

def _dev_costs(tier: Dict) -> Tuple[int, int, str]:
    """Return (low, high, breakdown_md) for development labour."""
    team = tier["team"]
    weeks_low = tier["dev_weeks_low"]
    weeks_high = tier["dev_weeks_high"]

    rows = []
    total_low = 0
    total_high = 0
    for role, count in team.items():
        rate = HOURLY_RATES[role]
        hrs_low = weeks_low * HOURS_PER_WEEK * count
        hrs_high = weeks_high * HOURS_PER_WEEK * count
        cost_low = rate * hrs_low
        cost_high = rate * hrs_high
        total_low += cost_low
        total_high += cost_high
        role_label = role.replace("_", " ").title()
        rows.append(
            f"| {role_label} ×{count} | {_fmt(rate)}/hr | "
            f"{hrs_low}–{hrs_high} hrs | {_fmt_range(cost_low, cost_high)} |"
        )

    table = (
        "| Role | Rate | Hours | Cost |\n"
        "| :--- | ---: | ---: | ---: |\n"
        + "\n".join(rows)
        + f"\n| **Total Development** | | | **{_fmt_range(total_low, total_high)}** |"
    )
    return total_low, total_high, table


# ---------------------------------------------------------------------------
# Infrastructure — hosting, DB, storage, CDN, CI/CD, monitoring, security
# ---------------------------------------------------------------------------

# Monthly INR costs per infra level for each component
_INFRA_MONTHLY = {
    # component: (basic, standard, premium)
    "App Server / Containers":     (4_000,  14_000,  40_000),
    "Load Balancer":               (1_500,   4_000,  10_000),
    "CI/CD Pipeline":              (    0,   2_000,   6_000),
    "Managed Database (RDS/Cloud DB)": (3_500, 10_000, 35_000),
    "Database Backups & Replicas": (1_000,   3_500,  12_000),
    "Object Storage (S3/GCS)":     (  600,   2_500,   8_000),
    "CDN (CloudFront/Cloudflare)": (1_000,   4_000,  15_000),
    "SSL Certificate + Domain":    (  200,     400,     800),
    "Monitoring & Alerting":       (    0,   4_000,  12_000),
    "Log Management":              (    0,   2_500,   8_000),
    "Security / WAF / DDoS Shield":(1_200,   5_000,  18_000),
}

_LEVEL_INDEX = {"basic": 0, "standard": 1, "premium": 2}


def _infra_costs(level: str, months: int) -> Tuple[int, int, str]:
    """Return (monthly_low, monthly_high, breakdown_md) for infrastructure."""
    idx = _LEVEL_INDEX[level]
    rows = []
    monthly_total = 0
    for component, prices in _INFRA_MONTHLY.items():
        price = prices[idx]
        monthly_total += price
        rows.append(f"| {component} | {_fmt(price)}/mo | {_fmt(price * months)} |")

    first_year = monthly_total * 12
    table = (
        f"| Component | Monthly | {months}-Month Total |\n"
        "| :--- | ---: | ---: |\n"
        + "\n".join(rows)
        + f"\n| **Total Infrastructure** | **{_fmt(monthly_total)}/mo** | **{_fmt(monthly_total * months)}** |"
    )
    return monthly_total, first_year, table


# ---------------------------------------------------------------------------
# Third-party services
# ---------------------------------------------------------------------------

def _third_party_costs(arch_lower: str) -> Tuple[int, str]:
    """Return (monthly_total, breakdown_md) for detected third-party services."""
    services = {
        "Email Service (AWS SES / Mailgun)": 1_500,
        "Error Tracking (Sentry Free)":         0,
    }

    if any(k in arch_lower for k in ["auth0", "firebase", "oauth", "sso", "cognito"]):
        services["Auth Provider (Auth0/Firebase)"] = 3_000
    elif any(k in arch_lower for k in ["auth", "jwt", "login"]):
        services["Auth Provider (Firebase Free tier)"] = 0

    if any(k in arch_lower for k in ["stripe", "razorpay", "payment", "paypal"]):
        services["Payment Gateway (Razorpay/Stripe — % per transaction)"] = 0
        services["PCI-DSS Compliance Setup (one-time ~₹25,000)"] = 0

    if any(k in arch_lower for k in ["sendgrid", "mailchimp", "campaign"]):
        services["Marketing Email Service (Mailchimp/SendGrid)"] = 2_500

    if any(k in arch_lower for k in ["twilio", "sms", "otp"]):
        services["SMS / OTP Service (Twilio/MSG91)"] = 2_000

    if any(k in arch_lower for k in ["map", "google maps", "location"]):
        services["Maps API (Google Maps Platform)"] = 1_500

    if any(k in arch_lower for k in ["push notification", "fcm", "apns"]):
        services["Push Notifications (Firebase FCM — free tier)"] = 0

    if any(k in arch_lower for k in ["analytics", "mixpanel", "amplitude"]):
        services["Analytics (Mixpanel/GA4 — free tier)"] = 0

    monthly = sum(services.values())
    rows = [f"| {svc} | {_fmt(cost)}/mo |" for svc, cost in services.items()]
    table = (
        "| Service | Monthly Cost |\n"
        "| :--- | ---: |\n"
        + "\n".join(rows)
        + f"\n| **Total 3rd-Party Services** | **{_fmt(monthly)}/mo** |"
    )
    return monthly, table


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def estimate_project_costs(
    context: DocumentAnalysis,
    user_stories: List[UserStory],
    architecture: str,
) -> str:
    """
    Generate a detailed INR cost estimation section for the project.
    Covers development labour, hosting, database, storage, CDN, CI/CD,
    monitoring, security, and third-party services.

    Returns:
        Markdown string with full cost breakdown.
    """
    from datetime import datetime

    num_features = len(context.features)
    num_stories = len(user_stories)
    arch_lower = architecture.lower()

    tier = _classify_tier(num_features)
    weeks_low = tier["dev_weeks_low"]
    weeks_high = tier["dev_weeks_high"]
    months_low = max(1, weeks_low // 4)
    months_high = max(1, weeks_high // 4)

    dev_low, dev_high, dev_table = _dev_costs(tier)
    infra_monthly, _, infra_table = _infra_costs(tier["infra_level"], months_high)
    tp_monthly, tp_table = _third_party_costs(arch_lower)

    # One-time setup costs (DevOps bootstrap, QA tooling, domain, design assets)
    setup_low  = 15_000
    setup_high = 40_000

    # 6-month operational cost projection
    ops_6m = (infra_monthly + tp_monthly) * 6

    total_low  = dev_low  + setup_low  + (infra_monthly + tp_monthly) * months_low
    total_high = dev_high + setup_high + (infra_monthly + tp_monthly) * months_high

    # Detect complexity boosters
    boosters = []
    if any(k in arch_lower for k in ["payment", "stripe", "razorpay"]):
        boosters.append("Payment integration adds ₹20,000–₹50,000 (compliance + testing)")
    if any(k in arch_lower for k in ["realtime", "websocket", "socket.io"]):
        boosters.append("Real-time features add ₹15,000–₹40,000 + higher server costs")
    if any(k in arch_lower for k in ["ml", "ai", "model", "inference", "recommendation"]):
        boosters.append("AI/ML features add ₹30,000–₹1,00,000+ (GPU infra, model hosting)")
    if any(k in arch_lower for k in ["mobile", "ios", "android", "react native", "flutter"]):
        boosters.append("Mobile app adds ₹40,000–₹1,20,000 (native builds + app store setup)")
    if any(k in arch_lower for k in ["microservice", "kubernetes", "k8s"]):
        boosters.append("Microservices architecture adds 30–40% to DevOps & infra costs")

    output = f"""## 💰 Cost Estimation — INR Breakdown

> **Generated:** {datetime.now().strftime("%B %d, %Y")} | **Project Tier:** {tier['tier']} ({tier['complexity']} complexity) | **Currency:** ₹ INR

---

### 👥 Development Labour

{dev_table}

---

### 🖥️ Infrastructure (Monthly & Project Duration)

> Estimated project duration: **{weeks_low}–{weeks_high} weeks** (~{months_low}–{months_high} months)

{infra_table}

---

### 🔌 Third-Party Services

{tp_table}

---

### 📦 One-Time Setup Costs

| Item | Estimate |
| :--- | ---: |
| DevOps Bootstrap (CI/CD, Docker setup, IaC) | {_fmt_range(8_000, 20_000)} |
| QA Tooling & Environment Setup | {_fmt_range(3_000, 10_000)} |
| Domain Registration (2 years) | {_fmt_range(1_000, 3_000)} |
| Design Assets & Figma Licensing | {_fmt_range(3_000, 7_000)} |
| **Total Setup** | **{_fmt_range(setup_low, setup_high)}** |

---

### 📊 Total Cost Summary

| Category | Estimate |
| :--- | ---: |
| Development Labour | {_fmt_range(dev_low, dev_high)} |
| Infrastructure ({months_low}–{months_high} months) | {_fmt_range(infra_monthly * months_low, infra_monthly * months_high)} |
| Third-Party Services ({months_low}–{months_high} months) | {_fmt_range(tp_monthly * months_low, tp_monthly * months_high)} |
| One-Time Setup | {_fmt_range(setup_low, setup_high)} |
| User Stories in Scope | {num_stories} |
| **🧾 Grand Total (Project)** | **{_fmt_range(total_low, total_high)}** |

---

### 🔄 Ongoing Monthly Operational Cost (Post-Launch)

| Category | Monthly |
| :--- | ---: |
| Infrastructure | {_fmt(infra_monthly)} |
| Third-Party Services | {_fmt(tp_monthly)} |
| **Total Monthly Burn** | **{_fmt(infra_monthly + tp_monthly)}** |
| **6-Month Projection** | **{_fmt(ops_6m)}** |
| **Annual Projection** | **{_fmt((infra_monthly + tp_monthly) * 12)}** |
"""

    if boosters:
        output += "\n---\n\n### ⚡ Additional Cost Factors\n\n"
        for b in boosters:
            output += f"- {b}\n"

    output += """
---

> **Note:** All estimates are for the Indian market (INR). Development rates reflect Indian freelance/agency market (2026).
> Infrastructure costs are based on AWS/GCP India (ap-south-1) region pricing.
> Actual costs vary based on team location, vendor choice, and traffic scale.
> Payment gateways (Razorpay/Stripe) charge **1.5–3% per transaction** — not reflected above.
"""
    return output


def generate_executive_summary(
    context: DocumentAnalysis,
    user_stories: List[UserStory],
    architecture: str,
    cost_estimation: str = "",
) -> str:
    """
    Generate a non-technical executive summary for stakeholders (INR, Indian market).

    Covers: What, Who, Timeline, Full Budget Breakdown, Risks, Next Steps.

    Returns:
        Markdown string with executive summary.
    """
    from datetime import datetime

    _ = cost_estimation  # accepted for API compatibility; detail is recomputed here
    num_features = len(context.features)
    num_stories = len(user_stories)
    arch_lower = architecture.lower()
    project_type = context.project_type.value.replace("_", " ").title()

    critical_stories = [s for s in user_stories if s.priority.value == "Critical"]
    high_stories = [s for s in user_stories if s.priority.value == "High"]

    tier = _classify_tier(num_features)
    weeks_low = tier["dev_weeks_low"]
    weeks_high = tier["dev_weeks_high"]
    months_low = max(1, weeks_low // 4)
    months_high = max(1, weeks_high // 4)

    dev_low, dev_high, _ = _dev_costs(tier)
    infra_monthly, _, _ = _infra_costs(tier["infra_level"], months_high)
    tp_monthly, _ = _third_party_costs(arch_lower)
    setup_low, setup_high = 15_000, 40_000

    total_low  = dev_low  + setup_low  + (infra_monthly + tp_monthly) * months_low
    total_high = dev_high + setup_high + (infra_monthly + tp_monthly) * months_high
    monthly_ops = infra_monthly + tp_monthly

    # Detect integrations
    integrations = []
    if any(k in arch_lower for k in ["stripe", "razorpay", "payment"]):
        integrations.append("Payment Gateway (Razorpay / Stripe)")
    if any(k in arch_lower for k in ["auth0", "firebase", "oauth"]):
        integrations.append("Third-Party Authentication")
    if any(k in arch_lower for k in ["aws", "gcp", "azure", "cloud"]):
        integrations.append("Cloud Infrastructure (AWS / GCP India region)")
    if any(k in arch_lower for k in ["sendgrid", "ses", "email", "mailgun"]):
        integrations.append("Email Service (AWS SES / Mailgun)")
    if any(k in arch_lower for k in ["twilio", "sms", "otp"]):
        integrations.append("SMS/OTP Service (Twilio / MSG91)")
    if any(k in arch_lower for k in ["map", "google maps"]):
        integrations.append("Maps API (Google Maps Platform)")

    # Risks
    risks = []
    if num_features > 15:
        risks.append("Large scope — recommend phased delivery to reduce risk")
    if any(k in arch_lower for k in ["payment", "financial"]):
        risks.append("Payment integration requires PCI-DSS compliance review")
    if any(k in arch_lower for k in ["health", "medical", "patient"]):
        risks.append("Healthcare data requires DISHA/HIPAA compliance controls")
    if any(k in arch_lower for k in ["realtime", "websocket"]):
        risks.append("Real-time features require higher-spec servers and stress testing")
    if any(k in arch_lower for k in ["ml", "ai", "model"]):
        risks.append("AI/ML components may have unpredictable inference costs at scale")
    if not risks:
        risks.append("Standard delivery risks — scope creep, API integration delays")

    top_features = context.features[:5]

    summary = f"""# 📋 Executive Summary

**Generated:** {datetime.now().strftime("%B %d, %Y")} | **Currency:** ₹ INR (Indian Market)

---

## 🎯 What We're Building

**Project Type:** {project_type}
**Complexity:** {tier['tier']} — {tier['complexity']}

This MVP delivers a **{project_type.lower()}** with **{num_features} core features**:

"""
    for i, feature in enumerate(top_features, 1):
        summary += f"{i}. {feature}\n"
    if num_features > 5:
        summary += f"\n*...and {num_features - 5} additional features*\n"

    summary += "\n---\n\n## 👥 Who This Is For\n\n"
    if context.personas:
        for persona in context.personas[:4]:
            summary += f"- **{persona}**\n"
    else:
        summary += "- End users seeking a streamlined digital experience\n"

    summary += f"""
---

## ⏱️ Timeline

| Milestone | Duration |
| :--- | :--- |
| Discovery & Architecture | Week 1–2 |
| Core Feature Development | Week 2–{weeks_low} |
| QA, Testing & Bug Fixes | Week {weeks_low}–{weeks_high - 1} |
| Deployment & Launch | Week {weeks_high} |
| **Total Estimate** | **{weeks_low}–{weeks_high} weeks ({months_low}–{months_high} months)** |

---

## 💰 Investment Breakdown (INR)

### Development Cost
| Category | Estimate |
| :--- | ---: |
| Development Labour | {_fmt_range(dev_low, dev_high)} |
| One-Time Setup | {_fmt_range(setup_low, setup_high)} |
| Infrastructure ({months_low}–{months_high} months) | {_fmt_range(infra_monthly * months_low, infra_monthly * months_high)} |
| 3rd-Party Services ({months_low}–{months_high} months) | {_fmt_range(tp_monthly * months_low, tp_monthly * months_high)} |
| **Project Total** | **{_fmt_range(total_low, total_high)}** |

### Post-Launch Monthly Operations
| Category | Monthly Cost |
| :--- | ---: |
| Hosting & Infrastructure | {_fmt(infra_monthly)} |
| Third-Party Services | {_fmt(tp_monthly)} |
| **Total Monthly Burn** | **{_fmt(monthly_ops)}** |
| **Annual Operational Cost** | **{_fmt(monthly_ops * 12)}** |

"""

    if integrations:
        summary += "### Third-Party Services Required\n"
        for svc in integrations:
            summary += f"- {svc}\n"
        summary += "\n"

    summary += "---\n\n## ⚠️ Key Risks\n\n"
    for risk in risks[:5]:
        summary += f"- {risk}\n"

    summary += f"""
---

## ✅ Recommended Next Steps

1. **Approve & Sign-Off** — Confirm project scope and budget range
2. **Prioritise Critical Features** — Lock down the {len(critical_stories)} critical + {len(high_stories)} high-priority stories for Sprint 1
3. **Vendor Selection** — Choose cloud provider (AWS/GCP India region recommended), payment gateway, and auth provider
4. **Kick Off Development** — Begin with infrastructure setup and CI/CD pipeline
5. **Weekly Demos** — Schedule stakeholder reviews every Friday

---

## 📊 At a Glance

| Metric | Value |
| :--- | ---: |
| Core Features | {num_features} |
| User Stories | {num_stories} |
| Critical Stories | {len(critical_stories)} |
| High Priority Stories | {len(high_stories)} |
| Timeline | {weeks_low}–{weeks_high} weeks |
| **Project Budget** | **{_fmt_range(total_low, total_high)}** |
| **Monthly Ops Cost** | **{_fmt(monthly_ops)}** |
| **Annual Ops Cost** | **{_fmt(monthly_ops * 12)}** |

---

*Auto-generated by AI Factory. All costs in INR for the Indian development market (2026).
Infrastructure pricing based on AWS/GCP ap-south-1 (Mumbai) region.
Consult your finance team before finalising budgets.*
"""
    return summary
