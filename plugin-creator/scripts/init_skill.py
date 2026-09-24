#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --path <path>
        [--resources scripts,references,assets]
        [--examples] [--interface key=value]

Examples:
    init_skill.py my-new-skill --path skills/public
    init_skill.py my-new-skill --path skills/public --resources scripts,references
    init_skill.py my-api-helper --path skills/private --resources scripts --examples
    init_skill.py custom-skill --path /custom/location
    init_skill.py my-skill --path skills/public --openai-yaml
    init_skill.py my-skill --path skills/public --openai-yaml \
        --interface short_description="Short UI label"
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_RESOURCES = {"scripts", "references", "assets"}

SKILL_TEMPLATE = """---
name: {skill_name}
description: >
  [TODO: Complete and informative explanation of what the skill does and when to use it.
  Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.]
---

# {skill_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Structuring This Skill

[TODO: Choose the structure that best fits this skill's purpose. Common patterns:

**1. Workflow-Based** (best for sequential processes)
- Works well when there are clear step-by-step procedures
- Example: DOCX skill with "Workflow Decision Tree" -> "Reading" -> "Creating" -> "Editing"
- Structure: ## Overview -> ## Workflow Decision Tree -> ## Step 1 -> ## Step 2...

**2. Task-Based** (best for tool collections)
- Works well when the skill offers different operations/capabilities
- Example: PDF skill with "Quick Start" -> "Merge PDFs" -> "Split PDFs" -> "Extract Text"
- Structure: ## Overview -> ## Quick Start -> ## Task Category 1 -> ## Task Category 2...

**3. Reference/Guidelines** (best for standards or specifications)
- Works well for brand guidelines, coding standards, or requirements
- Example: Brand styling with "Brand Guidelines" -> "Colors" -> "Typography" -> "Features"
- Structure: ## Overview -> ## Guidelines -> ## Specifications -> ## Usage...

**4. Capabilities-Based** (best for integrated systems)
- Works well when the skill provides multiple interrelated features
- Example: Product Management with "Core Capabilities" -> numbered capability list
- Structure: ## Overview -> ## Core Capabilities -> ### 1. Feature
  -> ### 2. Feature...

Patterns can be mixed and matched as needed. Most skills combine patterns
(e.g., start with task-based, add workflow for complex operations).

Delete this entire "Structuring This Skill" section when done - it's just guidance.]

## [TODO: Replace with the first main section based on chosen structure]

[TODO: Add content here. See examples in existing skills:
- Code samples for technical skills
- Decision trees for complex workflows
- Concrete examples with realistic user requests
- References to scripts/templates/references as needed]

## Resources (optional)

Create only the resource directories this skill actually needs. Delete this
section if no resources are required.

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py`
  - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that
performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still
be read by Codex for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to
inform Codex's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas,
comprehensive guides, or any detailed information that Codex should reference
while working.

### assets/
Files not intended to be loaded into context, but rather used within the output
Codex produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images,
icons, fonts, or any files meant to be copied or used in the final output.

---

**Not every skill requires all three types of resources.**
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example helper script for {skill_name}

This is a placeholder script that can be executed directly.
Replace with actual implementation or delete if not needed.

Example real scripts from other skills:
- pdf/scripts/fill_fillable_fields.py - Fills PDF form fields
- pdf/scripts/convert_pdf_to_images.py - Converts PDF pages to images
"""

def main():
    print("This is an example script for {skill_name}")
    # TODO: Add actual script logic here
    # This could be data processing, file conversion, API calls, etc.

if __name__ == "__main__":
    main()
'''

EXAMPLE_SCRIPT_NODE = """/**
 * Example helper script for {skill_name}
 *
 * Placeholder — replace with actual implementation or delete if not needed.
 */

function main(): void {{
  console.log("This is an example script for {skill_name}");
  // TODO: Add actual script logic here
}}

main();
"""

EXAMPLE_SCRIPT_SHELL = """#!/usr/bin/env sh
# Example helper script for {skill_name}
#
# Placeholder — replace with actual implementation or delete if not needed.
set -eu

main() {{
  echo "This is an example script for {skill_name}"
  # TODO: Add actual script logic here
}}

main "$@"
"""

# language -> (example filename, template, is-executable)
_EXAMPLE_SCRIPTS = {
    "python": ("example.py", EXAMPLE_SCRIPT, True),
    "node": ("example.ts", EXAMPLE_SCRIPT_NODE, False),
    "shell": ("example.sh", EXAMPLE_SCRIPT_SHELL, True),
}

EXAMPLE_REFERENCE = """# Reference Documentation for {skill_title}

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.

Example real reference docs from other skills:
- product-management/references/communication.md - Comprehensive guide for status updates
- product-management/references/context_building.md - Deep-dive on gathering context
- bigquery/references/ - API references and query examples

## When Reference Docs Are Useful

Reference docs are ideal for:
- Comprehensive API documentation
- Detailed workflow guides
- Complex multi-step processes
- Information too lengthy for main SKILL.md
- Content that's only needed for specific use cases

## Structure Suggestions

### API Reference Example
- Overview
- Authentication
- Endpoints with examples
- Error codes
- Rate limits

### Workflow Guide Example
- Prerequisites
- Step-by-step instructions
- Common patterns
- Troubleshooting
- Best practices
"""

EXAMPLE_ASSET = """# Example Asset File

This placeholder represents where asset files would be stored.
Replace with actual asset files (templates, images, fonts, etc.) or delete if not needed.

Asset files are NOT intended to be loaded into context, but rather used within
the output Codex produces.

Example asset files from other skills:
- Brand guidelines: logo.png, slides_template.pptx
- Frontend builder: hello-world/ directory with HTML/React boilerplate
- Typography: custom-font.ttf, font-family.woff2
- Data: sample_data.csv, test_dataset.json

## Common Asset Types

- Templates: .pptx, .docx, boilerplate directories
- Images: .png, .jpg, .svg, .gif
- Fonts: .ttf, .otf, .woff, .woff2
- Boilerplate code: Project directories, starter files
- Icons: .ico, .svg
- Data files: .csv, .json, .xml, .yaml

Note: This is a text placeholder. Actual assets can be any file type.
"""


def normalize_skill_name(skill_name: str) -> str:
    """Normalize a skill name to lowercase hyphen-case."""
    normalized = skill_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    return re.sub(r"-{2,}", "-", normalized)


def title_case_skill_name(skill_name: str) -> str:
    """Convert hyphenated skill name to Title Case for display."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def parse_resources(raw_resources: str) -> list[str]:
    if not raw_resources:
        return []
    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in resources if item not in ALLOWED_RESOURCES})
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_RESOURCES))
        print(f"[ERROR] Unknown resource type(s): {', '.join(invalid)}")
        print(f"   Allowed: {allowed}")
        sys.exit(1)
    deduped = []
    seen = set()
    for resource in resources:
        if resource not in seen:
            deduped.append(resource)
            seen.add(resource)
    return deduped


def create_single_resource(
    resource_dir: Path,
    resource: str,
    skill_name: str,
    skill_title: str,
    include_examples: bool,
    language: str = "python",
) -> None:
    """Create a single resource directory and optional examples."""
    resource_dir.mkdir(exist_ok=True)

    if not include_examples:
        print(f"[OK] Created {resource}/")
        return

    if resource == "scripts":
        filename, template, executable = _EXAMPLE_SCRIPTS[language]
        example_script = resource_dir / filename
        example_script.write_text(
            template.format(skill_name=skill_name), encoding="utf-8", newline="\n"
        )
        if executable:
            example_script.chmod(0o755)
        print(f"[OK] Created scripts/{filename}")
    elif resource == "references":
        example_reference = resource_dir / "api_reference.md"
        example_reference.write_text(
            EXAMPLE_REFERENCE.format(skill_title=skill_title), encoding="utf-8", newline="\n"
        )
        print("[OK] Created references/api_reference.md")
    elif resource == "assets":
        example_asset = resource_dir / "example_asset.txt"
        example_asset.write_text(EXAMPLE_ASSET, encoding="utf-8", newline="\n")
        print("[OK] Created assets/example_asset.txt")


def create_resource_dirs(
    skill_dir: Path,
    skill_name: str,
    skill_title: str,
    resources: list[str],
    include_examples: bool,
    language: str = "python",
) -> None:
    for resource in resources:
        resource_dir = skill_dir / resource
        create_single_resource(
            resource_dir, resource, skill_name, skill_title, include_examples, language
        )


def print_next_steps(
    skill_name: str,
    skill_dir: Path,
    resources: list[str],
    include_examples: bool,
    generate_openai: bool,
    plugin_json: bool = False,
) -> None:
    """Print post-initialization guidance."""
    print(f"\n[OK] Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md to complete the TODO items and update the description")

    if resources and include_examples:
        print("2. Customize or delete the example files in scripts/, references/, and assets/")
    elif resources:
        print("2. Add resources to scripts/, references/, and assets/ as needed")
    else:
        print("2. Create resource directories only if needed (scripts/, references/, assets/)")

    if generate_openai:
        print("3. Update agents/openai.yaml if the UI metadata should differ")
    else:
        print("3. To add OpenAI Codex UI metadata, re-run with --openai-yaml")
    print("4. Run the validator when ready to check the skill structure")
    if plugin_json:
        print(
            "5. Fill in the TODOs in .claude-plugin/plugin.json: name, description, "
            'author.name ("name": "Jane Doe" — a real full name, not a login) and '
            'author.email ("email": "jdoe@proofpoint.com") — the mandatory '
            "author-name and author-email checks fail until both are real"
        )


def create_plugin_json(skills_path: Path) -> Path | None:
    """Scaffold a bare ``.claude-plugin/plugin.json`` at the plugin root.

    ``--path`` points at the plugin's ``skills/`` dir, so the plugin root is its
    parent and the plugin name is that dir's name. Writes only the bare standard
    fields — no ``[<domain>]`` description prefix or ``<group> -`` author prefix
    (the pre-commit stamp hook adds those). ``author.name`` and ``author.email`` are
    left as TODOs: the mandatory ``author-name`` and ``author-email`` checks require a
    real full name and a real ``@proofpoint.com`` address, neither of which this script
    has any way to know, so the starter manifest fails both until they are filled in.
    Never clobbers an existing file.
    """
    if skills_path.name != "skills":
        print(
            f"[WARN] --plugin-json expects --path to be a plugin's 'skills/' dir; "
            f"got '{skills_path}'. Skipping plugin.json."
        )
        return None

    plugin_dir = skills_path.parent
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        print(f"[OK] plugin.json already exists, leaving it untouched: {plugin_json}")
        return plugin_json

    payload = {
        "name": normalize_skill_name(plugin_dir.name),
        "version": "0.1.0",
        "description": "TODO: one-line plugin description",
        # Both placeholders are deliberately gate-FAILING. The name is a SINGLE LOWERCASE
        # token so it fails BOTH of author-name's conditions (word count and capitalised
        # first word): "TODO: your name" satisfied the shape rule — as would "TODO: your
        # full name" — and would have shipped a fake-green display name to the marketplace.
        "author": {"name": "todo-set-author-full-name", "email": "TODO: your email"},
        "skills": "./skills",
    }
    plugin_json.parent.mkdir(parents=True, exist_ok=True)
    plugin_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] Created plugin.json: {plugin_json}")
    return plugin_json


def init_skill(
    skill_name: str,
    path: str,
    resources: list[str],
    include_examples: bool,
    language: str = "python",
    generate_openai: bool = False,
    interface_overrides: list[str] | None = None,
    plugin_json: bool = False,
) -> Path | None:
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created
        resources: Resource directories to create
        include_examples: Whether to create example files in resource directories
        language: Plugin language for scaffolded example scripts (python|node|shell)
        generate_openai: Whether to generate agents/openai.yaml (OpenAI Codex only)
        interface_overrides: Optional list of key=value overrides for openai.yaml

    Returns:
        Path to created skill directory, or None if error
    """
    if interface_overrides is None:
        interface_overrides = []
    # Determine skill directory path
    skill_dir = Path(path).resolve() / skill_name

    try:
        # Create skill directory
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"[OK] Created skill directory: {skill_dir}")
    except FileExistsError:
        print(f"[ERROR] Skill directory already exists: {skill_dir}")
        return None
    except Exception as e:
        print(f"[ERROR] Error creating directory: {e}")
        return None

    try:
        # Create SKILL.md from template
        skill_title = title_case_skill_name(skill_name)
        skill_content = SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)

        skill_md_path = skill_dir / "SKILL.md"
        skill_md_path.write_text(skill_content, encoding="utf-8", newline="\n")
        print("[OK] Created SKILL.md")

        # Create agents/openai.yaml (OpenAI Codex only, opt-in)
        if generate_openai:
            try:
                from generate_openai_yaml import write_openai_yaml
            except ImportError as exc:
                raise RuntimeError(
                    "PyYAML is required for --openai-yaml. "
                    "Install it with: pip install PyYAML==6.0.3"
                ) from exc
            result = write_openai_yaml(skill_dir, skill_name, interface_overrides)
            if not result:
                raise RuntimeError("Failed to create agents/openai.yaml")

        # Create resource directories if requested
        if resources:
            create_resource_dirs(
                skill_dir, skill_name, skill_title, resources, include_examples, language
            )

        # Scaffold the plugin's bare .claude-plugin/plugin.json if requested
        if plugin_json:
            create_plugin_json(Path(path).resolve())

    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        print("Rolling back changes...")
        if skill_dir.exists():
            shutil.rmtree(skill_dir)
        return None

    print_next_steps(
        skill_name, skill_dir, resources, include_examples, generate_openai, plugin_json
    )

    return skill_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a new skill directory with a SKILL.md template.",
    )
    parser.add_argument("skill_name", help="Skill name (normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Output directory for the skill")
    parser.add_argument(
        "--resources",
        default="",
        help="Comma-separated list: scripts,references,assets",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Create example files inside the selected resource directories",
    )
    parser.add_argument(
        "--language",
        choices=["python", "node", "shell"],
        default="python",
        help="Plugin language for the scaffolded example script "
        "(python->example.py, node->example.ts, shell->example.sh). Default: python",
    )
    parser.add_argument(
        "--openai-yaml",
        action="store_true",
        help="Generate agents/openai.yaml for OpenAI Codex UI metadata",
    )
    parser.add_argument(
        "--interface",
        action="append",
        default=[],
        help="Interface override in key=value format (repeatable, requires --openai-yaml)",
    )
    parser.add_argument(
        "--plugin-json",
        action="store_true",
        help="Also scaffold a bare .claude-plugin/plugin.json at the plugin root "
        "(--path must be the plugin's 'skills/' dir). Never clobbers an existing one.",
    )
    args = parser.parse_args()

    raw_skill_name = args.skill_name
    skill_name = normalize_skill_name(raw_skill_name)
    if not skill_name:
        print("[ERROR] Skill name must include at least one letter or digit.")
        sys.exit(1)
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        print(
            f"[ERROR] Skill name '{skill_name}' is too long ({len(skill_name)} characters). "
            f"Maximum is {MAX_SKILL_NAME_LENGTH} characters."
        )
        sys.exit(1)
    if skill_name != raw_skill_name:
        print(f"Note: Normalized skill name from '{raw_skill_name}' to '{skill_name}'.")

    resources = parse_resources(args.resources)
    if args.examples and not resources:
        print("[ERROR] --examples requires --resources to be set.")
        sys.exit(1)
    if args.interface and not args.openai_yaml:
        print("[ERROR] --interface requires --openai-yaml to be set.")
        sys.exit(1)

    path = args.path

    print(f"Initializing skill: {skill_name}")
    print(f"   Location: {path}")
    if resources:
        print(f"   Resources: {', '.join(resources)}")
        if args.examples:
            print("   Examples: enabled")
    else:
        print("   Resources: none (create as needed)")
    if args.openai_yaml:
        print("   OpenAI YAML: enabled")
    if args.plugin_json:
        print("   plugin.json: enabled")
    print()

    result = init_skill(
        skill_name,
        path,
        resources,
        args.examples,
        language=args.language,
        generate_openai=args.openai_yaml,
        interface_overrides=args.interface,
        plugin_json=args.plugin_json,
    )

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
