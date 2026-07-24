<h1 align="center">
  AI DIAL Client (Python)
</h1>
<p align="center">
  <p align="center">
  <a href="https://dialx.ai/">
    <img src="https://dialx.ai/logo/dialx_logo.svg" alt="About DIALX">
  </a>
</p>
<h4 align="center">
  <a href="https://discord.gg/ukzj9U9tEe">
    <img src="https://img.shields.io/static/v1?label=DIALX%20Community%20on&message=Discord&color=blue&logo=Discord&style=flat-square" alt="Discord">
  </a>
</h4>

- [Usage](#usage)
  - [Authentication](#authentication)
    - [API Keys](#api-keys)
    - [Bearer Token](#bearer-token)
  - [Lifecycle Management](#lifecycle-management)
  - [Deployments](#deployments)
    - [List Deployments](#list-deployments)
    - [Get Deployment by Id](#get-deployment-by-id)
    - [Get Deployment Configuration](#get-deployment-configuration)
  - [Make Chat Completions Requests](#make-completions-requests)
    - [Without Streaming](#without-streaming)
    - [With Streaming](#with-streaming)
  - [Working with Files](#working-with-files)
    - [Working with URLs](#working-with-urls)
    - [Uploading Files](#uploading-files)
    - [Downloading Files](#downloading-files)
    - [Deleting Files](#deleting-files)
    - [Accessing Metadata](#accessing-metadata)
  - [Prompts](#prompts)
    - [Get Prompt](#get-prompt)
    - [Get Prompt Metadata](#get-prompt-metadata)
  - [Applications](#applications)
    - [List Applications](#list-applications)
    - [Get Application by Id](#get-application-by-id)
  - [Models](#models)
    - [Get Model by Name](#get-model-by-name)
  - [User](#user)
    - [Get Authenticated User Info](#get-authenticated-user-info)
  - [Toolsets](#toolsets)
    - [Get Toolset by Id](#get-toolset-by-id)
  - [Resource Permissions](#resource-permissions)
    - [Grant Permissions](#grant-permissions)
  - [Client Channel](#client-channel)
    - [Sign In to Toolsets](#sign-in-to-toolsets)
  - [Client Pool](#client-pool)
    - [Synchronous Client Pool](#synchronous-client-pool)
    - [Asynchronous Client Pool](#asynchronous-client-pool)
- [Development](#development)
  - [Pre-requisites](#pre-requisites)
  - [Setup](#setup)
  - [Main commands](#main-commands)
  - [Git hooks](#git-hooks)

## Usage

This section outlines how to use the AI DIAL Python client to interact with the DIAL Core API.
It covers authentication methods, making chat completion requests, working with files, managing applications,
and utilizing client pools for efficient connection management.

### Authentication

#### API Keys

For authentication with an API key, pass it during the client initialization:

```python
from aidial_client import Dial, AsyncDial

dial_client = Dial(api_key="your_api_key", base_url="https://your-dial-instance.com")

async_dial_client = AsyncDial(
    api_key="your_api_key", base_url="https://your-dial-instance.com"
)
```

You can also pass `api_key` as a function without parameters, that returns a `string`:

```python
def my_key_function():
    # Any custom logic to get an API key
    return "your-api-key"


dial_client = Dial(api_key=my_key_function, base_url="https://your-dial-instance.com")

async_dial_client = AsyncDial(
    api_key=my_key_function, base_url="https://your-dial-instance.com"
)
```

For `async` clients, you can use coroutine as well:

```python
async def my_key_function():
    # Any custom logic to get an API key
    return "your-api-key"


async_dial_client = AsyncDial(
    api_key=my_key_function, base_url="https://your-dial-instance.com"
)
```

#### Bearer Token

You can use a Bearer Token for a token-based authentication of API calls. Client instances will use it to construct the `Authorization` header when making requests:

```python
from aidial_client import Dial, AsyncDial

# Create an instance of the synchronous client
sync_client = Dial(
    bearer_token="your_bearer_token_here", base_url="https://your-dial-instance.com"
)

# Create an instance of the asynchronous client
async_client = AsyncDial(
    bearer_token="your_bearer_token_here", base_url="https://your-dial-instance.com"
)
```

### Lifecycle Management

For deterministic shutdown of underlying HTTP clients, both client types and
client pools expose lifecycle APIs.

```python
from aidial_client import AsyncDial, AsyncDialClientPool, Dial, DialClientPool

# Sync client
with Dial(api_key="your_api_key", base_url="https://your-dial-instance.com") as client:
    ...

client = Dial(api_key="your_api_key", base_url="https://your-dial-instance.com")
client.close()

# Async client
async with AsyncDial(
    api_key="your_api_key", base_url="https://your-dial-instance.com"
) as async_client:
    ...

async_client = AsyncDial(
    api_key="your_api_key", base_url="https://your-dial-instance.com"
)
await async_client.aclose()

# Sync pool
with DialClientPool() as pool:
    pooled_client = pool.create_client(
        base_url="https://your-dial-instance.com", api_key="your-api-key"
    )

# Async pool
async with AsyncDialClientPool() as async_pool:
    pooled_async_client = async_pool.create_client(
        base_url="https://your-dial-instance.com", api_key="your-api-key"
    )
```

You can also pass `bearer_token` as a function without parameters, that returns a `string`:

```python
def my_token_function():
    # Any custom logic to get an API key
    return "your-bearer-token"


dial_client = Dial(
    bearer_token=my_token_function, base_url="https://your-dial-instance.com"
)

async_dial_client = AsyncDial(
    bearer_token=my_token_function, base_url="https://your-dial-instance.com"
)
```

For `async` clients, you can use coroutine as well:

```python
async def my_token_function():
    # Any custom logic to get a bearer token
    return "your-bearer-token"


dial_client = Dial(
    bearer_token=my_token_function, base_url="https://your-dial-instance.com"
)
```

### Deployments

#### List Deployments

To get a list of available deployments:

```python
# Sync
deployments = client.deployments.list()
# Async
deployments = await async_client.deployments.list()
```

```pycon
>>> client.deployments.list()
[
    Deployment(id='gpt-35-turbo', model='gpt-35-turbo', owner='organization-owner', object='deployment', status='succeeded', created_at=1724760524, updated_at=1724760524, scale_settings=ScaleSettings(scale_type='standard'), features=Features(rate=False, tokenize=False, truncate_prompt=False, configuration=False, system_prompt=True, tools=False, seed=False, url_attachments=False, folder_attachments=False, allow_resume=True)),
    Deployment(id='stable-diffusion-xl', model='stable-diffusion-xl', owner='organization-owner', object='deployment', status='succeeded', created_at=1724760524, updated_at=1724760524, scale_settings=ScaleSettings(scale_type='standard'), features=Features(rate=False, tokenize=False, truncate_prompt=False, configuration=False, system_prompt=True, tools=False, seed=False, url_attachments=False, folder_attachments=False, allow_resume=True)),
    ...,
]
```

#### Get Deployment by Id

To fetch a single deployment by its identifier:

```python
# Sync
deployment = client.deployments.get("gpt-35-turbo")
# Async
deployment = await async_client.deployments.get("gpt-35-turbo")
```

As a result, you will receive a `Deployment` object:

```python
Deployment(
    id="gpt-35-turbo",
    model="gpt-35-turbo",
    object="deployment",
    owner="organization-owner",
    status="succeeded",
    created_at=1724760524,
    updated_at=1724760524,
    scale_settings=ScaleSettings(scale_type="standard"),
    features=Features(
        rate=False,
        tokenize=False,
        truncate_prompt=False,
        configuration=True,
        system_prompt=True,
        tools=True,
        seed=False,
        url_attachments=False,
        folder_attachments=False,
        allow_resume=True,
        chat_completion=True,
        responses_api=False,
        reasoning_efforts=["low", "medium", "high"],
    ),
    defaults={},
)
```

#### Get Deployment Configuration

Some deployments expose a JSON Schema document describing their runtime configuration. Use `get_configuration()` to retrieve it:

```python
# Sync
config = client.deployments.get_configuration_schema("gpt-35-turbo")
# Async
config = await async_client.deployments.get_configuration_schema("gpt-35-turbo")
```

The response is a plain `dict` whose shape is entirely deployment-specific:

```python
{
    "type": "object",
    "properties": {
        "model_to_use": {
            "type": "string",
            "enum": ["gpt-4", "gpt-4o"],
            "default": "gpt-4",
        }
    },
    "additionalProperties": False,
}
```

### Make Completions Requests

#### Without Streaming

Synchronous:

```python
...
client = Dial(api_key="your-api-key", base_url="https://your-dial-instance.com")

completion = client.chat.completions.create(
    deployment_name="gpt-35-turbo",
    stream=False,
    messages=[
        {
            "role": "system",
            "content": "2+3=",
        }
    ],
    api_version="2024-02-15-preview",
)
```

Asynchronous:

```python
...
async_client = AsyncDial(
    api_key="your-api-key", base_url="https://your-dial-instance.com"
)
completion = await async_client.chat.completions.create(
    deployment_name="gpt-35-turbo",
    stream=False,
    messages=[
        {
            "role": "system",
            "content": "2+3=",
        }
    ],
    api_version="2024-02-15-preview",
)
```

Example of a response:

```pycon
>>> completion
ChatCompletionResponse(
    id='chatcmpl-A18H6rWmocm52WMweXvp8BNnwbfsp',
    object='chat.completion',
    choices=[
        Choice(
            index=0,
            message=ChatCompletionMessage(
                role='assistant',
                content='5',
                custom_content=None,
                function_call=None,
                tool_calls=None
            ),
            finish_reason='stop',
            logprobs=None
        )
    ],
    created=1724833500,
    model='gpt-35-turbo-16k',
    usage=CompletionUsage(
        prompt_tokens=11,
        completion_tokens=1,
        total_tokens=12
    ),
    system_fingerprint=None
)
```

#### With Streaming

Synchronous:

```python
...
client = Dial(api_key="your-api-key", base_url="https://your-dial-instance.com")

completion = client.chat.completions.create(
    deployment_name="gpt-35-turbo",
    # Specify a stream parameter
    stream=True,
    messages=[
        {
            "role": "system",
            "content": "2+3=",
        }
    ],
    api_version="2024-02-15-preview",
)
for chunk in completion:
    ...
```

Asynchronous:

```python
...
async_client = AsyncDial(
    api_key="your-api-key", base_url="https://your-dial-instance.com"
)
completion = await async_client.chat.completions.create(
    deployment_name="gpt-35-turbo",
    # Specify a stream parameter
    stream=True,
    messages=[
        {
            "role": "system",
            "content": "2+3=",
        }
    ],
    api_version="2024-02-15-preview",
)
async for chunk in completion:
    ...
```

Example of chunk objects:

```pycon
>>> chunk
ChatCompletionChunk(
    id='chatcmpl-A18NiK8Zh39RdcNX91T0eHfERfyU3',
    object='chat.completion.chunk',
    choices=[
        ChoiceDelta(
            index=0,
            delta=ChunkEmptyDelta(
                content='5',
                object=None,
                tool_calls=None,
                role=None
                ),
            finish_reason=None,
            logprobs=None
        )
    ],
    created=1724833910,
    model='gpt-35-turbo-16k',
    usage=None,
    system_fingerprint=None
)
>>> chunk
ChatCompletionChunk(
    id='chatcmpl-A18NiK8Zh39RdcNX91T0eHfERfyU3',
    object='chat.completion.chunk',
    choices=[
        ChoiceDelta(
            index=0,
            delta=ChunkEmptyDelta(
                content=None,
                object=None,
                tool_calls=None,
                role=None
            ),
            # Last chunk has non-empty finish_reason
            finish_reason='stop',
            logprobs=None
        )
    ],
    created=1724833910,
    model='gpt-35-turbo-16k',
    usage=CompletionUsage(
        prompt_tokens=11,
        completion_tokens=1,
        total_tokens=12
    ),
    system_fingerprint=None
)
```

### Working with Files

#### Working with URLs

Files are AI DIAL resources that operate with URL-like objects. Use `pathlib.PurePosixPath` or `str` to create to create new URL-like objects or to get a `string` representation of them.

- Use `client.my_files_home()` to upload a file into your bucket in the AI DIAL storage.
- Use `await async_client.my_files_home()` to get the URL of your bucket and then use it to upload files.

The following example demonstrates how you can use the path-like object returned by `my_files_home()` function:

```python
sync_client.files.upload(
    url=sync_client.my_files_home() / "some-relative-path/my-file.txt", ...
)

async_client.files.upload(
    url=await async_client.my_files_home() / "some-relative-path/my-file.txt", ...
)
```

If you already have a relative URL like `files/...`, you can use it as well:

```python
relative_url = "files/test-bucket/some-relative-path/my-file.txt"
sync_client.files.upload(url=relative_url, ...)
```

You can also use an absolute URL:

```python
absolute_url = "http://dial.core/v1/files/test-bucket/some-relative-path/my-file.txt"
sync_client.files.upload(url=absolute_url, ...)
```

**Note**, that an invalid URL provided to the function, will raise an `InvalidDialURLException` exception.

#### Uploading Files

Use `upload()` to add files into your storage bucket:

```python
with open("./some-local-file.txt", "rb") as file:
    # Sync client
    sync_client.files.upload(
        url=sync_client.my_files_home() / "some-relative-path/my-file.txt", file=file
    )
    # Async client
    await async_client.files.upload(
        url=await async_client.my_files_home() / "some-relative-path/my-file.txt",
        file=file,
    )
```

Files can contain raw bytes or file-like objects. To specify filename and content type of the uploaded file, use **tuple** instead of file object:

```python
sync_client.files.upload(
    url=sync_client.my_files_home() / "some-relative-path/my-file.txt",
    file=("filename.txt", "text/plain", file),
)
```

`upload()` returns a `FileItem` describing the stored file:

```python
FileItem(
    name="my-file.txt",
    parent_path="some-relative-path",
    bucket="my-bucket",
    url="files/my-bucket/some-relative-path/my-file.txt",
    node_type="ITEM",
    resource_type="FILE",
    content_length=12,
    content_type="text/plain",
    etag="9749fad13d6e7092a6337c4af9d83764",
    created_at=1724836229736,
    updated_at=1724836248936,
    author="user@example.com",
)
```

#### Downloading Files

Use `download()` to download files from your storage bucket:

```python
result = client.files.download(
    url=client.my_files_home() / "relative_folder/my-file.txt"
)

result = await async_client.files.download(
    url=await async_client.my_files_home() / "relative_folder/my-file.txt"
)
```

For large async downloads, use `stream_download()` to process bytes as they arrive without buffering the full response in memory:

```python
async with async_client.files.stream_download(
    url=await async_client.my_files_home() / "relative_folder/my-file.txt"
) as result:
    async for bytes_chunk in result:
        ...
```

As a result, you will receive an object of type `FileDownloadResponse`, that you can iterate by byte chunks:

```python
for bytes_chunk in result:
    ...
```

or get full content as bytes:

```python
# Sync
all_content = result.get_content()
# Async
all_content = await result.aget_content()
```

or access response metadata:

```python
headers = result.headers
content_type = result.content_type
```

or write it to the file:

```python
# Sync
result.write_to("./some-local-file.txt")
# Async
await result.awrite_to("./some-local-file.txt")
```

#### Deleting Files

Use `delete()` to remove files from your storage bucket:

```python
await sync_client.files.delete(
    url=sync_client.my_files_home() / "relative_folder/my-file.txt"
)

await async_client.files.delete(
    url=await async_client.my_files_home() / "relative_folder/my-file.txt"
)
```

#### Moving and Copying Files

Use `move_to()` to relocate a file within DIAL storage and `copy_to()` to duplicate it. Both accept the same `source` / `destination` URLs (relative, absolute, or `PurePosixPath`) and an optional `overwrite` flag (default `False`):

```python
# Sync client
sync_client.files.move_to(
    source=sync_client.my_files_home() / "draft/my-file.txt",
    destination=sync_client.my_files_home() / "final/my-file.txt",
)
sync_client.files.copy_to(
    source=sync_client.my_files_home() / "final/my-file.txt",
    destination=sync_client.my_files_home() / "backup/my-file.txt",
    overwrite=True,
)

# Async client
await async_client.files.move_to(
    source=await async_client.my_files_home() / "draft/my-file.txt",
    destination=await async_client.my_files_home() / "final/my-file.txt",
)
await async_client.files.copy_to(
    source=await async_client.my_files_home() / "final/my-file.txt",
    destination=await async_client.my_files_home() / "backup/my-file.txt",
    overwrite=True,
)
```

Both methods return `None` on success. `source` and `destination` must point to files in the same DIAL storage (passing a `prompts/...` URL raises `InvalidDialURLError`).

#### Accessing Metadata

Use `get_metadata()` to access metadata of a file or folder:

```python
# Sync client
metadata = sync_client.files.get_metadata(
    url=sync_client.my_files_home() / "relative_folder/my-file.txt"
)

# Async client
metadata = await async_client.files.get_metadata(
    url=await async_client.my_files_home() / "relative_folder/my-file.txt"
)
```

Folder metadata can be paginated with `limit` and `token`:

```python
metadata = await async_client.files.get_metadata(
    url=await async_client.my_files_home() / "relative_folder/",
    limit=100,
    token=next_token,
)
next_token = metadata.next_token
items = metadata.items
```

Example of metadata:

```python
FileMetadata(
    name="my-file.txt",
    parent_path="relative_folder",
    bucket="my-bucket",
    url="files/my-bucket/test-folder-artifacts/test-file",
    node_type="ITEM",
    resource_type="FILE",
    content_length=12,
    content_type="application/octet-stream",
    etag="9749fad13d6e7092a6337c4af9d83764",
    created_at=1724836229736,
    updated_at=1724836248936,
    author="user@example.com",
    next_token=None,
    items=None,
)
```

### Prompts

#### Save Prompt

Use `save()` to create or update a prompt by its storage path:

```python
from aidial_client.types.prompt import Prompt

prompt_url = "prompts/my-bucket/my-folder/my-prompt"
prompt_payload = Prompt(
    id=prompt_url,
    name="my-prompt",
    folder_id="my-folder",
    content="You are a helpful assistant.",
)

# Sync
saved_prompt = client.prompts.save(prompt_url, prompt=prompt_payload)
# Async
saved_prompt = await async_client.prompts.save(prompt_url, prompt=prompt_payload)
```

As a result, you will receive a `PromptItem` object:

```python
PromptItem(
    name="my-prompt",
    parent_path="my-folder",
    bucket="my-bucket",
    url="prompts/my-bucket/my-folder/my-prompt",
    node_type="ITEM",
    resource_type="PROMPT",
    etag="9749fad13d6e7092a6337c4af9d83764",
    created_at=1724836229736,
    updated_at=1724836248936,
    author="user@example.com",
)
```

#### Get Prompt

Use `get()` to fetch a single prompt by its storage path:

```python
# Sync
prompt = client.prompts.get("prompts/my-bucket/my-folder/my-prompt")
# Async
prompt = await async_client.prompts.get("prompts/my-bucket/my-folder/my-prompt")
```

As a result, you will receive a `Prompt` object:

```python
Prompt(
    id="prompts/my-bucket/my-folder/my-prompt",
    name="my-prompt",
    folder_id="my-folder",
    content="You are a helpful assistant.",
)
```

#### Get Prompt Metadata

Use `get_metadata()` to access metadata of a prompt:

```python
# Sync
metadata = client.prompts.get_metadata("prompts/my-bucket/my-folder/my-prompt")
# Async
metadata = await async_client.prompts.get_metadata(
    "prompts/my-bucket/my-folder/my-prompt"
)
```

As a result, you will receive a `PromptMetadata` object:

```python
PromptMetadata(
    name="my-prompt",
    parent_path="my-folder",
    bucket="my-bucket",
    url="prompts/my-bucket/my-folder/my-prompt",
    node_type="ITEM",
    resource_type="PROMPT",
    items=[],
)
```

#### Delete Prompt

Use `delete()` to remove a prompt by its storage path:

```python
# Sync
client.prompts.delete("prompts/my-bucket/my-folder/my-prompt")
# Async
await async_client.prompts.delete("prompts/my-bucket/my-folder/my-prompt")
```

### Applications

#### List Applications

To get a list of your DIAL applications:

```python
# Sync
applications = client.application.list()
# Async
applications = await async_client.application.list()
```

As a result, you will receive a list of `Application` objects:

```python
[
    Application(
        object="application",
        id="app_id",
        description="",
        application="app_id",
        display_name="app with attachments",
        display_version="0.0.0",
        icon_url="...",
        reference="...",
        owner="organization-owner",
        status="succeeded",
        created_at=1672534800,
        updated_at=1672534800,
        features=Features(
            rate=False,
            tokenize=False,
            truncate_prompt=False,
            configuration=False,
            system_prompt=True,
            tools=False,
            seed=False,
            url_attachments=False,
            folder_attachments=False,
            allow_resume=True,
            chat_completion=True,
            responses_api=False,
            reasoning_efforts=[],
        ),
        input_attachment_types=["image/png", "text/txt", "image/jpeg"],
        defaults={},
        max_input_attachments=0,
        description_keywords=[],
    ),
    ...,
]
```

#### Get Application by Id

You can get your DIAL applications by their Ids:

```python
# Sync
application = client.application.get("app_id")
# Async
application = await async_client.application.get("app_id")
```

As a result, you will receive a list of `Application` objects. Refer to the [previous example](#list-applications).

### Models

#### Get Model by Name

To retrieve metadata, capabilities, and pricing for a specific model:

```python
# Sync
model_info = client.model.get("gpt-4")
# Async
model_info = await async_client.model.get("gpt-4")
```

As a result, you will receive a `ModelInfo` object:

```python
ModelInfo(
    id="gpt-4",
    model="gpt-4",
    object="model",
    owner="organization-owner",
    status="succeeded",
    created_at=1724760524,
    updated_at=1724760524,
    lifecycle_status="generally-available",
    display_name="GPT-4",
    description="OpenAI GPT-4 model.",
    capabilities=ModelCapabilities(
        scale_types=["standard"],
        completion=False,
        chat_completion=True,
        embeddings=False,
        fine_tune=False,
        inference=False,
    ),
    limits=ModelLimits(
        max_prompt_tokens=8192,
        max_completion_tokens=4096,
        max_total_tokens=None,
    ),
    pricing=ModelPricing(
        unit="token",
        prompt="0.00003",
        completion="0.00006",
    ),
)
```

For embedding models, `ModelInfo` also includes `embedding_dimensions` — the size of the output vector (e.g. `embedding_dimensions=1536`). It is omitted for non-embedding models.

### User

#### Get Authenticated User Info

To retrieve information about the currently authenticated user:

```python
# Sync
user_info = client.user.info()

# Async
user_info = await async_client.user.info()
```

As a result, you will receive a `UserInfo` object. When authenticated with an
API key:

```python
UserInfo(
    roles=["default"],
    project="PROJECT-NAME",
    userClaims=None,
)
```

When authenticated with an access token:

```python
UserInfo(
    roles=["BA"],
    project=None,
    userClaims={
        "email": ["user_email"],
        "sub": ["user_sub"],
    },
)
```

`userClaims` is returned as an opaque `dict` because its contents depend on the
identity provider. `UserInfo` also preserves any additional fields the DIAL
deployment may return, so forward compatibility is retained.

### Toolsets

#### Get Toolset by Id

To retrieve information about a specific MCP toolset:

```python
# Sync
toolset_info = client.toolset.get("my-toolset")
# Async
toolset_info = await async_client.toolset.get("my-toolset")
```

As a result, you will receive a `ToolsetInfo` object:

```python
ToolsetInfo(
    id="my-toolset",
    toolset="my-toolset",
    display_name="My Toolset",
    description="A collection of tools for data processing.",
    transport="HTTP",
    allowed_tools=["tool-a", "tool-b"],
    owner="organization-owner",
    status="succeeded",
    created_at=1724760524,
    updated_at=1724760524,
)
```

### Resource Permissions

#### Grant Permissions

Use `resource_permissions.grant()` to grant access to one or more files in DIAL storage to a specific deployment (receiver). This is typically used when a deployment needs to read files on behalf of a user.

```python
# Sync
client.resource_permissions.grant(
    resources=["files/my-bucket/report.pdf"],
    receiver="my-deployment",
    permissions=["READ"],
)
# Async
await async_client.resource_permissions.grant(
    resources=["files/my-bucket/report.pdf"],
    receiver="my-deployment",
    permissions=["READ"],
)
```

- `resources` — list of DIAL file URL strings to share.
- `receiver` — the deployment ID that should receive access.
- `permissions` — list of permission strings; defaults to `["READ"]`.

The method returns `None` on success and raises `DialException` on HTTP error.

### Client Channel

DIAL Core's [client channel API](https://dialx.ai/universal_chat_api.yaml) lets a deployment ask an interactive client (e.g. the chat UI) to take some action and report the result back. The channel id is propagated to the deployment via the `X-DIAL-CLIENT-CHANNEL-ID` forwarded header on the inbound request.

#### Sign In to Toolsets

Use `client_channel.signin_toolsets()` to request interactive sign-in for one or more toolsets on the active client channel. The method returns a `dict[str, SigninResult]` mapping each input toolset id to its outcome — responses are correlated by the client, so the caller never has to deal with the underlying JSON-RPC ids.

```python
from aidial_client import SigninResult

# Sync
results = client.client_channel.signin_toolsets(
    channel_id="<channel-id-from-X-DIAL-CLIENT-CHANNEL-ID>",
    toolset_ids=[
        "toolsets/public/toolset-a",
        "toolsets/public/toolset-b",
    ],
    timeout=120.0,
)

# Async
results = await async_client.client_channel.signin_toolsets(
    channel_id="<channel-id>",
    toolset_ids=["toolsets/public/my-toolset"],
)
```

Each value is a `SigninResult` enum:

```python
{
    "toolsets/public/toolset-a": SigninResult.SUCCESS,
    "toolsets/public/toolset-b": SigninResult.DENIED,
}
```

- `SigninResult.SUCCESS` — the user signed in.
- `SigninResult.DENIED` — the user declined.
- `SigninResult.ERROR` — the server returned a JSON-RPC error, or the response was missing/unrecognized.

Arguments:

- `channel_id` — required; the channel id received via the `X-DIAL-CLIENT-CHANNEL-ID` header on the inbound request.
- `toolset_ids` — sequence of toolset ids to request sign-in for; an empty sequence returns `{}` without contacting the server.
- `timeout` — optional `float` seconds or `httpx.Timeout`; defaults to the client-wide timeout. Useful for interactive flows where the user may take a while to respond.

Raises `DialException` on HTTP errors (e.g. unauthorized, missing channel), transport failures (timeouts, network errors), or if the SSE stream closes without a response event.

### Client Pool

When you need to create multiple DIAL clients and wish to enhance performance by reusing the HTTP connection for the same DIAL instance, consider using synchronous and asynchronous **client pools**.

#### Synchronous Client Pool

```python
from aidial_client import DialClientPool

client_pool = DialClientPool()

first_client = client_pool.create_client(
    base_url="https://your-dial-instance.com", api_key="your-api-key"
)

second_client = client_pool.create_client(
    base_url="https://your-dial-instance.com", bearer_token="your-bearer-token"
)
```

#### Asynchronous Client Pool

```python
from aidial_client import (
    AsyncDialClientPool,
)

client_pool = AsyncDialClientPool()

first_client = client_pool.create_client(
    base_url="https://your-dial-instance.com", api_key="your-api-key"
)

second_client = client_pool.create_client(
    base_url="https://your-dial-instance.com", bearer_token="your-bearer-token"
)
```

## Development

To set up the development environment and run the project, follow the instructions below.

### Pre-requisites

The following tools are required to work with the project:

1. `Make`
2. `Python 3.10`
3. `Poetry 2.*`. See the [Poetry installation guide](https://python-poetry.org/docs/#installation)

### Setup

1. Create `.env` file in the root of the project. Copy `.env.template` file data to the `.env` and customize the values
   if needed. You can customize python and poetry locations.
2. Create and activate virtual environment

    ```bash
    make init_env
    source .venv/bin/activate
    ```

3. Install dependencies

    ```bash
    make install
    ```

### Git hooks

You may optionally install Git hooks that will automatically run the linting step on Git push. You only need to do it once for the given repository.

```sh
make install_git_hooks
```

> [!IMPORTANT]
> This command doesn't work if you have already installed Git hooks locally or globally.

### Main commands

| Command                   | Description                                   |
|---------------------------|-----------------------------------------------|
| `make install`            | Install virtual environment and dependencies  |
| `make build`              | Build the package                             |
| `make clean`              | Clean virtual environment and build artifacts |
| `make install_git_hooks`  | Install the git hooks                         |
| `make lint`               | Run linters                                   |
| `make format`             | Run code formatters                           |
| `make test`               | Run tests (e.g., `make test PYTHON=3.12`)     |
| `make integration_test`   | Run integration tests                         |
| `make coverage`           | Generate test coverage report                 |
| `make help`               | Show available commands                       |
