import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, OpenAIChatCompletionsModel, Runner, trace
from openai import AsyncOpenAI, OpenAI

load_dotenv()

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


def load_prompt_with_content(content, prompt_filepath="prompt.txt"):
    """
    Loads a prompt from a file, replaces a {content} placeholder with the given content, and returns the resulting string.
    """
    with open(prompt_filepath, "r", encoding="utf-8") as f:
        prompt_template = f.read()
    return prompt_template.replace("{content}", content)

async def extract_info_from_content(content):
    """Extract information from a webpage."""
    gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=GEMINI_API_KEY)
    gemini_model = OpenAIChatCompletionsModel(model="gemini-3-flash-preview", openai_client=gemini_client)
    prompt = load_prompt_with_content(content)

    agent = Agent(
        name="Extract Info from Content",
        tools=[],
        model=gemini_model,
        instructions=prompt,
    )
    runner = Runner()
    return await runner.run(agent,"generate the markup page")

async def main():
    with open("output/vfSZGGC6Tdcm31CLnSZu9bRulbJ3.html", "r", encoding="utf-8") as f:
        content = f.read()
    extracted_info = await extract_info_from_content(content)
    with open("test.MD", "w", encoding="utf-8") as fout:
        fout.write(extracted_info.final_output if hasattr(extracted_info, "final_output") else str(extracted_info))
if __name__ == "__main__":
    asyncio.run(main())