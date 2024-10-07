import requests
from typing import Any, AnyStr, Type
from pypdf import PdfReader
import spacy
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from gentopia.tools.basetool import BaseTool
from pydantic import BaseModel, Field
import os
import subprocess

subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
nlp = spacy.load("en_core_web_sm")

class PDFReaderArgs(BaseModel):
    pdf_url: str = Field(..., description="URL of the PDF file to download and summarize")
    summarize: bool = Field(default=True, description="Summarize the content of the PDF")

class PDFReaderAndSummarizer(BaseTool):
    """Tool that downloads a PDF from a URL, reads it, and summarizes the content."""

    name = "pdf_reader_and_summarizer"
    description = ("A PDF reader and summarizer that downloads a PDF, extracts its text, and summarizes the content.")

    args_schema: Type[BaseModel] = PDFReaderArgs

    def _load_pdf(self, pdf_url: str, output_file: str) -> str:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return output_file
        else:
            raise Exception(f"Failed to download PDF")

    def _read_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def _summarize_text(self, text: str, sentence_count: int = 3000) -> str:
        doc = nlp(text)
        sentences = [s.text for s in doc.sents]
        summary = ' '.join(sentences[:sentence_count])
        return summary

    def _run(self, pdf_url: AnyStr, summarize: bool = True) -> str:
        output_file = "paper.pdf"
        try:
            paper_pdf = self._load_pdf(pdf_url, output_file)
        except Exception as e:
            return f"Error downloading PDF: {e}"
        try:
            text = self._read_pdf(paper_pdf)
        except Exception as e:
            return f"Error reading PDF: {e}"
        if summarize:
            try:
                summary = self._summarize_text(text)
                os.remove(paper_pdf)
                return f"Summary:\n{summary}"
            except ValueError:
                os.remove(paper_pdf)
                return "The document is too short."

        os.remove(paper_pdf)
        return text

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

if __name__ == "__main__":
    pdf_url = "https://arxiv.org/pdf/1905.12688" #Placeholder
    summarizer = PDFReaderAndSummarizer()
    result = summarizer._run(pdf_url, summarize=True)
    print(result)
