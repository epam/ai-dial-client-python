from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.resources.chat.completions import (
    AsyncChatCompletions,
    ChatCompletions,
)


class Chat(Resource):
    completions: ChatCompletions


class AsyncChat(AsyncResource):
    completions: AsyncChatCompletions
