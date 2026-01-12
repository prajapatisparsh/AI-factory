# 🧠 The AI Factory

A self-evolving multi-agent MVP generator that transforms business requirements into complete specifications.

## 🎯 Overview

The AI Factory uses collaborative AI agents to:
1. **Parse** business requirements from documents (PDF, images, text)
2. **Generate** user stories and architecture
3. **Draft** backend and frontend specifications
4. **Review** for quality issues
5. **Fix** identified problems
6. **Evaluate** final output with PM gatekeeper
7. **Learn** from failures to improve over time

## ✨ Key Innovation

Agents read persistent "playbooks" (Markdown files with learned rules). When output fails PM evaluation, a Coach agent extracts lessons and updates playbooks. **The system gets smarter with each failure.**

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the application:**
   ```bash
   poetry run streamlit run app.py
   ```

## 📋 Environment Variables

```env
GOOGLE_API_KEY=<gemini_key>       # For document vision
GROQ_API_KEY=<deepseek_key>       # For agent reasoning
TAVILY_API_KEY=<tavily_key>       # For library verification
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<key>
```

## 🏗️ Architecture

### Agents

| Agent | Purpose | API |
|-------|---------|-----|
| VisionAgent | Document parsing | Gemini 1.5 Pro |
| PMAgent | User stories, clarifications, evaluation | DeepSeek R1 (Groq) |
| TechLeadAgent | Architecture design | DeepSeek R1 (Groq) |
| DevTeamAgent | Backend/Frontend specs | DeepSeek R1 (Groq) |
| QAAgent | Quality analysis | DeepSeek R1 (Groq) |
| CoachAgent | Lesson extraction | DeepSeek R1 (Groq) |

### Workflow Phases

1. **Ingestion** - Parse uploaded document
2. **Foundation** - Generate user stories + architecture
3. **Clarification** - Resolve ambiguities
4. **Drafting** - Create backend/frontend specs
5. **QA** - Analyze for issues
6. **Fixing** - Apply corrections
7. **Gatekeeper** - PM evaluation (may loop back)
8. **Output** - Generate final files

### Safety Mechanisms

- ⏱️ **Rate Limit Protection** - Exponential backoff (1s → 16s)
- 🔄 **Infinite Loop Guard** - Max 3 retries then force proceed
- 📝 **Memory Deduplication** - 80% similarity threshold
- 💾 **State Recovery** - Graceful corruption handling

## 📁 Directory Structure

```
ai_factory/
├── app.py                 # Streamlit entry point
├── src/
│   ├── agents/           # AI agent implementations
│   │   ├── base.py       # Abstract base + Groq wrapper
│   │   ├── vision.py     # Gemini document parser
│   │   ├── pm.py         # Product Manager
│   │   ├── tech_lead.py  # Architect
│   │   ├── dev_team.py   # Backend/Frontend
│   │   ├── qa.py         # Quality checker
│   │   └── coach.py      # Memory updater
│   ├── utils/            # Utilities
│   │   ├── state.py      # Session management
│   │   ├── files.py      # I/O operations
│   │   └── fuzzy.py      # Text similarity
│   └── schemas.py        # Pydantic models
├── memory/               # Persistent playbooks
│   ├── pm_playbook.md
│   ├── tech_lead_playbook.md
│   ├── backend_playbook.md
│   ├── frontend_playbook.md
│   └── qa_playbook.md
└── projects/             # Generated outputs
```

## 📚 Playbooks

Each agent reads from learned rules to improve over time:

- **PM Playbook** - Requirements quality, evaluation criteria
- **Tech Lead Playbook** - Architecture decisions, tech choices
- **Backend Playbook** - API design, error handling
- **Frontend Playbook** - UX patterns, state management
- **QA Playbook** - Security checks, quality standards

## 🎮 Usage Tips

1. **Upload clear requirements** - The better the input, the better the output
2. **Review ambiguities** - The system flags unclear requirements
3. **Check QA report** - Critical issues must be addressed
4. **Trust the process** - If rejected, the system learns and improves

## 📊 Output Files

Each project generates:

| File | Contents |
|------|----------|
| `00_MASTER_PROMPT.md` | Implementation guide |
| `01_User_Stories.md` | Detailed requirements |
| `02_Architecture.md` | System design |
| `03_Backend_Final.md` | Backend specification |
| `04_Frontend_Final.md` | Frontend specification |
| `05_QA_Report.md` | Quality analysis |

## 🛡️ Error Handling

- **Gemini fails**: Falls back to text input
- **Groq fails**: Retries with exponential backoff
- **Tavily fails**: Uses fallback version list
- **PM rejects**: Extracts lessons and retries
- **Max retries**: Forces proceed with warnings

## 📄 License

MIT License - Feel free to modify and use.
