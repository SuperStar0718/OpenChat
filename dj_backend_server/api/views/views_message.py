from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from web.models.chatbot import Chatbot
import requests

class ChatbotResponse:
    def __init__(self, response):
        self.response = response

    def get_bot_reply(self):
        return self.response['text']

    def get_source_documents(self):
        return self.response.get('sourceDocuments', [])

@require_POST
def send_search_request(request):
    try:
        # Validate the request data
        message = request.POST.get('message')
        history = request.POST.getlist('history[]')

        # Implement the equivalent logic for validation
        if not message:
            return JsonResponse({
                'ai_response': "Message is required."
            }, status=400)
        # You can add additional validation for 'history' if needed.

        bot_token = request.headers.get('X-Bot-Token')
        bot = get_object_or_404(Chatbot, token=bot_token)

        # Implement the equivalent logic to send the HTTP request to the external API
        response = requests.post(
            'http://llm-server:3000/api/chat',
            json={
                'question': message,
                'namespace': str(bot.getId()),  # Assuming getId returns a UUID object
                'mode': "assistant",
                'initial_prompt': bot.getPromptMessage(),
                'history': history  # Assuming the API expects the chat history
            },
            timeout=200
        )

        bot_response = ChatbotResponse(response.json())

        return JsonResponse({
            'ai_response': bot_response.get_bot_reply()
        })

    except Exception as e:
        return JsonResponse({
            'ai_response': "Something went wrong, please try again later. If this issue persists, please contact support."
        }, status=500)

@require_POST
def init_chat(request):
    bot_token = request.headers.get('X-Bot-Token')
    bot = get_object_or_404(Chatbot, token=bot_token)

    return JsonResponse({
        "bot_name": bot.getName(),
        "logo": "logo",
        "faq": [],
        "initial_questions": []
    })

@require_POST
def send_chat(request):
    try:
        # Validate the request data
        content = request.POST.get('content')
        history = request.POST.getlist('history[]')
        content_type = request.POST.get('type')

        # Implement the equivalent logic for validation
        if not content:
            return JsonResponse({
                "type": "text",
                "response": {
                    "text": "Content is required."
                }
            }, status=400)
        # You can add additional validation for 'history' and 'content_type' if needed.

        bot_token = request.headers.get('X-Bot-Token')
        bot = get_object_or_404(Chatbot, token=bot_token)

        # Implement the equivalent logic to send the HTTP request to the external API
        response = requests.post(
            'http://llm-server:3000/api/chat',
            json={
                'question': content,
                'namespace': str(bot.getId()),  # Assuming getId returns a UUID object
                'mode': "assistant",
                'initial_prompt': bot.getPromptMessage(),
                'history': history
            },
            timeout=200
        )

        if response.json() is None:
            return JsonResponse({
                "type": "text",
                "response": {
                    "text": "The request was received successfully, but the LLM server was unable to handle it, please make sure your env keys are set correctly. **code: llm5XX**"
                }
            })

        bot_response = ChatbotResponse(response.json())

        return JsonResponse({
            "type": "text",
            "response": {
                "text": bot_response.get_bot_reply()
            }
        })

    except Exception as e:
        return JsonResponse({
            "type": "text",
            "response": {
                "text": "I'm unable to help you at the moment, please try again later.  **code: b404**"
            }
        }, status=500)