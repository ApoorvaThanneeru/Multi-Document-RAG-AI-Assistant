from __future__ import annotations

import logging
import re
import time

from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)

GENERATION_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
]

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    return _client


def _generate_with_fallback(prompt: str, temperature: float, max_tokens: int) -> str:
    """Try each model in the fallback list; retry once on rate-limit errors."""
    client = _get_client()
    last_error = None

    for model in GENERATION_MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    ),
                )
                return response.text
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    if attempt == 0:
                        logger.warning("Rate limited on %s, retrying in 5s...", model)
                        time.sleep(5)
                        continue
                    logger.warning("Rate limited on %s, trying next model", model)
                    break
                raise

    raise last_error


def _postprocess(text: str) -> str:
    """Strip inline source tags and reasoning artifacts from LLM output."""
    text = re.sub(r"\[Source:\s*[^\]]*\]", "", text)
    text = re.sub(r"\[Page\s*\d+\]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


SYSTEM_PROMPT = """\
You are an intelligent AI assistant designed for multi-document question answering and task execution using retrieved context.

CRITICAL OUTPUT RULES:
- Do NOT display internal reasoning, steps, classifications, or thinking process to the user.
- Do NOT label or mention intent type (Retrieval, Generation, Mixed) in your response.
- Do NOT include [Source: ...] tags inline within the answer text. Sources are handled separately by the system.
- Only return the FINAL polished answer. Nothing else.

INTENT HANDLING (internal only — never show this to the user):

For factual questions (who, what, when, where, details):
- Answer ONLY using the provided context.
- Do NOT hallucinate or add outside information.
- Extract only relevant details from the context.
- Combine information from multiple document chunks to build a complete answer.
- Avoid copying raw text verbatim; interpret, clean, and refine it.
- Remove duplicates and spaced-out/broken text artifacts.
- If limited information is available, say: "The documents provide limited information, but based on available data: ..."
- If no relevant information exists, say: "This information is not available in the provided documents."

For content creation tasks (write email, summarize, explain, rewrite):
- Return ONLY the requested output (e.g., only the email body, only the summary).
- Do NOT include unrelated extracted information, preambles, or extra context dumps.
- Generate a complete, polished, and professional response.
- Use context to inform the output, but fill gaps intelligently.

For mixed queries (facts + generated output):
- Use document context as the source of truth, then enhance with structured output.

ANSWER QUALITY:
- Always prioritize the most relevant information first.
- Keep answers concise but informative — do not overload with everything available.
- Use bullet points and structure when appropriate.
- Avoid repetition, unnecessary details, and verbose explanations.
- If the answer involves a list, limit to the 5–8 most relevant points, grouped logically.

SPECIAL CASES:
- If the query is vague, provide the most useful interpretation.
- If documents contain conflicting info, mention the uncertainty.
- For summarization: combine information from multiple chunks; do not rely on a single chunk. Infer complete meaning from partial context.
"""

CHAT_PROMPT_TEMPLATE = """{system_prompt}

DOCUMENT CONTEXT:
{context}

CONVERSATION HISTORY:
{chat_history}

USER QUERY: {question}

Respond with ONLY the final answer. Do not show reasoning steps or source tags."""

SUMMARIZE_PROMPT_TEMPLATE = """{system_prompt}

TASK: Summarize the following document.

DOCUMENT NAME: {document_name}

FULL DOCUMENT CONTENT:
{content}

Produce a well-organized summary with:
1. Main topics covered
2. Key points, details, and takeaways
3. Important policies, numbers, dates, or named entities

Use bullet points for clarity and rank by importance. Do not dump raw text. Do not include [Source:] tags."""


def generate_chat_response(
    question: str,
    context: str,
    chat_history: list[dict] | None = None,
) -> str:
    """Generate a response using Gemini with RAG context."""
    history_text = ""
    if chat_history:
        for msg in chat_history[-6:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_text += f"{role.upper()}: {content}\n"

    prompt = CHAT_PROMPT_TEMPLATE.format(
        system_prompt=SYSTEM_PROMPT,
        context=context,
        chat_history=history_text or "No previous conversation.",
        question=question,
    )

    return _postprocess(_generate_with_fallback(prompt, temperature=0.3, max_tokens=2048))


def generate_summary(document_name: str, content: str) -> str:
    """Generate a summary for a full document."""
    prompt = SUMMARIZE_PROMPT_TEMPLATE.format(
        system_prompt=SYSTEM_PROMPT,
        document_name=document_name,
        content=content,
    )

    return _postprocess(_generate_with_fallback(prompt, temperature=0.3, max_tokens=4096))
