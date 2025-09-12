"""
Utility functions for handling GitHub wiki URLs and generating documents.
Used by the backend API

Author: Abe Moore Odell
"""
from urllib.parse import urlparse
from enum import Enum
import re
import tempfile
from multiprocessing import Process, Queue
import os
import shutil

import requests
from git import Repo
import mistune
from markdown_pdf import MarkdownPdf, Section


class DocumentType(Enum):
    """
    document types allowed to be created from wiki
    """
    MARKDOWN = "MARKDOWN"
    HTML = "HTML"
    PDF = "PDF"


def get_and_generate_wiki_document(candidate_url: str, doc_type: DocumentType) -> str:
    """
    Given a candidate url, ensure that it is a valid github wiki url
    If it is valid, clone the wiki and generate a document
    Inputs: candidate_url, str representing user inputted url to validate
    Returns: str the name of the generated file
    """
    safe_url = ensure_safe_url(candidate_url)

    with tempfile.TemporaryDirectory() as temp_dir:
        wiki_pages, wiki_url = clone_wiki(safe_url, temp_dir)
        md_path = write_markdown_file(wiki_pages, wiki_url)

        if doc_type == DocumentType.MARKDOWN:
            return md_path
        if doc_type == DocumentType.HTML:
            return markdown_to_html(md_path)
        if doc_type == DocumentType.PDF:
            return markdown_to_pdf(md_path)


def ensure_safe_url(candidate_url: str) -> str:
    """
    Semantic validation of user inputted url. Ensure it is valid github repo url.
    Pydantic already ensures that the url is validly formed
    Inputs: candidate_url, str representing user inputted url to validate
    Returns: string safe_url
    """
    candidate_url = candidate_url.strip().lower()

    parsed_url = urlparse(candidate_url)
    if parsed_url.netloc != "github.com":
        raise ValueError("Not a github url")

    pattern = r"^/([^/]+)/([^/]+)(/wiki)?(/.*)?$"
    match = re.match(pattern, parsed_url.path)
    if not match:
        raise ValueError("Not a valid github repo url")

    user, repo = match.groups()[0], match.groups()[1]
    wiki_url = f"https://github.com/{user}/{repo}/wiki"
    r = requests.head(wiki_url, timeout=3)
    if r.status_code != 200:
        raise ValueError("GitHub repo does not exist")

    safe_url = f"https://github.com/{user}/{repo}"
    return safe_url


def _clone_worker(wiki_url: str, temp_dir: str, q: Queue):
    """
    Worker function to clone the wiki in a separate process
    Puts the result (wiki_pages, error) in the queue
    """
    try:
        repo = Repo.clone_from(wiki_url, temp_dir)
        tree = repo.head.commit.tree
        wiki_pages = [(entry, entry.name, entry.type) for entry in tree]
        q.put((wiki_pages, None))
    except Exception as e:
        q.put((None, e))


def clone_wiki(safe_url: str, temp_dir: str, timeout: int = 5) -> tuple[list[tuple], str]:
    """
    Clones the wiki from the safe_url into the temp_dir
    Uses a separate process to enforce timeout if clone takes too long
    Returns a list of tuples containing (entry, name, type)
    """
    wiki_url = safe_url + ".wiki.git"
    q = Queue()
    p = Process(target=_clone_worker, args=(wiki_url, temp_dir, q))
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise TimeoutError(f"Cloning {wiki_url} exceeded {timeout} seconds")

    wiki_pages, error = q.get()
    if error:
        raise error
    if not wiki_pages:
        raise ValueError("Wiki is empty")

    return wiki_pages, wiki_url


def write_markdown_file(wiki_pages: list[tuple], wiki_url: str) -> str:
    """
    Given a list of wiki pages, write them to a markdown file
    Returns the name of the markdown file
    """
    with open("output.markdown", "w", encoding="utf-8") as f:
        f.write(f"Cloned from: {wiki_url}\n")
        for entry, name, type_ in wiki_pages:
            if type_ == "blob" and name.endswith(".md"):
                f.write(f"\n\n# {name}\n\n")
                blob_data = entry.data_stream.read().decode("utf-8")
                f.write(blob_data)
    return "output.markdown"


def markdown_to_html(md_path: str) -> str:
    """
    Converts markdown file of wiki to an HTML file, returns the HTML file name
    """
    with open(md_path, "r", encoding="utf-8") as md_file:
        md_content = md_file.read()

    markdown_parser = mistune.create_markdown(plugins=[
        'table',
        'strikethrough',
        'footnotes',
        'task_lists',
        'def_list',
        'url',
        'abbr',
        'mark',
        'insert',
        'superscript',
        'subscript',
        'math'])

    html = markdown_parser(md_content)

    with open("output.html", "w", encoding="utf-8") as html_file:
        html_file.write(html)

    return "output.html"


# TODO images and table formatting not working properly
def markdown_to_pdf(md_path: str) -> str:
    """
    Converts markdown file of wiki to a PDF file, returns the PDF file name
    """
    with open(md_path, "r", encoding="utf-8") as md_file:
        md_content = md_file.read()
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(md_content))
        pdf.save("output.pdf")
        return "output.pdf"
