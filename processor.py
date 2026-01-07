import os
import asyncio
import csv
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


def create_summary_txt(generated_dir="generated", summary_filename="summary.txt"):
    """
    Extract the comma-separated summary line from each markdown file and create a properly formatted CSV file.
    Fields containing commas will be quoted to ensure proper parsing in Google Sheets.
    
    Args:
        generated_dir: Directory containing markdown files
        summary_filename: Name of the output summary file (default: summary.txt)
    """
    md_files = [
        f for f in os.listdir(generated_dir)
        if f.endswith(".md") and f != "summary.md"
    ]
    if not md_files:
        print(f"No markdown files found in {generated_dir} to extract summaries from.")
        return
    
    header = ["Decision", "Brief Description", "Asking price", "TTM Revenue", "TTM profit", "LastMonth Revenue", "Customers", "Selling REASONING"]
    rows = [header]
    
    for md_file in md_files:
        filepath = os.path.join(generated_dir, md_file)
        with open(filepath, "r", encoding="utf-8") as fin:
            lines = fin.readlines()
            
        # Find the last line that contains comma-separated values
        # Look for lines with multiple commas (at least 4-5 commas for our format)
        summary_line = None
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            # Check if line has multiple commas (likely our summary line)
            if line.count(',') >= 4:
                # Remove markdown formatting like **Summary:** if present
                if '**Summary:**' in line:
                    line = line.replace('**Summary:**', '').strip()
                summary_line = line
                break
        
        if summary_line:
            # Parse the comma-separated line into fields
            # Try csv.reader first (works for properly quoted CSV)
            import io
            fields = None
            try:
                reader = csv.reader(io.StringIO(summary_line))
                parsed_fields = next(reader)
                if len(parsed_fields) == 7:
                    fields = parsed_fields
            except:
                pass
            
            # If csv.reader didn't work (unquoted CSV), use regex-based parsing
            # Pattern: Look for commas that are NOT inside quoted strings or numeric values
            if not fields:
                import re
                # Pattern to match: field, field, field
                # But be smart about commas inside values like "$222,240" or "1,000-5,000"
                # Strategy: Split by comma, but merge parts that look like they belong together
                parts = [p.strip() for p in summary_line.split(',')]
                
                # Expected format: Description, Price, Revenue, Profit, LastMonth, Customers, Reason
                # Fields 2-5 are monetary (may have commas), Field 6 may have commas (ranges)
                # Try to merge adjacent parts that look like they're part of the same field
                # Use iterative merging to handle multi-part fields
                merged = parts[:]
                for _ in range(3):  # Max 3 passes
                    new_merged = []
                    i = 0
                    while i < len(merged):
                        part = merged[i].strip()
                        
                        if i < len(merged) - 1:
                            next_part = merged[i + 1].strip()
                            
                            should_merge = (
                                # "$222" + "240" -> "$222,240"
                                (part.endswith('$') and next_part[0].isdigit()) or
                                # "1" + "000" or "000-5" -> "1,000" or "1,000-5"
                                (part.replace('$', '').replace(',', '').replace('.', '').strip().isdigit() and 
                                 len(part.strip()) <= 4 and not part.endswith('k') and not part.endswith('M') and
                                 (next_part.replace(',', '').replace('-', '').isdigit() or
                                  ('-' in next_part and next_part.replace(',', '').replace('-', '').isdigit()))) or
                                # "1,000-" + "5" -> "1,000-5"
                                (part.endswith('-') and next_part[0].isdigit()) or
                                # "000-5" + "000" -> "000-5,000"
                                ('-' in part and part.replace('-', '').replace(',', '').isdigit() and 
                                 next_part.replace(',', '').isdigit() and len(next_part.replace(',', '')) <= 4) or
                                # Short number + digits
                                (len(part.strip()) <= 3 and part.replace('$', '').strip().isdigit() and 
                                 not part.endswith('k') and not part.endswith('M') and
                                 next_part.replace(',', '').isdigit())
                            )
                            
                            if should_merge:
                                new_merged.append(f"{part},{next_part}")
                                i += 2
                                continue
                        
                        new_merged.append(merged[i])
                        i += 1
                    
                    if len(new_merged) == len(merged):
                        break
                    merged = new_merged
                
                if len(merged) == 7:
                    fields = merged
                elif len(merged) > 7:
                    # Too many fields - try to merge the last few
                    # Often the description or reason field gets split
                    # Merge first field(s) if they don't look like prices
                    if not merged[0].startswith('$') and len(merged) > 7:
                        # Try merging first two fields
                        fields = [f"{merged[0]}, {merged[1]}"] + merged[2:]
                        if len(fields) != 7:
                            fields = None
                    else:
                        fields = None
                else:
                    fields = None
            
            if fields and len(fields) == 7:
                # Add "Pending" as the Decision column value (first column)
                fields.insert(0, "Pending")
                rows.append(fields)
            else:
                print(f"Warning: Could not parse summary line in {md_file} into 7 fields. Line: {summary_line[:100]}...")
        else:
            print(f"Warning: Could not find summary line in {md_file}")
    
    summary_path = os.path.join(generated_dir, summary_filename)
    # Write CSV with proper quoting - fields containing commas will be quoted
    with open(summary_path, "w", encoding="utf-8", newline='') as fout:
        writer = csv.writer(fout, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)
    
    print(f"Created {summary_path} with {len(rows) - 1} summary lines")
