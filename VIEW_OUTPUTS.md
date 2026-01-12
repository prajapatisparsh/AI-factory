# 📋 How to View Full Outputs

## **1. Terminal Logs (Real-time)**
Look at your PowerShell terminal where you ran `poetry run streamlit run app.py`

**What you'll see:**
```
INFO:src.agents.base:Calling llama-3.1-8b-instant with max_tokens=8192
INFO:src.agents.base:✅ LLM response: finish_reason=stop, tokens=3420
INFO:__main__:Phase 4: backend_draft length = 5420
INFO:__main__:Phase 4: frontend_draft length = 4830
INFO:__main__:Phase 6: backend_final length = 5420
INFO:__main__:Phase 6: frontend_final length = 4830
```

This shows you:
- Which model is being called
- How many tokens each response used
- Length of each specification
- Any errors

---

## **2. Saved Files (After Phase 8)**
After the pipeline completes, all files are saved in:

```
D:\Personal project\Personal ai projects\projects\<timestamp>_<project_name>\
```

**Files created:**
- `user_stories.md` - All user stories
- `architecture.md` - Full architecture document
- `backend_spec.md` - Complete backend specification
- `frontend_spec.md` - Complete frontend specification
- `qa_report.md` - Full QA analysis
- `evaluation.md` - PM evaluation
- `master_prompt.txt` - Complete context for Claude/GPT

**Open these files in VS Code** to see the COMPLETE outputs (not truncated)!

---

## **3. Streamlit Expanders (In UI)**
Click the expanders like:
- 📋 View Phase 1 Output
- 📝 View User Stories
- 🏛️ View Architecture
- ⚙️ View Backend Spec
- 🎨 View Frontend Spec
- 🔍 View QA Issues

These show **first 1000 characters** of each output.

---

## **4. Check Terminal for Errors**
If you see errors like:
```
ERROR:src.agents.base:❌ DAILY TOKEN LIMIT EXCEEDED
```

The terminal will show you:
- Exact error messages
- Stack traces
- Which phase failed
- Token usage details

---

## **5. Session State (Debug)**
Add this to your Streamlit sidebar to debug:

```python
with st.sidebar:
    if st.button("Debug State"):
        state = get_workflow_state()
        st.write(f"Backend draft: {len(state.backend_draft) if state.backend_draft else 0} chars")
        st.write(f"Backend final: {len(state.backend_final) if state.backend_final else 0} chars")
        st.write(f"Frontend draft: {len(state.frontend_draft) if state.frontend_draft else 0} chars")
        st.write(f"Frontend final: {len(state.frontend_final) if state.frontend_final else 0} chars")
```

---

## **Quick Reference**

| **What** | **Where** |
|----------|-----------|
| Real-time logs | Terminal/PowerShell |
| Full outputs | `projects/<timestamp>/` folder |
| Quick preview | Expanders in UI (first 1000 chars) |
| Errors & traces | Terminal |
| Token usage | Terminal logs |
| Complete specs | Markdown files after Phase 8 |

---

## **Recommended Workflow**

1. **Watch terminal** while pipeline runs
2. **Check expanders** for quick previews
3. **Open saved files** after completion for full content
4. **Use terminal logs** to debug issues

---

**Pro Tip**: Keep your terminal visible while using the UI so you can see what's happening in real-time!
