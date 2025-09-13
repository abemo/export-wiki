"""
controller API for export-wiki

Author: Abe Moore Odell 
"""

import os
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exception_handlers import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, AnyUrl
from util import get_and_generate_wiki_document, DocumentType

limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

origins = [
    "https://abemo.github.io",
    "https://abemo.github.io/export-wiki/",
    "https://www.abemo.github.io/export-wiki/",
    "http://localhost",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "Authorization"],
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        return response


app.add_middleware(SecurityHeadersMiddleware)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse({
        "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "UNKNOWN"),
        "message": "An error occurred. Please try again."
    })


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    error_message = "Validation error: " + str(exc)
    logger.warning(error_message)
    return JSONResponse(
        status_code=422,
        content={"error": "INVALID_INPUT",
                 "message": "Invalid request parameters."}
    )


@app.get("/")
async def health_check():
    return {"status": "ok"}


class ConstrainedUrl(AnyUrl):
    max_length = 300


class ExportRequest(BaseModel):
    wiki_url: ConstrainedUrl
    doc_type: DocumentType


@app.post("/export")
@limiter.limit("5/minute")
async def export_wiki_from_url(
        request: Request,
        export_request: ExportRequest,
        background_tasks: BackgroundTasks
):
    """
    Given a wiki url and document type, validate the url, clone the wiki,
    generate the document, and return the document as a file response.
    Inputs: wiki_url, str representing user inputted url to validate
            doc_type, DocumentType enum representing the type of document to create
    Returns: FileResponse, the generated document file
    """
    wiki_url = str(export_request.wiki_url)
    doc_type = export_request.doc_type

    try:
        file_name = get_and_generate_wiki_document(wiki_url, doc_type)

        if not os.path.exists(file_name):
            raise HTTPException(
                status_code=500, detail="File generation failed")

        background_tasks.add_task(os.remove, file_name)

        if doc_type != DocumentType.MARKDOWN and os.path.exists("output.markdown"):
            background_tasks.add_task(os.remove, "output.markdown")

        return FileResponse(
            path=file_name,
            media_type={
                "MARKDOWN": "text/markdown",
                "HTML": "text/html",
                "PDF": "application/pdf"
            }[doc_type.value],
            filename=file_name,
            background=background_tasks
        )
    except Exception as e:
        logger.exception("Error exporting wiki")
        raise HTTPException(
            status_code=400,
            detail={"error": "EXPORT_FAILED",
                    "message": "Failed to export wiki"}) from e
