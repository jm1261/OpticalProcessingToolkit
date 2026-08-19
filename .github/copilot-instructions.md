# Function Review

After creating or modifying a function, delegate the changed function to `DescriptionManager` before considering the task complete. Have it check the function's description, docstring clarity, parameter and return documentation, and consistency of type annotations with nearby code.

Keep the review focused on the changed function. Report actionable findings with file and line references, and do not make unrelated documentation or typing changes automatically.

# README Documentation

After creating or modifying a project directory, source file, or Python function, delegate the affected scope to `ProjectDocumentationManager` before considering the task complete. Have it update `README.md` with verified project, directory, file, function, setup, usage, and logging information, including the contents page.

Keep README updates limited to verified repository information. Preserve sections for other projects in the repository and do not invent undocumented behavior.