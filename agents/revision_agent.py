from langchain_core.prompts import PromptTemplate

from llm import get_llm

prompt = PromptTemplate(
    input_variables=["context"],
    template="""
You are an expert study planner.

Use ONLY the context below.

Context:
{context}

Create a detailed 7-day revision plan.

Format:

# 📅 7-Day Revision Plan

## Day 1
- Topics to study
- Important concepts
- Practice task

## Day 2
- Topics to revise
- Key formulas
- Practice task

Continue until Day 7.

Rules:
- Use only the provided context.
- Divide the topics evenly.
- Mention important formulas if available.
- Include one practice activity every day.
- Finish with final revision tips.
"""
)


def create_plan(context, provider="Gemini"):
    """
    Generate a revision plan using the selected AI model.
    """

    llm = get_llm(provider)

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context
        }
    )

    return response.content