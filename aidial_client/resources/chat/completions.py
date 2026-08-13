from collections.abc import AsyncIterable, Iterable, Mapping
from typing import (
    Any,
    Literal,
    cast,
    overload,
)

import openai
from openai import AsyncStream as OpenaiAsyncStream
from openai import Stream as OpenaiStream
from openai.types.chat import ChatCompletion as OpenaiChatCompletion
from openai.types.chat import ChatCompletionChunk as OpenaiChatCompletionChunk
from pydantic import StrictStr

from aidial_client._compatibility.openai import Omit
from aidial_client._utils._dict import remove_none
from aidial_client._utils._openai import (
    convert_openai_async_stream,
    convert_openai_error,
    convert_openai_response,
    convert_openai_stream,
)
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.chat import (
    ChatCompletionChunk,
    ChatCompletionResponse,
    FunctionCallSpecParam,
    FunctionParam,
    Message,
    PromptCacheOptionsParam,
    ReasoningEffort,
    ResponseFormat,
    StaticToolParam,
    StreamOptions,
    ToolCallSpecParam,
    ToolParam,
)
from aidial_client.types.chat.request import ChatCompletionRequestCustomFields


class ChatCompletions(Resource):
    default_api_version: str | None = None
    openai_client: openai.AzureOpenAI

    @overload
    def create(
        self,
        *,
        deployment_name: str,
        messages: list[Message],
        stream: Literal[True],
        api_version: str | None = None,
        model: str | None = None,
        functions: list[FunctionParam] | None = None,
        function_call: Literal["none", "auto"]
        | FunctionCallSpecParam
        | None = None,
        tools: list[ToolParam | StaticToolParam] | None = None,
        tool_choice: Literal["none", "auto", "required"]
        | ToolCallSpecParam
        | None = None,
        parallel_tool_calls: bool | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        n: int | None = None,
        stop: str | list[str] | None = None,
        max_tokens: int | None = None,
        max_completion_tokens: int | None = None,
        max_prompt_tokens: Literal["infinity"] | int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        logit_bias: dict | None = None,
        seed: int | None = None,
        user: str | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        prompt_cache_key: str | None = None,
        prompt_cache_options: PromptCacheOptionsParam | None = None,
        response_format: ResponseFormat | None = None,
        stream_options: StreamOptions | None = None,
        custom_fields: ChatCompletionRequestCustomFields | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        # Extra params
        extra_body: dict[str, Any] | None = None,
        extra_headers: Mapping[StrictStr, StrictStr] | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> Iterable[ChatCompletionChunk]: ...

    @overload
    def create(
        self,
        *,
        deployment_name: str,
        messages: list[Message],
        stream: Literal[False],
        api_version: str | None = None,
        model: str | None = None,
        functions: list[FunctionParam] | None = None,
        function_call: Literal["none", "auto"]
        | FunctionCallSpecParam
        | None = None,
        tools: list[ToolParam | StaticToolParam] | None = None,
        tool_choice: Literal["none", "auto", "required"]
        | ToolCallSpecParam
        | None = None,
        parallel_tool_calls: bool | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        n: int | None = None,
        stop: str | list[str] | None = None,
        max_tokens: int | None = None,
        max_completion_tokens: int | None = None,
        max_prompt_tokens: Literal["infinity"] | int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        logit_bias: dict | None = None,
        seed: int | None = None,
        user: str | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        prompt_cache_key: str | None = None,
        prompt_cache_options: PromptCacheOptionsParam | None = None,
        response_format: ResponseFormat | None = None,
        stream_options: StreamOptions | None = None,
        custom_fields: ChatCompletionRequestCustomFields | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        # Extra params
        extra_body: dict[str, Any] | None = None,
        extra_headers: Mapping[StrictStr, StrictStr] | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> ChatCompletionResponse: ...

    def create(
        self,
        *,
        deployment_name: str,
        messages: list[Message],
        api_version: str | None = None,
        stream: bool = False,
        model: str | None = None,
        functions: list[FunctionParam] | None = None,
        function_call: Literal["none", "auto"]
        | FunctionCallSpecParam
        | None = None,
        tools: list[ToolParam | StaticToolParam] | None = None,
        tool_choice: Literal["none", "auto", "required"]
        | ToolCallSpecParam
        | None = None,
        parallel_tool_calls: bool | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        n: int | None = None,
        stop: str | list[str] | None = None,
        max_tokens: int | None = None,
        max_completion_tokens: int | None = None,
        max_prompt_tokens: Literal["infinity"] | int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        logit_bias: dict | None = None,
        seed: int | None = None,
        user: str | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        prompt_cache_key: str | None = None,
        prompt_cache_options: PromptCacheOptionsParam | None = None,
        response_format: ResponseFormat | None = None,
        stream_options: StreamOptions | None = None,
        custom_fields: ChatCompletionRequestCustomFields | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        # Extra params
        extra_body: dict[str, Any] | None = None,
        extra_headers: Mapping[StrictStr, StrictStr] | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> ChatCompletionResponse | Iterable[ChatCompletionChunk]:
        model = model or deployment_name
        extra_body = extra_body or {}
        extra_headers = extra_headers or {}
        extra_params = extra_params or {}

        input_params = remove_none(
            {
                "messages": messages,
                "model": model,
                "frequency_penalty": frequency_penalty,
                "function_call": function_call,
                "functions": functions,
                "logit_bias": logit_bias,
                "max_tokens": max_tokens,
                "n": n,
                "presence_penalty": presence_penalty,
                "seed": seed,
                "stop": stop,
                "stream": stream,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "tools": tools,
                "top_p": top_p,
                "user": user,
                "logprobs": logprobs,
                "top_logprobs": top_logprobs,
                # DIAL-specific parameters and the ones which aren't supported
                # by every openai version are sent in the request body directly
                "extra_body": {
                    **remove_none(
                        {
                            "max_prompt_tokens": max_prompt_tokens,
                            "custom_fields": custom_fields,
                            "max_completion_tokens": max_completion_tokens,
                            "parallel_tool_calls": parallel_tool_calls,
                            "reasoning_effort": reasoning_effort,
                            "prompt_cache_key": prompt_cache_key,
                            "prompt_cache_options": prompt_cache_options,
                            "response_format": response_format,
                            "stream_options": stream_options,
                        }
                    ),
                    **extra_body,
                },
                "extra_query": {
                    "api-version": (
                        api_version or self.default_api_version or Omit()
                    )
                },
                "extra_headers": {
                    # We use Omit to override openai client auth headers
                    **{"Authorization": Omit(), "api-key": Omit()},
                    **(self.http_client.auth_headers()),
                    **extra_headers,
                },
            }
        )
        try:
            openai_response = self.openai_client.chat.completions.create(
                **input_params,
            )
            openai_response = cast(
                OpenaiChatCompletion | OpenaiStream[OpenaiChatCompletionChunk],
                openai_response,
            )
        except openai.APIError as err:
            raise convert_openai_error(err)

        if isinstance(openai_response, OpenaiChatCompletion):
            return convert_openai_response(openai_response)
        else:
            return convert_openai_stream(openai_response)


class AsyncChatCompletions(AsyncResource):
    default_api_version: str | None = None
    openai_client: openai.AsyncAzureOpenAI

    @overload
    async def create(
        self,
        *,
        deployment_name: str,
        messages: list[Message],
        stream: Literal[True],
        api_version: str | None = None,
        model: str | None = None,
        functions: list[FunctionParam] | None = None,
        function_call: Literal["none", "auto"]
        | FunctionCallSpecParam
        | None = None,
        tools: list[ToolParam | StaticToolParam] | None = None,
        tool_choice: Literal["none", "auto", "required"]
        | ToolCallSpecParam
        | None = None,
        parallel_tool_calls: bool | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        n: int | None = None,
        stop: str | list[str] | None = None,
        max_tokens: int | None = None,
        max_completion_tokens: int | None = None,
        max_prompt_tokens: Literal["infinity"] | int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        logit_bias: dict | None = None,
        seed: int | None = None,
        user: str | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        prompt_cache_key: str | None = None,
        prompt_cache_options: PromptCacheOptionsParam | None = None,
        response_format: ResponseFormat | None = None,
        stream_options: StreamOptions | None = None,
        custom_fields: ChatCompletionRequestCustomFields | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        # Extra params
        extra_body: dict[str, Any] | None = None,
        extra_headers: Mapping[StrictStr, StrictStr] | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> AsyncIterable[ChatCompletionChunk]: ...

    @overload
    async def create(
        self,
        *,
        deployment_name: str,
        messages: list[Message],
        stream: Literal[False],
        api_version: str | None = None,
        model: str | None = None,
        functions: list[FunctionParam] | None = None,
        function_call: Literal["none", "auto"]
        | FunctionCallSpecParam
        | None = None,
        tools: list[ToolParam | StaticToolParam] | None = None,
        tool_choice: Literal["none", "auto", "required"]
        | ToolCallSpecParam
        | None = None,
        parallel_tool_calls: bool | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        n: int | None = None,
        stop: str | list[str] | None = None,
        max_tokens: int | None = None,
        max_completion_tokens: int | None = None,
        max_prompt_tokens: Literal["infinity"] | int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        logit_bias: dict | None = None,
        seed: int | None = None,
        user: str | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        prompt_cache_key: str | None = None,
        prompt_cache_options: PromptCacheOptionsParam | None = None,
        response_format: ResponseFormat | None = None,
        stream_options: StreamOptions | None = None,
        custom_fields: ChatCompletionRequestCustomFields | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        # Extra params
        extra_body: dict[str, Any] | None = None,
        extra_headers: Mapping[StrictStr, StrictStr] | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> ChatCompletionResponse: ...

    async def create(
        self,
        *,
        deployment_name: str,
        messages: list[Message],
        api_version: str | None = None,
        stream: bool = False,
        model: str | None = None,
        functions: list[FunctionParam] | None = None,
        function_call: Literal["none", "auto"]
        | FunctionCallSpecParam
        | None = None,
        tools: list[ToolParam | StaticToolParam] | None = None,
        tool_choice: Literal["none", "auto", "required"]
        | ToolCallSpecParam
        | None = None,
        parallel_tool_calls: bool | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        n: int | None = None,
        stop: str | list[str] | None = None,
        max_tokens: int | None = None,
        max_completion_tokens: int | None = None,
        max_prompt_tokens: Literal["infinity"] | int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        logit_bias: dict | None = None,
        seed: int | None = None,
        user: str | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        prompt_cache_key: str | None = None,
        prompt_cache_options: PromptCacheOptionsParam | None = None,
        response_format: ResponseFormat | None = None,
        stream_options: StreamOptions | None = None,
        custom_fields: ChatCompletionRequestCustomFields | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        # Extra params
        extra_body: dict[str, Any] | None = None,
        extra_headers: Mapping[StrictStr, StrictStr] | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> ChatCompletionResponse | AsyncIterable[ChatCompletionChunk]:
        model = model or deployment_name
        extra_body = extra_body or {}
        extra_headers = extra_headers or {}
        extra_params = extra_params or {}

        input_params = remove_none(
            {
                "messages": messages,
                "model": model,
                "frequency_penalty": frequency_penalty,
                "function_call": function_call,
                "functions": functions,
                "logit_bias": logit_bias,
                "max_tokens": max_tokens,
                "n": n,
                "presence_penalty": presence_penalty,
                "seed": seed,
                "stop": stop,
                "stream": stream,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "tools": tools,
                "top_p": top_p,
                "user": user,
                "logprobs": logprobs,
                "top_logprobs": top_logprobs,
                # DIAL-specific parameters and the ones which aren't supported
                # by every openai version are sent in the request body directly
                "extra_body": {
                    **remove_none(
                        {
                            "max_prompt_tokens": max_prompt_tokens,
                            "custom_fields": custom_fields,
                            "max_completion_tokens": max_completion_tokens,
                            "parallel_tool_calls": parallel_tool_calls,
                            "reasoning_effort": reasoning_effort,
                            "prompt_cache_key": prompt_cache_key,
                            "prompt_cache_options": prompt_cache_options,
                            "response_format": response_format,
                            "stream_options": stream_options,
                        }
                    ),
                    **extra_body,
                },
                "extra_query": {
                    "api-version": (
                        api_version or self.default_api_version or Omit()
                    )
                },
                "extra_headers": {
                    # We use Omit to override openai client auth headers
                    **{"Authorization": Omit(), "api-key": Omit()},
                    **(await self.http_client.auth_headers()),
                    **extra_headers,
                },
            }
        )
        try:
            openai_response = await self.openai_client.chat.completions.create(
                **input_params,
            )
            openai_response = cast(
                OpenaiChatCompletion
                | OpenaiAsyncStream[OpenaiChatCompletionChunk],
                openai_response,
            )
        except openai.APIError as err:
            raise convert_openai_error(err)

        if isinstance(openai_response, OpenaiChatCompletion):
            return convert_openai_response(openai_response)
        else:
            return convert_openai_async_stream(openai_response)
