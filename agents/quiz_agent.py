import json

from langchain_core.prompts import ChatPromptTemplate

from llm import get_llm
from prompts import QUIZ_PROMPT

# Create Prompt
quiz_prompt = ChatPromptTemplate.from_template(QUIZ_PROMPT)


def generate_quiz(context, provider="Gemini"):
    """
    Generate quiz from document context using
    the selected AI model.
    """

    llm = get_llm(provider)

    chain = quiz_prompt | llm

    try:

        response = chain.invoke({
            "context": context
        })

        text = response.content.strip()

        # Remove markdown if model returns it
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        # Extract only JSON array
        start = text.find("[")
        end = text.rfind("]")

        if start != -1 and end != -1:
            text = text[start:end + 1]

        quiz = json.loads(text)

        return quiz

    except Exception as e:

        print("\n========== QUIZ ERROR ==========")
        print(e)

        try:
            print("\nModel Output:\n")
            print(text)
        except:
            pass

        print("================================\n")

        return []