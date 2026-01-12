from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI
from sqlmodel import Session

from regulus_api.core.config import get_settings
from regulus_api.rag.retriever import semantic_search


@dataclass
class Citation:
    chunk_id: int
    file_id: int
    file_path: str
    start_line: int
    end_line: int
    score: float


def explain_with_citations(
    session: Session,
    repo_id: int,
    question: str,
    file_path: str | None = None,
) -> tuple[str, list[Citation]]:
    hits = semantic_search(session=session, repo_id=repo_id, query=question, file_path=file_path)
    citations = [
        Citation(
            chunk_id=hit.chunk_id,
            file_id=hit.file_id,
            file_path=hit.file_path,
            start_line=hit.start_line,
            end_line=hit.end_line,
            score=hit.score,
        )
        for hit in hits
    ]

    if not hits:
        return "No relevant context found for this question.", citations

    settings = get_settings()
    if settings.openai_api_key:
        client = OpenAI(api_key=settings.openai_api_key)
        context_blocks = [
            f"[{idx + 1}] {hit.file_path}:{hit.start_line}-{hit.end_line}\n{hit.content}"
            for idx, hit in enumerate(hits)
        ]
        system_prompt = (
            "You are a senior engineer answering questions about a codebase. "
            "Use only the provided context. Cite sources like [1], [2]."
        )
        user_prompt = f"Question: {question}\n\nContext:\n" + "\n\n".join(context_blocks)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        answer = response.choices[0].message.content or "No response from model."
        return answer, citations

    answer_lines = [
        "LLM not configured. Top retrieved context:",
    ]
    for idx, hit in enumerate(hits, start=1):
        answer_lines.append(
            f"[{idx}] {hit.file_path}:{hit.start_line}-{hit.end_line} (score {hit.score:.2f})"
        )
    return "\n".join(answer_lines), citations
