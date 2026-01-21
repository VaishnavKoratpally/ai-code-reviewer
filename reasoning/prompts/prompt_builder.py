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

OUTPUT FORMAT (JSON ONLY):

{
  "architecture_summary": "High-level summary of how the system is structured.",
  "design_smells": [
    {
      "name": "Smell name",
      "evidence": "File or code pattern from context",
      "why_it_matters": "Why this is a problem"
    }
  ],
  "scalability_risks": [
    {
      "name": "Risk name",
      "evidence": "File or code pattern from context",
      "impact_and_mitigation": "Impact + how to fix"
    }
  ]
}


Rules:
- Use only the keys shown above.
- Do not include markdown.
- Do not include commentary outside JSON.
- Base your analysis strictly on the provided code context.
- Only reference files, modules, or patterns that appear in the provided context.
- Do not invent technologies, frameworks, or services.
- If evidence is insufficient, explicitly say "Insufficient information."
- Every issue must be tied to a concrete code pattern or file.


CODE CONTEXT:
{context_text}
"""

    return prompt
