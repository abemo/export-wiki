"""
controller API for export-wiki

TODO https://www.geeksforgeeks.org/python/creating-first-rest-api-with-fastapi/ 
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from model.util import get_and_generate_wiki_document, DocumentType

app = FastAPI()

origins = [

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/export")
def export_wiki_from_url(
        wiki_url: str,
        doc_type: DocumentType,
        background_tasks: BackgroundTasks
):
    """
    Given a wiki url and document type, validate the url, clone the wiki,
    generate the document, and return the document as a file response.
    Inputs: wiki_url, str representing user inputted url to validate
            doc_type, DocumentType enum representing the type of document to create
    Returns: FileResponse, the generated document file
    """
    try:
        file_name = get_and_generate_wiki_document(wiki_url, doc_type)

        if not os.path.exists(file_name):
            raise HTTPException(
                status_code=500, detail="File generation failed")

        background_tasks.add_task(os.remove, file_name)

        if os.path.exists("output.markdown"):
            background_tasks.add_task(os.remove, "output.markdown")

        return FileResponse(
            path=file_name,
            media_type={
                "MARKDOWN": "text/markdown",
                "HTML": "text/html",
                "PDF": "application/pdf"
            }[doc_type.value],
            filename=file_name
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
