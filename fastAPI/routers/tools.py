from fastapi import APIRouter, File, UploadFile, HTTPException
import os 
import dotenv
from pydantic import BaseModel
from typing import Union, List, Optional

from .unstrToStr import unstructerToStr
from .read_file import read_pdf, read_csv, read_txt, read_html, read_excel, read_json, read_xml, read_docx, read_pptx, read_markdown
from .codeInterpreter import code_interpret, upload_file_for_code_interpreter
from .rag import rag

from firecrawl import FirecrawlApp

router = APIRouter()
dotenv.load_dotenv()

app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))


class Struct(BaseModel):
    schema: str
    data: Union[str, List[str]]

class Crawl(BaseModel):
    url: str
    limit: Optional[int] = 7

class Map(BaseModel):
    url: str

class Code(BaseModel):
    code: str

class UserFile(BaseModel):
    file: UploadFile

class RAG(BaseModel):
    docs: List[str]

@router.post("/crawl/", tags=["tools"])
async def crawl(crawl: Crawl):
    """
    Crawls a website and returns the content of the page and the content of the pages linked on the page
    """

    first = app.scrape_url(crawl.url)
    links = first['linksOnPage']
    contents = []
    contents.append(first['content'])
    for link in links:
        if link == crawl.url:
            continue
        try:
            contents.append(app.scrape_url(link)['content'])
        except:
            continue
    return contents

@router.post("/map/", tags=["tools"])
async def map(map: Map):
    return app.scrape_url(map.url)['linksOnPage']

@router.post("/struct_str/", tags=["tools"])
async def struct(struct: Struct):
    return unstructerToStr(struct.schema, struct.data)

@router.post("/struct_array/", tags=["tools"])
async def struct(struct: Struct):

    call = struct.schema.split(' ')[1][:-1]

    res = [unstructerToStr(struct.schema, d) for d in range(struct.data)]

    for i in range(1, len(res)):

        for entry in res[i]['data']:
            if call in entry and call in res[0]['data'][0]:
                res[0]['data'].append(entry[call])
            else:
                res[0]['data'].append(entry)

    return res[0]

@router.post("/read/", tags=["tools"])
async def read(file: UploadFile = File(...)):
    fileType = file.filename.split('.')[-1].lower()

    file_content = await file.read()

    file_readers = {
        'pdf': read_pdf,
        'csv': read_csv,
        'txt': read_txt,
        'html': read_html,
        'excel': read_excel,
        'json': read_json,
        'xml': read_xml,
        'docx': read_docx,
        'pptx': read_pptx,
        'md': read_markdown,
        'xlsx': read_excel
    }

    try:
        reader = file_readers.get(fileType)
        if reader:
            content = reader(file_content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    finally:
        pass
    
    return {"filename": file.filename, "content": content}


@router.post("/code/", tags=["tools"])
async def code(code: Code):
    return code_interpret(code.code)

@router.post("/file_code/", tags=["tools"])
async def file(file: UserFile):
    return upload_file_for_code_interpreter(file.file_url)

@router.post("/rag/", tags=["tools"])
async def rag(rag: RAG):
    return rag(rag.docs)