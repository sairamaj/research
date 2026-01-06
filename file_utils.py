import os


def get_output_filepath(unique_id, output_dir="output"):
    """Generate output file path for a startup ID."""
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"{unique_id}.html")

