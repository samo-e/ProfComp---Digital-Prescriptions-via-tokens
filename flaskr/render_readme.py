"""
Takes readme.md and renders it to two files
    help-student.html
    help-teacher.html
"""

from markdown_it import MarkdownIt
from pathlib import Path
import re

md = MarkdownIt("commonmark").enable("table")


def strip_flag(content: str, flag: str, strip_content=True):
    """
    Removes certain flags from the html by checking
        <!-- {flag}_START -->(.*?)<!-- {flag}_END -->'
    Flags include
    MD_ONLY : Does not display on website at all
    TEACHER_ONLY_START : Only displays if the user is logged in and a teacher
    STUDENT_ONLY_START : Only displays if the user is logged in and a student

    strip_content:
        if True: remove all the text between,
        else: remove just the comments
    """
    if strip_content:
        return re.sub(
            rf"<!-- {flag}_START -->(.*?)<!-- {flag}_END -->",
            "",
            content,
            flags=re.DOTALL,
        )
    else:
        return re.sub(
            rf"<!-- {flag}_START -->(.*?)<!-- {flag}_END -->",
            r"\1",
            content,
            flags=re.DOTALL,
        )


def table_open(tokens, idx, options, env):
    return '<table class="table table-striped table-bordered">\n'


def fence(tokens, idx, options, env):
    token = tokens[idx]
    lang_class = f"language-{token.info.strip()}" if token.info else ""
    return f'<pre class="p-3 bg-light border rounded"><code class="{lang_class}">{token.content}</code></pre>\n'


def render_readme():
    """
    Renders README.md as a html page and outputs to the two files
    """
    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    md.renderer.rules["table_open"] = table_open
    md.renderer.rules["fence"] = fence

    outputs = {"teacher": True, "student": False}

    templates_dir = (
        Path(__file__).resolve().parents[0] / "website" / "templates" / "views" / "help"
    )
    templates_dir.mkdir(parents=True, exist_ok=True)
    for file, is_teacher in outputs.items():
        this_content = strip_flag(content, "TEACHER_ONLY", not is_teacher)
        this_content = strip_flag(this_content, "MD_ONLY")

        html = md.render(this_content)

        output_file = templates_dir / f"help-{file}.html"
        output_file.write_text(html, encoding="utf-8")
