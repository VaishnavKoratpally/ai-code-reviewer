def chunk_file(file_path: str, content: str, max_lines: int = 40):
    lines = content.splitlines()
    chunks = []

    for i in range(0, len(lines), max_lines):
        chunk_lines = lines[i:i + max_lines]
        chunk_text = "\n".join(chunk_lines)

        chunk = {
            "id": f"{file_path}:{i // max_lines}",
            "file_path": file_path,
            "content": chunk_text,
            "type": "code",
        }
        chunks.append(chunk)

    return chunks
