import logging

from django.conf import settings
from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError


logger = logging.getLogger(__name__)


class OpenAIChatClient:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError('OPENAI_API_KEY no esta configurada')

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def create_response(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=600,
            )
        except RateLimitError:
            return 'Estoy recibiendo muchas solicitudes. Intenta nuevamente en unos segundos.'
        except APIConnectionError:
            return 'No pude conectarme al servicio de IA. Intenta nuevamente.'
        except APIStatusError as error:
            logger.warning(
                'OpenAI API status error: status=%s body=%s',
                error.status_code,
                error.response.text,
            )
            return 'El servicio de IA no pudo procesar la solicitud.'

        return response.choices[0].message.content
