# AI DIAL Client (Python)

## Table of Contents

- [Authentication](#authentication)
  - [API Keys](#api-keys)
  - [Bearer Token](#bearer-token)
- [List Deployments](#list-deployments)
- [Make Chat Completions Requests](#make-completions-requests)
  - [Without Streaming](#without-streaming)
  - [With Streaming](#with-streaming)
- [Working with Files](#working-with-files)
  - [Working with URLs](#working-with-urls)
  - [Uploading Files](#uploading-files)
  - [Downloading Files](#downloading-files)
  - [Deleting Files](#deleting-files)
  - [Accessing Metadata](#accessing-metadata)
- [Applications](#applications)
  - [List Applications](#list-applications)
  - [Get Application by Id](#get-application-by-id)
- [Client Pool](#client-pool)
  - [Synchronous Client Pool](#synchronous-client-pool)
  - [Asynchronous Client Pool](#asynchronous-client-pool)

## Authentication

### API Keys

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

### Bearer Token

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

## List Deployments

If you want to get a list of available deployments, use `client.deployments.list()` or method:

```pycon
>>> client.deployments.list()
[
    Deployment(id='gpt-35-turbo', model='gpt-35-turbo', owner='organization-owner', object='deployment', status='succeeded', created_at=1724760524, updated_at=1724760524, scale_settings=ScaleSettings(scale_type='standard'), features={'rate': False, 'tokenize': False, 'truncate_prompt': False, 'configuration': False, 'system_prompt': True, 'tools': False, 'seed': False, 'url_attachments': False, 'folder_attachments': False, 'allow_resume': True}),
    Deployment(id='stable-diffusion-xl', model='stable-diffusion-xl', owner='organization-owner', object='deployment', status='succeeded', created_at=1724760524, updated_at=1724760524, scale_settings=ScaleSettings(scale_type='standard'), features={'rate': False, 'tokenize': False, 'truncate_prompt': False, 'configuration': False, 'system_prompt': True, 'tools': False, 'seed': False, 'url_attachments': False, 'folder_attachments': False, 'allow_resume': True}),
    Deployment(id='gemini-pro-vision', model='gemini-pro-vision', owner='organization-owner', object='deployment', status='succeeded', created_at=1724760524, updated_at=1724760524, scale_settings=ScaleSettings(scale_type='standard'), features={'rate': False, 'tokenize': False, 'truncate_prompt': False, 'configuration': False, 'system_prompt': True, 'tools': False, 'seed': False, 'url_attachments': False, 'folder_attachments': False, 'allow_resume': True}),
]
```

## Make Completions Requests

### Without Streaming

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

### With Streaming

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

## Working with Files

### Working with URLs

Files are AI DIAL resources that operate with URL-like objects. Use `pathlib.PurePosixPath` or `str` to create to create new URL-like objects or to get a `string` representation of them.

* Use `client.my_files_home()` to upload a file into your bucket in the AI DIAL storage.
* Use `await async_client.my_files_home()` to get the URL of your bucket and then use it to upload files.

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

### Uploading Files

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

### Downloading Files

Use `download()` to download files from your storage bucket:

```python
result = client.files.download(
    url=client.my_files_home() / "relative_folder/my-file.txt"
)

result = await async_client.files.download(
    url=await async_client.my_files_home() / "relative_folder/my-file.txt"
)
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

or write it to the file:

```python
# Sync
result.write_to("./some-local-file.txt")
# Async
await result.awrite_to("./some-local-file.txt")
```

### Deleting Files

Use `delete()` to remove files from your storage bucket:


```python
await sync_client.files.delete(
    url=sync_client.my_files_home() / "relative_folder/my-file.txt"
)

await async_client.files.delete(
    url=await async_client.my_files_home() / "relative_folder/my-file.txt"
)
```

### Accessing Metadata

Use `metadata()` to access metadata of a file:

```python
metadata = await async_client.files.metadata(
    url=await async_client.my_files_home() / "relative_folder/my-file.txt"
)
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
    items=None,
    updatedAt=1724836248936,
    etag="9749fad13d6e7092a6337c4af9d83764",
    createdAt=1724836229736,
)
```

## Applications

### List Applications

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
        ),
        input_attachment_types=["image/png", "text/txt", "image/jpeg"],
        defaults={},
        max_input_attachments=0,
        description_keywords=[],
    ),
    ...,
]
```

### Get Application by Id

You can get your DIAL applications by their Ids:

```python
# Sync
application = client.application.get("app_id")
# Async
application = await async_client.application.get("app_id")
```

As a result, you will receive a list of `Application` objects. Refer to the [previous example](#list-applications).

## Client Pool

When you need to create multiple DIAL clients and wish to enhance performance by reusing the HTTP connection for the same DIAL instance, consider using synchronous and asynchronous **client pools**.

### Synchronous Client Pool

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

### Asynchronous Client Pool

```python
from dial_client import (
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
