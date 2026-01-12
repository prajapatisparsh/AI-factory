"""
Cost Estimation Utility - Simple cost estimation without full agent overhead.
Generates a brief cost summary as part of the project output.
"""

from typing import List, Dict
from src.schemas import DocumentAnalysis, UserStory


def estimate_project_costs(
    context: DocumentAnalysis,
    user_stories: List[UserStory],
    architecture: str
) -> str:
    """
    Generate a simple cost estimation section for the project.
    
    Returns:
        Markdown string with cost estimate
    """
    # Estimate complexity based on features
    num_features = len(context.features)
    num_stories = len(user_stories)
    
    # Simple complexity calculation
    if num_features <= 5:
        complexity = "Low"
        dev_weeks = "2-4"
        team_size = "1-2"
        cost_range = "$5,000 - $15,000"
    elif num_features <= 12:
        complexity = "Medium"
        dev_weeks = "4-8"
        team_size = "2-3"
        cost_range = "$15,000 - $40,000"
    else:
        complexity = "High"
        dev_weeks = "8-16"
        team_size = "3-5"
        cost_range = "$40,000 - $100,000+"
    
    # Check for complexity indicators in architecture
    has_auth = "auth" in architecture.lower() or "jwt" in architecture.lower()
    has_payments = "payment" in architecture.lower() or "stripe" in architecture.lower()
    has_realtime = "websocket" in architecture.lower() or "realtime" in architecture.lower()
    
    additional_factors = []
    if has_auth:
        additional_factors.append("Authentication system (+10-20%)")
    if has_payments:
        additional_factors.append("Payment integration (+15-25%)")
    if has_realtime:
        additional_factors.append("Real-time features (+20-30%)")
    
    # Build output
    output = f"""## 💰 Cost Estimation Summary

| Metric | Estimate |
| :--- | :--- |
| **Complexity** | {complexity} |
| **Features** | {num_features} core features |
| **User Stories** | {num_stories} stories |
| **Timeline** | {dev_weeks} weeks |
| **Team Size** | {team_size} developers |
| **Estimated Cost** | {cost_range} |
"""
    
    if additional_factors:
        output += "\n### Additional Cost Factors\n"
        for factor in additional_factors:
            output += f"- {factor}\n"
    
    output += """
> **Note:** These are rough estimates for MVP development. Actual costs depend on team rates, location, and specific requirements.
"""
    
    return output


def generate_executive_summary(
    context: DocumentAnalysis,
    user_stories: List[UserStory],
    architecture: str,
    cost_estimation: str
) -> str:
    """
    Generate a non-technical executive summary for stakeholders.
    
    This 1-pager covers: What, Why, How Long, How Much, Key Risks, Next Steps.
    
    Returns:
        Markdown string with executive summary
    """
    from datetime import datetime
    
    # Extract key info
    num_features = len(context.features)
    num_stories = len(user_stories)
    project_type = context.project_type.value.replace('_', ' ').title()
    
    # Get top 5 features for the summary
    top_features = context.features[:5]
    
    # Get critical stories
    critical_stories = [s for s in user_stories if s.priority.value == "Critical"]
    high_stories = [s for s in user_stories if s.priority.value == "High"]
    
    # Estimate timeline from cost estimation
    if num_features <= 5:
        timeline_weeks = "2-4"
        timeline_months = "~1"
        budget_range = "$5,000 - $15,000"
    elif num_features <= 12:
        timeline_weeks = "4-8"
        timeline_months = "1-2"
        budget_range = "$15,000 - $40,000"
    else:
        timeline_weeks = "8-16"
        timeline_months = "2-4"
        budget_range = "$40,000 - $100,000+"
    
    # Detect key integrations/risks based on architecture
    arch_lower = architecture.lower()
    integrations = []
    if any(kw in arch_lower for kw in ['stripe', 'payment', 'paypal']):
        integrations.append("Payment processing")
    if any(kw in arch_lower for kw in ['auth0', 'oauth', 'sso']):
        integrations.append("Third-party authentication")
    if any(kw in arch_lower for kw in ['aws', 'gcp', 'azure']):
        integrations.append("Cloud infrastructure")
    if any(kw in arch_lower for kw in ['sendgrid', 'ses', 'email']):
        integrations.append("Email services")
    
    # Identify potential risks
    risks = []
    if num_features > 15:
        risks.append("Large scope may require phased delivery")
    if any(kw in arch_lower for kw in ['payment', 'financial', 'money']):
        risks.append("Payment compliance requirements (PCI-DSS)")
    if any(kw in arch_lower for kw in ['health', 'medical', 'patient']):
        risks.append("Healthcare compliance (HIPAA)")
    if any(kw in arch_lower for kw in ['realtime', 'websocket', 'live']):
        risks.append("Real-time features require specialized infrastructure")
    if len(risks) == 0:
        risks.append("Standard development risks (scope creep, integration issues)")
    
    # Build the summary
    summary = f"""# 📋 Executive Summary

**Generated:** {datetime.now().strftime("%B %d, %Y")}

---

## 🎯 What We're Building

**Project Type:** {project_type}

This MVP will deliver a {project_type.lower()} application with **{num_features} core features** that enable users to:

"""
    
    for i, feature in enumerate(top_features[:5], 1):
        summary += f"{i}. {feature}\n"
    
    if num_features > 5:
        summary += f"\n*...and {num_features - 5} additional features*\n"
    
    summary += f"""
---

## 💡 Why This Matters

Based on the requirements analysis, this application addresses:

"""
    
    # Extract personas and their needs
    if context.personas:
        for persona in context.personas[:3]:
            summary += f"- **{persona}** - enabling them to accomplish their goals efficiently\n"
    else:
        summary += "- End users seeking a streamlined digital experience\n"
    
    summary += f"""
---

## ⏱️ Timeline

| Phase | Duration |
| :--- | :--- |
| **MVP Development** | {timeline_weeks} weeks |
| **Estimated Delivery** | {timeline_months} month(s) from kickoff |

**Key Milestones:**
1. **Week 1-2:** Setup, architecture, core infrastructure
2. **Week 2-{int(timeline_weeks.split('-')[0])+2}:** Feature development
3. **Final weeks:** Testing, refinement, deployment

---

## 💰 Investment

| Category | Estimate |
| :--- | :--- |
| **Development Budget** | {budget_range} |
| **Team Size** | 2-4 developers |
| **Ongoing Costs** | ~$100-500/month (hosting, services) |

"""
    
    if integrations:
        summary += "**Third-Party Services Required:**\n"
        for integration in integrations:
            summary += f"- {integration}\n"
        summary += "\n"
    
    summary += f"""---

## ⚠️ Key Risks & Mitigations

"""
    
    for risk in risks[:4]:
        summary += f"- {risk}\n"
    
    summary += f"""
---

## ✅ Recommended Next Steps

1. **Review & Approve** - Confirm this summary aligns with business objectives
2. **Prioritize Features** - Validate the {len(critical_stories)} critical features for MVP
3. **Kick Off Development** - Begin with foundation and highest-priority items
4. **Establish Checkpoints** - Schedule weekly demos for stakeholder feedback

---

## 📊 At a Glance

| Metric | Value |
| :--- | :--- |
| Core Features | {num_features} |
| User Stories | {num_stories} |
| Critical Priority | {len(critical_stories)} stories |
| High Priority | {len(high_stories)} stories |
| Estimated Timeline | {timeline_months} month(s) |
| Budget Range | {budget_range} |

---

*This executive summary was auto-generated from technical specifications. For detailed technical information, refer to the Architecture and Specification documents.*
"""
    
    return summary
