arXiv query cheatsheet (for search_query)
The arXiv API uses search_query=... with field prefixes and boolean operators.
Fields
 • all: anywhere (default-ish)
 • ti: title
 • abs: abstract
 • au: author
 • cat: category (e.g., cs.CV, cs.LG, cs.CL, stat.ML)


Operators
 • AND, OR, ANDNOT
 • Parentheses: ( ... )
 • Phrases: use quotes, e.g. all:"diffusion model"


Patterns
 • Broad topic + category:
 ◦ all:"graph neural network" AND (cat:cs.LG OR cat:cs.AI)
 • 

 • Narrow with task keywords:
 ◦ all:"diffusion model" AND (all:inpainting OR all:"image editing") AND cat:cs.CV
 • 

 • Two-stage approach:
 ◦ Stage 1 (recall): all:"retrieval augmented generation" OR all:RAG
 ◦ Stage 2 (precision): add abs: or add exclusions with ANDNOT
 • 



Tip: keep a small log of query iterations in `search_log.md` (string + timestamp + result count + what changed + filter rationale). See SKILL.md Step 1 for the required log format.
