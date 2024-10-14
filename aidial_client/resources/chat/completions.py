from typing import (
    Any,
    AsyncIterable,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Union,
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
    Addon,
    ChatCompletionChunk,
    ChatCompletionResponse,
    FunctionCallSpecParam,
    FunctionParam,
    Message,
    ToolCallSpecParam,
    ToolParam,
)
from aidial_client.types.chat.request import ChatCompletionRequestCustomFields


class ChatCompletions(Resource):
    default_api_version: Optional[str] = None
    openai_client: openai.AzureOpenAI

    @overload
    def create(
        self,
        *,
        deployment_name: str,
        messages: List[Message],
        stream: Literal[True],
        api_version: Optional[str] = None,
        model: Optional[str] = None,
        functions: Union[List[FunctionParam], None] = None,
        function_call: Union[
            Union[Literal["none", "auto"], FunctionCallSpecParam], None
        ] = None,
        tools: Union[List[ToolParam], None] = None,
        tool_choice: Union[
            Union[Literal["none", "auto"], ToolCallSpecParam], None
        ] = None,
        addons: Union[Addon, None] = None,
        temperature: Union[float, None] = None,
        top_p: Union[float, None] = None,
        n: Union[int, None] = None,
        stop: Union[Union[str, List[str]], None] = None,
        max_tokens: Union[int, None] = None,
        max_prompt_tokens: Union[Union[Literal["infinity"], int], None] = None,
        presence_penalty: Union[float, None] = None,
        frequency_penalty: Union[float, None] = None,
        logit_bias: Union[Dict, None] = None,
        seed: Union[int, None] = None,
        user: Union[str, None] = None,
        custom_fields: Union[ChatCompletionRequestCustomFields, None] = None,
        logprobs: Union[bool, None] = None,
        top_logprobs: Union[int, None] = None,
        # Extra params
        extra_body: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Mapping[StrictStr, StrictStr]] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Iterable[ChatCompletionChunk]: ...

    @overload
    def create(
        self,
        *,
        deployment_name: str,
        messages: List[Message],
        stream: Literal[False],
        api_version: Optional[str] = None,
        model: Optional[str] = None,
        functions: Union[List[FunctionParam], None] = None,
        function_call: Union[
            Union[Literal["none", "auto"], FunctionCallSpecParam], None
        ] = None,
        tools: Union[List[ToolParam], None] = None,
        tool_choice: Union[
            Union[Literal["none", "auto"], ToolCallSpecParam], None
        ] = None,
        addons: Union[Addon, None] = None,
        temperature: Union[float, None] = None,
        top_p: Union[float, None] = None,
        n: Union[int, None] = None,
        stop: Union[Union[str, List[str]], None] = None,
        max_tokens: Union[int, None] = None,
        max_prompt_tokens: Union[Union[Literal["infinity"], int], None] = None,
        presence_penalty: Union[float, None] = None,
        frequency_penalty: Union[float, None] = None,
        logit_bias: Union[Dict, None] = None,
        seed: Union[int, None] = None,
        user: Union[str, None] = None,
        custom_fields: Union[ChatCompletionRequestCustomFields, None] = None,
        logprobs: Union[bool, None] = None,
        top_logprobs: Union[int, None] = None,
        # Extra params
        extra_body: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Mapping[StrictStr, StrictStr]] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> ChatCompletionResponse: ...

    def create(
        self,
        *,
        deployment_name: str,
        messages: List[Message],
        api_version: Optional[str] = None,
        stream: bool = False,
        model: Optional[str] = None,
        functions: Union[List[FunctionParam], None] = None,
        function_call: Union[
            Union[Literal["none", "auto"], FunctionCallSpecParam], None
        ] = None,
        tools: Union[List[ToolParam], None] = None,
        tool_choice: Union[
            Union[Literal["none", "auto"], ToolCallSpecParam], None
        ] = None,
        addons: Union[Addon, None] = None,
        temperature: Union[float, None] = None,
        top_p: Union[float, None] = None,
        n: Union[int, None] = None,
        stop: Union[Union[str, List[str]], None] = None,
        max_tokens: Union[int, None] = None,
        max_prompt_tokens: Union[Union[Literal["infinity"], int], None] = None,
        presence_penalty: Union[float, None] = None,
        frequency_penalty: Union[float, None] = None,
        logit_bias: Union[Dict, None] = None,
        seed: Union[int, None] = None,
        user: Union[str, None] = None,
        custom_fields: Union[ChatCompletionRequestCustomFields, None] = None,
        logprobs: Union[bool, None] = None,
        top_logprobs: Union[int, None] = None,
        # Extra params
        extra_body: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Mapping[StrictStr, StrictStr]] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Union[ChatCompletionResponse, Iterable[ChatCompletionChunk]]:

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
                "addons": addons,
                "max_prompt_tokens": max_prompt_tokens,
                "custom_fields": custom_fields,
                "logprobs": logprobs,
                "top_logprobs": top_logprobs,
                "extra_body": extra_body,
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
                Union[
                    OpenaiChatCompletion,
                    OpenaiStream[OpenaiChatCompletionChunk],
                ],
                openai_response,
            )
        except openai.APIError as err:
            raise convert_openai_error(err)

        if isinstance(openai_response, OpenaiChatCompletion):
            return convert_openai_response(openai_response)
        else:
            return convert_openai_stream(openai_response)


class AsyncChatCompletions(AsyncResource):
    default_api_version: Optional[str] = None
    openai_client: openai.AsyncAzureOpenAI

    @overload
    async def create(
        self,
        *,
        deployment_name: str,
        messages: List[Message],
        stream: Literal[True],
        api_version: Optional[str] = None,
        model: Optional[str] = None,
        functions: Union[List[FunctionParam], None] = None,
        function_call: Union[
            Union[Literal["none", "auto"], FunctionCallSpecParam], None
        ] = None,
        tools: Union[List[ToolParam], None] = None,
        tool_choice: Union[
            Union[Literal["none", "auto"], ToolCallSpecParam], None
        ] = None,
        addons: Union[Addon, None] = None,
        temperature: Union[float, None] = None,
        top_p: Union[float, None] = None,
        n: Union[int, None] = None,
        stop: Union[Union[str, List[str]], None] = None,
        max_tokens: Union[int, None] = None,
        max_prompt_tokens: Union[Union[Literal["infinity"], int], None] = None,
        presence_penalty: Union[float, None] = None,
        frequency_penalty: Union[float, None] = None,
        logit_bias: Union[Dict, None] = None,
        seed: Union[int, None] = None,
        user: Union[str, None] = None,
        custom_fields: Union[ChatCompletionRequestCustomFields, None] = None,
        # Extra params
        extra_body: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Mapping[StrictStr, StrictStr]] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterable[ChatCompletionChunk]: ...

    @overload
    async def create(
        self,
        *,
        deployment_name: str,
        messages: List[Message],
        stream: Literal[False],
        api_version: Optional[str] = None,
        model: Optional[str] = None,
        functions: Union[List[FunctionParam], None] = None,
        function_call: Union[
            Union[Literal["none", "auto"], FunctionCallSpecParam], None
        ] = None,
        tools: Union[List[ToolParam], None] = None,
        tool_choice: Union[
            Union[Literal["none", "auto"], ToolCallSpecParam], None
        ] = None,
        addons: Union[Addon, None] = None,
        temperature: Union[float, None] = None,
        top_p: Union[float, None] = None,
        n: Union[int, None] = None,
        stop: Union[Union[str, List[str]], None] = None,
        max_tokens: Union[int, None] = None,
        max_prompt_tokens: Union[Union[Literal["infinity"], int], None] = None,
        presence_penalty: Union[float, None] = None,
        frequency_penalty: Union[float, None] = None,
        logit_bias: Union[Dict, None] = None,
        seed: Union[int, None] = None,
        user: Union[str, None] = None,
        custom_fields: Union[ChatCompletionRequestCustomFields, None] = None,
        logprobs: Union[bool, None] = None,
        top_logprobs: Union[int, None] = None,
        # Extra params
        extra_body: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Mapping[StrictStr, StrictStr]] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> ChatCompletionResponse: ...

    async def create(
        self,
        *,
        deployment_name: str,
        messages: List[Message],
        api_version: Optional[str] = None,
        stream: bool = False,
        model: Optional[str] = None,
        functions: Union[List[FunctionParam], None] = None,
        function_call: Union[
            Union[Literal["none", "auto"], FunctionCallSpecParam], None
        ] = None,
        tools: Union[List[ToolParam], None] = None,
        tool_choice: Union[
            Union[Literal["none", "auto"], ToolCallSpecParam], None
        ] = None,
        addons: Union[Addon, None] = None,
        temperature: Union[float, None] = None,
        top_p: Union[float, None] = None,
        n: Union[int, None] = None,
        stop: Union[Union[str, List[str]], None] = None,
        max_tokens: Union[int, None] = None,
        max_prompt_tokens: Union[Union[Literal["infinity"], int], None] = None,
        presence_penalty: Union[float, None] = None,
        frequency_penalty: Union[float, None] = None,
        logit_bias: Union[Dict, None] = None,
        seed: Union[int, None] = None,
        user: Union[str, None] = None,
        custom_fields: Union[ChatCompletionRequestCustomFields, None] = None,
        logprobs: Union[bool, None] = None,
        top_logprobs: Union[int, None] = None,
        # Extra params
        extra_body: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Mapping[StrictStr, StrictStr]] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Union[ChatCompletionResponse, AsyncIterable[ChatCompletionChunk]]:
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
                "addons": addons,
                "max_prompt_tokens": max_prompt_tokens,
                "custom_fields": custom_fields,
                "logprobs": logprobs,
                "top_logprobs": top_logprobs,
                "extra_body": extra_body,
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
                Union[
                    OpenaiChatCompletion,
                    OpenaiAsyncStream[OpenaiChatCompletionChunk],
                ],
                openai_response,
            )
        except openai.APIError as err:
            raise convert_openai_error(err)

        if isinstance(openai_response, OpenaiChatCompletion):
            return convert_openai_response(openai_response)
        else:
            return convert_openai_async_stream(openai_response)
