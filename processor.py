import os
import asyncio
from extract_info_from_content import process_file


def run_extract_info_for_scraped_files(output_dir="output", generated_dir="generated", use_real_llm=False, max_workers=3):
    """
    Run the extract_info_from_content process on all HTML files in the OUTPUT_DIR directory,
    and put the resulting markdown in the 'generated' directory.
    
    Args:
        output_dir: Directory containing HTML files to process
        generated_dir: Directory to save generated markdown files
        use_real_llm: If True, use real LLM API. If False, use mock (default: False)
        max_workers: Number of files to process in parallel (default: 3)
    """
    html_files = [
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(".html")
    ]
    if not html_files:
        print(f"No scraped html files found in {output_dir}")
        return

    async def batch_process(max_workers=3):
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_with_semaphore(html_file):
            async with semaphore:
                await process_file(html_file, output_dir=generated_dir, use_real_llm=use_real_llm)
        
        tasks = [process_with_semaphore(html_file) for html_file in html_files]
        await asyncio.gather(*tasks)
    
    asyncio.run(batch_process(max_workers))


def merge_markdown_files(output_dir="generated", summary_filename="summary.md"):
    """
    Merge all .md files in the output_dir into a single summary.md file.
    """
    md_files = [
        f for f in os.listdir(output_dir)
        if f.endswith(".md") and f != summary_filename
    ]
    if not md_files:
        print(f"No markdown files found in {output_dir} to merge.")
        return
    
    merged_content = []
    for md_file in md_files:
        filepath = os.path.join(output_dir, md_file)
        with open(filepath, "r", encoding="utf-8") as fin:
            content = fin.read()
            # Do not add filename as a header
            merged_content.append(f"{content}\n")

    summary_path = os.path.join(output_dir, summary_filename)
    with open(summary_path, "w", encoding="utf-8") as fout:
        fout.write("\n\n".join(merged_content))

    print(f"Merged {len(md_files)} markdown files into {summary_path}")

