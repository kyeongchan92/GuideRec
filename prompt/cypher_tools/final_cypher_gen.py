FINAL_CYPHER_GENERATION_PROMPT = """
You are a Neo4j Cypher expert. Given partial Cypher logic from various semantic fields, write a full Cypher query.

User query: {query}

Partial Cypher components:
{parts}

Instructions:
- Combine the MATCH, WHERE, and WITH clauses into a full valid Cypher query.
- Include `RETURN` clause with pk, name, address, and menu.
- Use LIMIT 500.
- Do not include backticks or Markdown blocks.

Final Cypher:
"""
