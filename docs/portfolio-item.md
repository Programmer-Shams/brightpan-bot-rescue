# Upwork portfolio item

Draft for the owner to publish. Every number comes from the hand-reviewed results files in the repository (eval/results-broken.csv, eval/results-fixed*.csv, eval/holdout4-*.csv). No outside links, as the plan says.

## Project title
Fixing an AI Chatbot That Gives Wrong Answers: 46% → 100% on the Same Test

Shorter, if Upwork's title box is too small:
Fixing an AI Chatbot That Gave Wrong Answers: 46% → 100%

## Your role
AI developer: audit, fixes and testing

## Project description
A Python/LangChain support bot was giving outdated policies, inventing answers and showing one customer's order to another (faults planted on purpose). I audited it, ranked 5 root causes by severity, fixed them one at a time (same 41-question test after each), then fixed what a code review found: 46% → 100% correct in 3 separate runs, 1 → 0 privacy leaks, 0% → 100% of answers citing a source. On 15 new questions never used for any change: 10/15 → 15/15. Deliverables: written audit, fixes as separate commits, before/after results. Built with Python, LangChain, OpenAI and Chroma.

Shorter, if Upwork's description box is too small:
A Python/LangChain support bot gave outdated policies, invented answers and showed one customer's order to another (faults planted on purpose). I audited it, ranked 5 root causes, fixed them one at a time with the same 41-question test rerun after each, plus fixes from a code review: 46% → 100% correct, 1 → 0 privacy leaks, 0% → 100% of answers citing a source. Deliverables: written audit, one fix per commit, before/after results.

## Skills
Python, LangChain, AI Chatbot, RAG, OpenAI API

## Content (upload in this order)
1. 1-video.mp4: the video (1 min 54 s, 1920x1200, no audio). Caption on screen: "Faults planted on purpose for this portfolio project."
2. 2-cover-before-after.png: the before/after table; use it as the cover/thumbnail.
3. 3-architecture-before-after.png: the architecture, before vs after, with each fault marked.
4. 4-screenshot-broken-bot-leaks-order.png: the broken bot giving another customer's order and email to the wrong person.
5. 5-screenshot-fixed-vs-broken.png: the same shipping question, broken ($75, free) vs fixed ($6.95 under $99, with source).

Optional text block for the item (from the case study):
The bot was built quickly, then the store changed two policies and it kept giving the old answers. I wrote a 41-question test first, measured the bot as it was (19/41), wrote an audit with each fault's evidence and root cause, then fixed them in order of risk: privacy, outdated index, ungrounded instructions, bad chunking, weak retrieval. An independent code review of the result found more issues, which I fixed and retested. Every answer before and after was reviewed by hand. The final bot answered 41/41 in each of three runs and 15/15 on new questions it was never tuned on.
