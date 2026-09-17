import logging
import time

from groq import Groq
from groq import APIConnectionError, APITimeoutError, RateLimitError, APIStatusError

from backend.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Central Groq-backed LLM service used by the portal AI and RAG layers."""

    def __init__(self):
        self.model = settings.GROQ_MODEL
        self.client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
        self.system_prompt = """
You are the Corporate AI Assistant for an Employee Management Portal.

You assist employees, managers, HR staff, and administrators with:
Employee Management, Attendance, Leave, Payroll, Performance Reviews,
Departments, Documents, Onboarding, Offboarding, HR Policies, workplace
communication, professional emails, official letters, meeting summaries,
HR reports, and employee guidance.

Rules:
1. Be professional and concise.
2. Never invent company-specific facts.
3. When application data is supplied in context, use that data as the source of truth.
4. Clearly say when the required information is unavailable.
5. Use bullets or short sections when helpful.
""".strip()

    def ask(self, prompt: str, system_prompt: str | None = None) -> str:
        prompt = (prompt or "").strip()
        if not prompt:
            return "Please enter your question."

        if not self.client:
            logger.error("GROQ_API_KEY is not configured")
            return "The AI assistant is not configured. Please contact the administrator."

        messages = [
            {"role": "system", "content": system_prompt or self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=settings.GROQ_TEMPERATURE,
                    max_tokens=settings.GROQ_MAX_TOKENS,
                )
                answer = response.choices[0].message.content if response.choices else None
                if answer:
                    return answer.strip()
                return "The AI returned an empty response."
            except RateLimitError:
                if attempt == 2:
                    logger.warning("Groq rate limit reached")
                    return "The AI assistant is temporarily rate-limited. Please try again shortly."
                time.sleep(2 ** attempt)
            except (APIConnectionError, APITimeoutError):
                if attempt == 2:
                    logger.warning("Groq connection/timeout failure")
                    return "Sorry, the AI assistant is temporarily unavailable."
                time.sleep(2 ** attempt)
            except APIStatusError as exc:
                logger.error("Groq API returned status %s", getattr(exc, "status_code", "unknown"))
                return "Sorry, the AI service returned an error."
            except Exception:
                logger.exception("Unexpected Groq AI error")
                return "Sorry, the AI assistant is currently unavailable."

        return "Sorry, the AI assistant is currently unavailable."


llm = LLMService()
