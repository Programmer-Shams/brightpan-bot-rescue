# Upwork portfolio item

Draft for the owner to publish. Every number comes from the hand-reviewed results files `eval/results-broken.csv` and `eval/results-fixed.csv`; see `eval/results-log.md`.

**Title:** Fixing an AI Chatbot That Gives Wrong Answers: 46% → 98% on the Same Test

**Role:** AI developer: audit, fixes and testing

**Description:** A Python/LangChain support bot was giving outdated policies, inventing answers and showing one customer's order to another (faults staged on a demo store). I audited it, ranked 5 root causes by severity, fixed them one at a time and reran the same 41-question test after each fix: 46% → 98% correct, 1 → 0 privacy leaks, 0% → 100% of answers citing a source. Deliverables: written audit, fixes as separate commits, before/after results. Built with Python, LangChain, OpenAI and Chroma.

**Skills:** Python, LangChain, AI Chatbot, RAG, OpenAI API

**Content:**
1. Demo video (60–120 s, caption on screen: "Staged faults on a demo bot."): the broken bot giving a wrong shipping answer and leaking an order, the audit report, the fix commits, the same questions answered correctly, the before/after table.
2. Architecture diagram: `docs/architecture.png`.
3. Text: a short version of `docs/case-study.md`.
