def build_architecture_prompt(chunks):
    context_blocks = []

    for chunk in chunks:
        block = f"FILE: {chunk['file_path']}\n{chunk['content']}"
        context_blocks.append(block)

    context_text = "\n\n---\n\n".join(context_blocks)

    prompt = f"""
You are a senior software architect performing static analysis of a codebase.

Your task:
Analyze the provided code excerpts and produce a structured architectural assessment.

You MUST return valid JSON in the following format ONLY:

{{
  "architecture_summary": "<high level description of the system architecture>",
  "design_smells": ["<smell 1>", "<smell 2>", "..."],
  "scalability_risks": ["<risk 1>", "<risk 2>", "..."]
}}

Rules:
- Use only the keys shown above.
- Do not include markdown.
- Do not include commentary outside JSON.
- Base your analysis strictly on the provided code context.

CODE CONTEXT:
{context_text}
"""

    return prompt
