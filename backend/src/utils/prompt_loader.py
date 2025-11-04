import aiofiles
import os

async def load_prompt_template(file_path: str) -> str:
    """Loads a prompt template from a given file path."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt template file not found: {file_path}")
    async with aiofiles.open(file_path, mode="r") as f:
        content = await f.read()
    return content
