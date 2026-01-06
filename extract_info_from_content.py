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

async def process_file(input_filepath, output_dir="generated"):
    """Process a single HTML file and save the extracted info to the generated directory."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the HTML content
    with open(input_filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract information
    print(f"Processing {input_filepath}...")
    extracted_info = await extract_info_from_content(content)
    
    # Generate output filename (replace .html with .md)
    input_filename = os.path.basename(input_filepath)
    output_filename = os.path.splitext(input_filename)[0] + ".md"
    output_filepath = os.path.join(output_dir, output_filename)
    
    # Write the extracted info to the output file
    with open(output_filepath, "w", encoding="utf-8") as fout:
        fout.write(extracted_info.final_output if hasattr(extracted_info, "final_output") else str(extracted_info))
    
    print(f"Generated {output_filepath}")

async def main():
    """Process all HTML files in the output directory."""
    output_dir = "output"
    generated_dir = "generated"
    
    # Get all HTML files in the output directory
    html_files = [
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(".html")
    ]
    
    if not html_files:
        print(f"No HTML files found in {output_dir} directory.")
        return
    
    print(f"Found {len(html_files)} HTML file(s) to process.")
    
    # Process each file
    for html_file in html_files:
        await process_file(html_file, generated_dir)
    
    print(f"\nAll files processed. Results saved to {generated_dir} directory.")

if __name__ == "__main__":
    asyncio.run(main())