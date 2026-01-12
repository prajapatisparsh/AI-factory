"""
Intelligent Prompting Techniques - Enhance LLM outputs.
Includes Chain-of-Thought, Self-Reflection, and Few-Shot Learning.
"""

from typing import Optional, List, Dict, Any


class IntelligentPrompting:
    """
    Collection of advanced prompting techniques to improve LLM outputs.
    """
    
    # Chain-of-Thought prefix for complex reasoning
    CHAIN_OF_THOUGHT = """
BEFORE ANSWERING, THINK STEP-BY-STEP:
1. What is the core requirement?
2. What are the key constraints?
3. What could go wrong or be missed?
4. What is the best approach?

After thinking through these questions, provide your detailed answer.

"""
    
    # Self-reflection suffix for quality improvement
    SELF_REFLECTION = """

AFTER GENERATING YOUR RESPONSE:
1. Review your output for completeness
2. Check for any missing edge cases
3. Verify consistency across sections
4. List any assumptions you made

If you find issues, FIX THEM before providing your final answer.
"""
    
    # Role-based expertise prefixes
    EXPERT_PREFIXES = {
        "backend": "You are a senior backend engineer with 15+ years of experience in building scalable APIs and microservices. You prioritize security, performance, and maintainability.",
        
        "frontend": "You are a senior frontend developer with expertise in modern React/Next.js. You focus on user experience, accessibility, performance, and clean component architecture.",
        
        "architect": "You are a principal software architect who has designed systems handling millions of users. You think about scalability, reliability, and future extensibility.",
        
        "pm": "You are a seasoned Product Manager who has shipped multiple successful products. You understand user needs, prioritization, and translating business requirements into technical specifications.",
        
        "qa": "You are a QA lead with expertise in test strategy, automation, and quality assurance. You think about edge cases, security vulnerabilities, and user experience issues.",
        
        "devops": "You are a DevOps engineer experienced with CI/CD, cloud infrastructure, and containerization. You focus on reliability, monitoring, and automation."
    }
    
    # Few-shot examples for common outputs
    FEW_SHOT_EXAMPLES = {
        "user_story": """
EXAMPLE USER STORY:

{
  "id": "US-001",
  "title": "User Registration",
  "user_role": "New User",
  "action": "create an account using email and password",
  "benefit": "I can access the platform's personalized features",
  "acceptance_criteria": [
    "Email format is validated (must contain @ and domain)",
    "Password must be 8+ characters with one uppercase and one number",
    "Duplicate emails are rejected with clear error message",
    "Confirmation email is sent within 30 seconds",
    "User is redirected to welcome page after successful registration"
  ],
  "priority": "Critical"
}
""",
        
        "api_endpoint": """
EXAMPLE API ENDPOINT:

### POST /api/v1/users/register

**Description:** Create a new user account

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z",
  "token": "eyJhbGc..."
}
```

**Error Responses:**
- 400: Invalid email format
- 409: Email already registered
- 422: Password doesn't meet requirements
""",
        
        "data_model": """
EXAMPLE DATA MODEL:

### User Model

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, Auto-generated | Unique identifier |
| email | String(255) | Required, Unique, Indexed | User's email address |
| password_hash | String(255) | Required | Bcrypt hashed password |
| name | String(100) | Required | Display name |
| role | Enum | Default: 'user', Options: ['user', 'admin'] | User role |
| is_active | Boolean | Default: true | Account status |
| created_at | DateTime | Auto-generated | Account creation time |
| updated_at | DateTime | Auto-updated | Last modification time |

**Indexes:**
- email (unique)
- created_at (for sorting)

**Relationships:**
- One-to-Many with Orders
- One-to-Many with Sessions
"""
    }
    
    @classmethod
    def enhance_system_prompt(
        cls,
        base_prompt: str,
        role: Optional[str] = None,
        use_cot: bool = True,
        use_reflection: bool = False
    ) -> str:
        """
        Enhance a system prompt with intelligent prompting techniques.
        
        Args:
            base_prompt: The original system prompt
            role: Expert role to use (backend, frontend, architect, pm, qa, devops)
            use_cot: Whether to add Chain-of-Thought prompting
            use_reflection: Whether to add self-reflection
        
        Returns:
            Enhanced system prompt
        """
        enhanced = ""
        
        # Add expert prefix if role specified
        if role and role in cls.EXPERT_PREFIXES:
            enhanced += cls.EXPERT_PREFIXES[role] + "\n\n"
        
        # Add Chain-of-Thought
        if use_cot:
            enhanced += cls.CHAIN_OF_THOUGHT
        
        # Add base prompt
        enhanced += base_prompt
        
        # Add self-reflection
        if use_reflection:
            enhanced += cls.SELF_REFLECTION
        
        return enhanced
    
    @classmethod
    def enhance_user_prompt(
        cls,
        base_prompt: str,
        example_type: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Enhance a user prompt with examples and context.
        
        Args:
            base_prompt: The original user prompt
            example_type: Type of few-shot example to include
            additional_context: Additional context to prepend
        
        Returns:
            Enhanced user prompt
        """
        enhanced = ""
        
        # Add additional context
        if additional_context:
            enhanced += f"{additional_context}\n\n"
        
        # Add few-shot example
        if example_type and example_type in cls.FEW_SHOT_EXAMPLES:
            enhanced += "FOLLOW THIS FORMAT EXACTLY:\n"
            enhanced += cls.FEW_SHOT_EXAMPLES[example_type]
            enhanced += "\n\nNOW, GENERATE YOUR RESPONSE:\n\n"
        
        enhanced += base_prompt
        
        return enhanced
    
    @classmethod
    def create_self_critique_prompt(cls, original_output: str, task_description: str) -> str:
        """
        Create a prompt for the model to critique its own output.
        
        Args:
            original_output: The LLM's original output
            task_description: What the task was
        
        Returns:
            Prompt for self-critique
        """
        return f"""You are a critical reviewer. Your task was:

{task_description}

You produced this output:

---
{original_output[:3000]}
---

Now, critically review your output:

1. **Completeness:** Are there any missing sections or requirements?
2. **Accuracy:** Are there any technical errors or inconsistencies?
3. **Clarity:** Is the output clear and well-organized?
4. **Edge Cases:** Did you miss any important edge cases?
5. **Best Practices:** Does it follow industry best practices?

List 3 specific improvements needed, then provide an IMPROVED version that addresses these issues.

FORMAT:
## Issues Found
1. [Issue 1]
2. [Issue 2]
3. [Issue 3]

## Improved Output
[Your improved output here]
"""
    
    @classmethod
    def create_verification_prompt(cls, output: str, requirements: List[str]) -> str:
        """
        Create a prompt to verify output against requirements.
        
        Args:
            output: The generated output
            requirements: List of requirements to check
        
        Returns:
            Verification prompt
        """
        req_list = "\n".join(f"{i+1}. {req}" for i, req in enumerate(requirements))
        
        return f"""Verify this output against the requirements:

REQUIREMENTS:
{req_list}

OUTPUT TO VERIFY:
---
{output[:2500]}
---

For each requirement, state:
- ✅ MET: [Explanation of how it's met]
- ❌ NOT MET: [Explanation of what's missing]
- ⚠️ PARTIAL: [Explanation of what's incomplete]

Finally, provide an overall score (0-100) and list any critical gaps.
"""


# Convenience functions
def enhance_prompt(
    system_prompt: str,
    user_prompt: str,
    role: Optional[str] = None,
    use_cot: bool = True,
    example_type: Optional[str] = None
) -> tuple:
    """
    Convenience function to enhance both system and user prompts.
    
    Returns:
        Tuple of (enhanced_system_prompt, enhanced_user_prompt)
    """
    enhanced_system = IntelligentPrompting.enhance_system_prompt(
        system_prompt,
        role=role,
        use_cot=use_cot
    )
    
    enhanced_user = IntelligentPrompting.enhance_user_prompt(
        user_prompt,
        example_type=example_type
    )
    
    return enhanced_system, enhanced_user
