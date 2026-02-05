import ast

class AstChunker:
    def chunk_file(self, file_path: str, content: str):
        chunks = []

        # fallback for non-Python files or parse errors
        if not file_path.endswith(".py"):
            return [{
                "id": f"{file_path}:0",
                "file_path": file_path,
                "content": content,
                "type": "code"
            }]

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return [{
                "id": f"{file_path}:0",
                "file_path": file_path,
                "content": content,
                "type": "code"
            }]

        lines = content.splitlines()

        for i, node in enumerate(tree.body):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                end = node.end_lineno

                chunk_text = "\n".join(lines[start:end])

                chunks.append({
                    "id": f"{file_path}:{i}",
                    "file_path": file_path,
                    "content": chunk_text,
                    "type": "code"
                })

        # fallback if no functions/classes
        if not chunks:
            chunks.append({
                "id": f"{file_path}:0",
                "file_path": file_path,
                "content": content,
                "type": "code"
            })

        return chunks
