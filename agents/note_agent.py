from langchain_core.prompts import PromptTemplate
from llm import get_llm

# Prompt Template
prompt = PromptTemplate(
    input_variables=["context"],
    template="""
You are an expert university professor.

Use ONLY the context below to generate study notes.

Context:
{context}

Create notes using this format:

# 📘 Topic

# 📖 Definition

# 🧠 Easy Explanation
Explain in very simple language.

# 🌍 Real-Life Example

# ⭐ Key Points
- Bullet points

# 📌 Important Formula
(Write "Not available" if none)

# 💼 Applications

# ⚠ Exam Tips

# 📝 Summary

Rules:
- Do NOT copy the PDF word-for-word.
- Rewrite in your own words.
- Keep the explanation easy to understand.
- If information is missing, write:
  "Not mentioned in the uploaded document."
"""
)


def generate_notes(context, provider="Gemini"):
    """
    Generate study notes using the selected LLM.
    provider: 'Gemini' or 'Ollama'
    """

    llm = get_llm(provider)

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context
        }
    )

    return response.content