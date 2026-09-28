#!/usr/bin/env python3
"""Stamp the canonical Framework sidebar into every Framework article."""

from pathlib import Path
import os
import re

ROOT = Path(__file__).parent
FRAMEWORK = ROOT / "framework"
SECTIONS = (
    ("Foundations", (("index.html", "Overview"), ("what-is-autonomous-ai.html", "What is autonomous AI"), ("the-autonomy-spectrum.html", "The autonomy spectrum"), ("glossary.html", "Glossary"))),
    ("Claude", (("claude/overview.html", "Overview"), ("claude/prompting-for-agents.html", "Prompting for agents"), ("claude/extended-thinking.html", "Extended thinking"), ("claude/tool-use.html", "Tool use"))),
    ("MCP", (("mcp/index.html", "Overview"), ("mcp/what-is-mcp.html", "What is MCP"), ("mcp/anatomy.html", "Anatomy"), ("mcp/transports.html", "Transports"), ("mcp/servers.html", "Servers"), ("mcp/clients.html", "Clients"), ("mcp/security.html", "Security"), ("mcp/directory.html", "Directory"))),
    ("Plugins", (("plugins/index.html", "Overview"), ("plugins/vs-mcp.html", "Plugins vs MCP"), ("plugins/marketplace.html", "Marketplace"))),
    ("Claude Code", (("claude-code/index.html", "Overview"), ("claude-code/settings.html", "Settings"), ("claude-code/permissions.html", "Permissions"), ("claude-code/hooks.html", "Hooks"), ("claude-code/subagents.html", "Subagents"), ("claude-code/skills.html", "Skills"), ("claude-code/memory.html", "Memory"))),
    ("Patterns", (("patterns/index.html", "Overview"), ("patterns/react-loop.html", "ReAct loop"), ("patterns/plan-execute.html", "Plan-execute"), ("patterns/multi-agent.html", "Multi-agent"), ("patterns/evaluation.html", "Evaluation"), ("patterns/prompt-caching.html", "Prompt caching"), ("patterns/context-engineering.html", "Context engineering"))),
    ("Autonomous", (("autonomous/index.html", "Overview"), ("autonomous/headless.html", "Headless"), ("autonomous/scheduling.html", "Scheduling"), ("autonomous/self-monitoring.html", "Self-monitoring"), ("autonomous/safety.html", "Safety"))),
    ("Build Guides", (("build/index.html", "Overview"), ("build/first-agent.html", "First agent (60 min)"), ("build/first-skill.html", "Write your first skill"), ("build/mcp-server.html", "Build an MCP server"), ("build/agent-sdk.html", "The Claude Agent SDK"), ("build/voice-agent.html", "Voice agent"), ("build/research-agent.html", "Research agent"))),
    ("Tools", (("tools/browser-automation.html", "Browser automation"), ("tools/desktop-control.html", "Desktop control"), ("tools/local-models.html", "Local and open models (Ollama)"))),
)

def sidebar(page: Path) -> str:
    current = page.relative_to(FRAMEWORK).as_posix()
    blocks = ['<aside class="framework-sidebar">']
    for heading, links in SECTIONS:
        blocks.extend((f"<h4>{heading}</h4>", "<ul>"))
        for target, label in links:
            href = os.path.relpath(FRAMEWORK / target, page.parent).replace(os.sep, "/")
            active = ' class="active"' if target == current else ""
            blocks.append(f'<li><a href="{href}"{active}>{label}</a></li>')
        blocks.append("</ul>")
    blocks.append("</aside>")
    return "".join(blocks)

def main() -> None:
    pattern = re.compile(r'<aside class="framework-sidebar">.*?</aside>', re.DOTALL)
    for page in FRAMEWORK.rglob("*.html"):
        original = page.read_text()
        updated, count = pattern.subn(sidebar(page), original, count=1)
        if count == 0:
            # Section landing pages use their own hub layout and have no sidebar
            # to replace.
            continue
        if count != 1:
            raise RuntimeError(f"Expected one sidebar in {page}")
        if updated != original:
            page.write_text(updated)

if __name__ == "__main__":
    main()
