"""
Utility functions for handling GitHub wiki URLs and generating documents.
Used by the backend API
"""
from urllib.parse import urlparse
from enum import Enum, auto
import re
import tempfile

import validators
import requests
from git import Repo
import markdown


class DocumentType(Enum):
    """
    Enum for different document types to be created from wiki.
    """
    MARKDOWN = auto()
    HTML = auto()
    PDF = auto()


def get_and_generate_wiki_document(candidate_url: str, doc_type: DocumentType):
    """
    Given a candidate url, ensure that it is a valid github wiki url
    If it is valid, clone the wiki and generate a document
    Inputs: candidate_url, str representing user inputted url to validate
    Returns: None
    """
    # 1. ensure that the url is valid
    safe_url = ensure_safe_url(candidate_url)
    # 2. create a temp directory to clone the wiki into
    with tempfile.TemporaryDirectory() as temp_dir:
        # 3. clone the wiki into the temp directory
        wiki_url = safe_url + ".wiki.git"
        repo = Repo.clone_from(wiki_url, temp_dir)
        tree = repo.head.commit.tree
        wiki_pages = [(entry, entry.name, entry.type) for entry in tree]

        if not wiki_pages:
            raise ValueError("Wiki is empty")

        # 4. create a file of the specified document type
        filename = f"output.{doc_type.name.lower()}"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Document type: {doc_type.name}\n")
            f.write(f"Cloned from: {wiki_url}\n")

            f.write("Files and directories in the wiki:\n")
            # 5. append each of the wiki pages to the output file
            for entry, name, type_ in wiki_pages:
                if type_ == "blob" and name.endswith(".md"):
                    # optional, acts as a separator
                    f.write(f"\n\n# {name}\n\n")
                    blob_data = entry.data_stream.read().decode("utf-8")
                    f.write(blob_data)

            if doc_type == DocumentType.MARKDOWN:
                return
            # 6. if doc_type is not markdown, convert output file
            # make sure to delete the markdown file once converted
            # f is currently the markdown file
            if doc_type == DocumentType.HTML:
                html = markdown.markdown(f.read())
                with open("output.html", "w", encoding="utf-8") as html_file:
                    html_file.write(html)
            if doc_type == DocumentType.PDF:
                raise NotImplementedError("PDF generation not implemented")


def ensure_safe_url(candidate_url: str) -> str:
    """
    Ensures that the url is valid, if it is not valid return an error
    if it is valid, ensure that it ends with "/wiki" and return the safe url
    Inputs: candidate_url, str representing user inputted url to validate
    Returns: safe url string if safe
    """
    candidate_url = candidate_url.strip().lower()
    # ensure that it is a valid url
    if not validators.url(candidate_url):
        raise ValueError("Not a legal url")
    # ensure that it is a github repo url
    parsed_url = urlparse(candidate_url)
    if parsed_url.netloc != "github.com":
        raise ValueError("Not a github url")
    # ensure that the url has a valid path to a repo or repo wiki
    # path should be of format "/{user_name}/{repo_name}/{optional wiki}/{optional others}"
    pattern = r"^/([^/]+)/([^/]+)(/wiki)?(/.*)?$"
    match = re.match(pattern, parsed_url.path)
    if not match:
        raise ValueError("Not a valid github repo url")

    user, repo = match.groups()[0], match.groups()[1]

    wiki_url = f"https://github.com/{user}/{repo}/wiki"

    # ensure that the wiki_url github repo and wiki exists
    r = requests.get(wiki_url, timeout=3)
    if r.status_code != 200:
        raise ValueError("GitHub repo does not exist")

    safe_url = f"https://github.com/{user}/{repo}"
    return safe_url


get_and_generate_wiki_document(
    "https://github.com/abemo/export-wiki/wiki/Introduction",
    DocumentType.HTML)
