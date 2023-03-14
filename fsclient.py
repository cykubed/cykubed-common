import argparse
import asyncio

import aiofiles
import aiofiles.os
import aiohttp
from aiohttp import ClientError
from loguru import logger

from common.exceptions import FilestoreWriteError, FilestoreReadError
from common.settings import settings


class AsyncFSClient(object):
    def __init__(self):
        self.servers = settings.FILESTORE_SERVERS.split(',')
        timeout = aiohttp.ClientTimeout(total=settings.FILESTORE_TOTAL_TIMEOUT,
                                        connect=settings.FILESTORE_CONNECT_TIMEOUT,
                                        sock_connect=settings.FILESTORE_CONNECT_TIMEOUT,
                                        sock_read=settings.FILESTORE_READ_TIMEOUT)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def upload(self, path):

        async def upload_file(host):
            try:
                file = {'file': open(path, 'rb')}
                resp = await self.session.post(f'http://{host}', data=file)
                return resp.status == 200
            except ClientError as ex:
                logger.warning(f'Failed to upload to {host} ({ex}): assume down')
                return False

        tasks = [upload_file(h) for h in self.servers]
        results = await asyncio.gather(*tasks)
        successful_writes = len(list(filter(lambda x: x, results)))
        if successful_writes < settings.FILESTORE_MIN_WRITE:
            if not successful_writes:
                raise FilestoreWriteError(f"Could not write to any replicas")
            else:
                raise FilestoreWriteError(f"Only wrote to a single replica")

    async def close(self):
        await self.session.close()

    async def download(self, fname, target=None):
        """
        Fetch from all servers, but return when any succeeds
        :param fname: file name
        :param target: target (local) file path
        :return:
        """
        if not target:
            target = fname

        async def fetch(host):
            try:
                async with aiofiles.tempfile.NamedTemporaryFile('wb', delete=False) as f:
                    async with self.session.get(f'http://{host}/{fname}') as resp:
                        async for chunk in resp.content.iter_chunked(settings.CHUNK_SIZE):
                            await f.write(chunk)
                    await aiofiles.os.rename(f.name, target)
                    return True
            except ClientError:
                return False

        tasks = [fetch(h) for h in self.servers]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        if not done:
            raise FilestoreReadError("Failed to download from any replica")
        # cancel the others
        for task in pending:
            task.cancel()


async def upload(file: str):
    client = AsyncFSClient()
    try:
        await client.upload(file)
    finally:
        await client.close()


async def download(file: str, target: str = None):
    client = AsyncFSClient()
    try:
        await client.download(file, target)
    finally:
        await client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', choices=['set', 'get'])
    parser.add_argument('file', type=str)
    parser.add_argument('-o', '--output', type=str)
    args = parser.parse_args()
    if args.cmd == 'set':
        asyncio.run(upload(args.file))
    else:
        asyncio.run(download(args.file, args.output))

