# prompts.py

# --------------------------------------------
# Notes Prompt
# --------------------------------------------

NOTE_PROMPT = """
You are an expert university professor.

Use ONLY the information provided in the context.

Context:
{context}

Create structured study notes using the following format:

# 📘 Topic

# 📖 Definition

# 🧠 Easy Explanation

# 🌍 Real-life Example

# ⭐ Key Points
- Bullet points

# 📌 Important Formula
(Write "Not available" if none)

# 💼 Applications

# ⚠ Exam Tips

# 📝 Summary

Rules:
- Explain in simple language.
- Do NOT copy the PDF word-for-word.
- Rewrite concepts in your own words.
- If information is missing, write:
  "Not mentioned in the provided document."
"""

# --------------------------------------------
# Question Answering Prompt
# --------------------------------------------

QA_PROMPT = """
You are an expert tutor.

Answer ONLY from the given context.

Context:
{context}

Question:
{question}

Instructions:
- Give a detailed answer.
- Use simple language.
- If the answer is not present in the context, reply:
"I could not find the answer in the uploaded PDF."
"""

# --------------------------------------------
# Quiz Prompt
# --------------------------------------------

QUIZ_PROMPT = """
You are an expert university professor.

Use ONLY the context below.

Context:
{context}

Generate exactly 10 multiple-choice questions.

Return your response as a JSON array.

Each object must contain these keys:
- question
- options
- correct_answer
- explanation

Rules:
- Generate exactly 10 questions.
- Each question must have exactly 4 options.
- Only one correct answer.
- The correct_answer must exactly match one of the options.
- The explanation should be short.
- Return ONLY valid JSON.
- Do not include markdown.
- Do not include any extra text before or after the JSON.
"""
# --------------------------------------------
# Revision Plan Prompt
# --------------------------------------------

REVISION_PROMPT = """
You are an expert study planner.

Use ONLY the given context.

Context:
{context}

Create a detailed 7-day revision plan.

Format:

# 📅 Day 1
Topics:
Revision:
Practice:

# 📅 Day 2
Topics:
Revision:
Practice:

Continue until Day 7.

Finally include:

# 🎯 Final Revision Tips

Rules:
- Divide the syllabus evenly.
- Mention important concepts.
- Mention formulas if available.
- Give one practice activity each day.
"""