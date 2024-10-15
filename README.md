# AI DIAL Client (Python)

## Table of Contents

- [Authentication](#authentication)
    - [Using API Key](#using-api-key)
    - [Using Bearer Token](#using-bearer-token)
- [Client Pool](#client-pool)
    - [Synchronous Client Pool](#synchronous-client-pool)
    - [Asynchronous Client Pool](#asynchronous-client-pool)
- [List deployments](#list-deployments)
- [Make chat completions request](#make-completions-request)
    - [Without streaming](#without-streaming)
    - [With streaming](#with-streaming)
- [Working with files](#working-with-files)
    - [Working with URLs](#working-with-urls)
    - [Uploading files](#uploading-files)
    - [Downloading files](#downloading-files)
    - [Deleting files](#deleting-files)
    - [Accessing metadata](#accessing-metadata)
- [Applications](#applications)
    - [List applications](#list-applications)
    - [Get application by id](#get-application-by-id)

## Authentication

### Using API Key

If you have API key, you can pass it during client initialization:

```python
from aidial_client import (
    Dial,
    AsyncDial,
)

dial_client = Dial(api_key='your_api_key', base_url='https://your-dial-instance.com')

async_dial_client = AsyncDial(api_key='your_api_key', base_url='https://your-dial-instance.com')
```

You also can pass api_key as function without parameters, that returns string
```python
def my_key_function():
    # Some your logic to get api key
    return  'your-api-key'

dial_client = Dial(api_key=my_key_function, base_url='https://your-dial-instance.com')

async_dial_client = AsyncDial(api_key=my_key_function, base_url='https://your-dial-instance.com')
```

For async client you can use coroutine as well:
```python
async def my_key_function():
    # Some your logic to get api key
    return 'your-api-key'

async_dial_client = AsyncDial(api_key=my_key_function, base_url='https://your-dial-instance.com')
```

### Using Bearer Token

```python
from aidial_client import (
    Dial,
    AsyncDial
)


# Create an instance of the synchronous client
sync_client = Dial(bearer_token='your_bearer_token_here', base_url='https://your-dial-instance.com')

# Create an instance of the asynchronous client
async_client = AsyncDial(bearer_token='your_bearer_token_here', base_url='https://your-dial-instance.com')
```

You also can pass bearer_token as function without parameters, that returns string
```python
def my_token_function():
    # Some your logic to get bearer token
    return  'your-bearer-token'

dial_client = Dial(bearer_token=my_token_function, base_url='https://your-dial-instance.com')

async_dial_client = AsyncDial(bearer_token=my_token_function, base_url='https://your-dial-instance.com')
```

For async client you can use coroutine as well:
```python
async def my_token_function():
    # Some your logic to get bearer token
    return 'your-bearer-token'

dial_client = Dial(bearer_token=my_token_function, base_url='https://your-dial-instance.com')
```

## Client Pool

When you need to create multiple DIAL clients, but you want to reuse the HTTP connection to the same DIAL instance for better performance, you can use client pool:

### Synchronous Client Pool

```python
from aidial_client import (
    DialClientPool
)
client_pool = DialClientPool()

first_client = client_pool.create_client(base_url="https://your-dial-instance.com", api_key="your-api-key")

second_client = client_pool.create_client(base_url="https://your-dial-instance.com", bearer_token="your-bearer-token")
```

### Asynchronous Client Pool

```python
from dial_client import (
    AsyncDialClientPool,
)
client_pool = AsyncDialClientPool()

first_client = client_pool.create_client(base_url="https://your-dial-instance.com", api_key="your-api-key")

second_client = client_pool.create_client(base_url="https://your-dial-instance.com", bearer_token="your-bearer-token")
```

## List deployments

If you want to get list of available deployments, use `client.deployments.list()` or method:

```python
client = Dial(api_key=api_key, base_url=base_url)

>>> client.deployments.list()
[
    Deployment(id='gpt-35-turbo', model='gpt-35-turbo', owner='organization-owner', object='deployment', status='succeeded', created_at=1724760524, updated_at=1724760524, scale_settings=ScaleSettings(scale_type='standard'), features={'rate': False, 'tokenize': False, 'truncate_prompt': False, 'configuration': False, 'system_prompt': True, 'tools': False, 'seed': False, 'url_attachments': False, 'folder_attachments': False, 'allow_resume': True}),
    Deployment(id='stable-diffusion-xl', model='stable-diffusion-xl', owner='organization-owner', object='deployment', status='succeeded', created_at=1724760524, updated_at=1724760524, scale_settings=ScaleSettings(scale_type='standard'), features={'rate': False, 'tokenize': False, 'truncate_prompt': False, 'configuration': False, 'system_prompt': True, 'tools': False, 'seed': False, 'url_attachments': False, 'folder_attachments': False, 'allow_resume': True}),
    Deployment(id='gemini-pro-vision', model='gemini-pro-vision', owner='organization-owner', object='deployment', status='succeeded', created_at=1724760524, updated_at=1724760524, scale_settings=ScaleSettings(scale_type='standard'), features={'rate': False, 'tokenize': False, 'truncate_prompt': False, 'configuration': False, 'system_prompt': True, 'tools': False, 'seed': False, 'url_attachments': False, 'folder_attachments': False, 'allow_resume': True}),
]
```

## Make completions request

### Without streaming

Sync:
```python
...
client = Dial(api_key='your-api-key', base_url='https://your-dial-instance.com')

completion = client.chat.completions.create(
    deployment_name='gpt-35-turbo',
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

Async:
```python
...
async_client = AsyncDial(api_key='your-api-key', base_url='https://your-dial-instance.com')
completion = await async_client.chat.completions.create(
    deployment_name='gpt-35-turbo',
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

Example of response
```python
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

### With streaming

Sync
```python
...
client = Dial(api_key='your-api-key', base_url='https://your-dial-instance.com')

completion = client.chat.completions.create(
    deployment_name='gpt-35-turbo',
    # Specify stream parameter
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

Async
```python
...
async_client = AsyncDial(api_key='your-api-key', base_url='https://your-dial-instance.com')
completion = await async_client.chat.completions.create(
    deployment_name='gpt-35-turbo',
    # Specify stream parameter
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

Example of chunk objects
```python
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

## Working with files

### Working with URLs
Files resource operates with URL-like objects, that can be created using `pathlib.PurePosixPath` or `str` objects. You can use them to create new URL-like objects or to get string representation of them.


If you want to upload file to your bucket inside of DIAL Storage, use

 `client.my_files_home()`

or

`await async_client.my_files_home()`

to get the URL of your bucket and then use it to upload the file.

Function will return path-like object, so you can use it like this:
```python
sync_client.files.upload(
    url=sync_client.my_files_home() / 'some-relative-path/my-file.txt',
    ...
)

async_client.files.upload(
    url=await async_client.my_files_home() / 'some-relative-path/my-file.txt',
    ...
)

```
If you already have relative URL like `files/...`, you can use it as well:
```python
relative_url = 'files/test-bucket/some-relative-path/my-file.txt'
sync_client.files.upload(
    url=relative_url,
    ...
)
```
or absolute URL:
```python
absolute_url = 'http://dial.core/v1/files/test-bucket/some-relative-path/my-file.txt'
sync_client.files.upload(
    url=absolute_url,
    ...
)
```
If you will provide invalid URL to the function, it will raise `InvalidDialURLException`.


### Uploading files

```python
with open('./some-local-file.txt', "rb") as file:
    # Sync client
    sync_client.files.upload(
        url=sync_client.my_files_home() / 'some-relative-path/my-file.txt',
        file=file
    )
    # Async client
    await async_client.files.upload(
        url=await async_client.my_files_home() / 'some-relative-path/my-file.txt',
        file=file
    )
```

File can contain just raw bytes or file-like object.

To specify filename and content type of uploaded file, you should use tuple instead of file object:

```python
sync_client.files.upload(
    ...
    file=('filename.txt', 'text/plain', file)
)
```

### Downloading files


```python
result = client.files.download(
    url=client.my_files_home() / 'relative_folder/my-file.txt'
)

result = await async_client.files.download(
    url=await async_client.my_files_home() / 'relative_folder/my-file.txt'
)
```
Result would be object of type `FileDownloadResponse`, that you can iterate by byte chunks:

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
result.write_to('./some-local-file.txt')
# Async
await result.awrite_to('./some-local-file.txt')
```

### Deleting files

```python

await sync_client.files.delete(
    url=sync_client.my_files_home() / 'relative_folder/my-file.txt'
)

await async_client.files.delete(
    url=await async_client.my_files_home() / 'relative_folder/my-file.txt'
)
```

### Accessing metadata

```python
metadata = await async_client.files.metadata(
    url=await async_client.my_files_home() / 'relative_folder/my-file.txt'
)
```
Metadata would look like this:
```python
FileMetadata(
    name='my-file.txt',
    parent_path='relative_folder',
    bucket='my-bucket',
    url='files/my-bucket/test-folder-artifacts/test-file',
    node_type='ITEM',
    resource_type='FILE',
    content_length=12,
    content_type='application/octet-stream',
    items=None,
    updatedAt=1724836248936,
    etag='9749fad13d6e7092a6337c4af9d83764',
    createdAt=1724836229736
)
```
## Applications


### List applications

```python
# Sync
applications = client.application.list()
# Async
applications = await async_client.application.list()
```

Result would be list of `Application` objects:
```python
[
Application(
    object='application',
    id='app_id',
    description='',
    application='app_id',
    display_name='app with attachments',
    display_version='0.0.0',
    icon_url='...',
    reference='...',
    owner='organization-owner',
    status='succeeded',
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
        allow_resume=True
    ),
    input_attachment_types=['image/png', 'text/txt', 'image/jpeg'],
    defaults={},
    max_input_attachments=0,
    description_keywords=[]
),
...
]
```

### Get application by id

```python
# Sync
application = client.application.get('app_id')
# Async
application = await async_client.application.get('app_id')
```

Result would be `Application` object, as in example above.




