"""
Lab 11 — Helper Utilities
"""
from core.config import get_llm_provider, PROVIDER_OPENROUTER  # noqa: F401
from core.openai_runtime import OpenAIRunner, OpenAIChatSession


async def chat_with_agent(agent, runner, user_message: str, session_id=None):
    """Send a message to the agent and get the response.

    Works with OpenAIRunner (OpenAI Red / OpenRouter Blue) and Google ADK (Gemini Red).
    """
    provider = getattr(runner, "provider", None)
    if isinstance(runner, OpenAIRunner) or provider in ("openrouter", "openai"):
        session = session_id if isinstance(session_id, OpenAIChatSession) else OpenAIChatSession()
        text = await runner.chat(agent, user_message, session=session)
        return text, session

    from google.genai import types

    user_id = "student"
    app_name = runner.app_name

    session = None
    if session_id is not None:
        try:
            session = await runner.session_service.get_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )
        except (ValueError, KeyError):
            pass

    if session is None:
        try:
            session = await runner.session_service.create_session(
                app_name=app_name, user_id=user_id
            )
        except Exception:
            session = await runner.session_service.create_session(
                app_name=app_name, user_id=user_id
            )

    import asyncio

    max_retries = 5
    for attempt in range(max_retries):
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )

        final_response = ""
        try:
            async for event in runner.run_async(
                user_id=user_id, session_id=session.id, new_message=content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if getattr(part, "text", None) and not getattr(part, "thought", False):
                            final_response += part.text
            return final_response, session
        except Exception as exc:
            err_str = f"{type(exc).__name__}: {exc}".lower()
            is_transient = any(
                k in err_str
                for k in (
                    "503", "unavailable", "429", "resource_exhausted",
                    "resourceexhausted", "deadline", "high demand", "servererror", "quota",
                )
            )
            if not is_transient or attempt == max_retries - 1:
                raise
            wait_sec = 15 * (attempt + 1)
            print(f"  [Gemini rate limit / 503 — đợi {wait_sec}s để reset quota rồi thử lại ({attempt + 1}/{max_retries - 1})...]")
            await asyncio.sleep(wait_sec)
            if session_id is None:
                try:
                    session = await runner.session_service.create_session(
                        app_name=app_name, user_id=user_id
                    )
                except Exception:
                    pass

    return final_response, session
