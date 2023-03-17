import argparse
import asyncio
import subprocess
import time

import aiofiles
import aiofiles.os
import aiohttp
import aioshutil
from aiohttp import ClientError
from loguru import logger

from common.exceptions import FilestoreWriteError, FilestoreReadError
from common.settings import settings


class AsyncFSClient(object):
    """
    Simple client for the distributed flat file store
    """

    def __init__(self):
        """
        Note that this will block until it can read all file store nodes
        """

        self.servers = settings.FILESTORE_SERVERS.split(',')

    async def connect(self):
        timeout = aiohttp.ClientTimeout(total=settings.FILESTORE_TOTAL_TIMEOUT,
                                        connect=settings.FILESTORE_CONNECT_TIMEOUT,
                                        sock_connect=settings.FILESTORE_CONNECT_TIMEOUT,
                                        sock_read=settings.FILESTORE_READ_TIMEOUT)
        self.session = aiohttp.ClientSession(timeout=timeout)
        # block until we can connect to all servers
        start = time.time()

        async def ping(h):
            resp = await self.session.get(f'http://{h}/hc')
            return resp.status == 200

        while time.time() - start < 300:
            tasks = [asyncio.create_task(ping(host)) for host in self.servers]
            results = await asyncio.gather(*tasks)
            fails = len(self.servers) - len(list(filter(lambda x: x, results)))
            if not fails:
                return
            logger.info(f"Cannot connect to {fails} file servers: waiting...")
            await asyncio.sleep(5)
        raise FilestoreReadError()

    async def upload(self, path):
        """
        Upload a file. Since this is a flat filestore only the final path segment is used as a key
        :param path: source path
        :return: True if fail successfully stored
        """
        async def upload_file(host):
            try:
                file = {'file': open(path, 'rb')}
                resp = await self.session.post(f'http://{host}/api/upload', data=file)
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
        """
        Gracefully close the session
        """
        await self.session.close()

    async def exists(self, fname) -> bool:
        """
        Check that a file exists on at least one node
        """
        async def do_head(host):
            try:
                async with self.session.head(f'http://{host}/{fname}') as resp:
                    return resp.status == 200
            except ClientError:
                return False

        tasks = [asyncio.create_task(do_head(h)) for h in self.servers]
        done, pending = await asyncio.wait(tasks)
        return len([True for t in done if t.result()]) > 0

    async def delete(self, fname) -> bool:
        """
        Delete the file from all accessible nodes
        """
        async def do_delete(host):
            try:
                async with self.session.delete(f'http://{host}/{fname}') as resp:
                    return resp.status == 200
            except ClientError:
                return False

        tasks = [asyncio.create_task(do_delete(h)) for h in self.servers]
        done, pending = await asyncio.wait(tasks)
        return bool(done)

    async def download_and_untar(self, fname, target_dir):
        """
        Download the file and unpack into the target directory
        :param fname: file name
        :param target_dir: target directory
        """

        tarfile = await self.download(fname)

        def untar():
            logger.info(f'Unpacking {tarfile}')
            subprocess.run(f'/bin/tar xf {tarfile} -I lz4', cwd=target_dir, shell=True, check=True,
                           encoding=settings.ENCODING)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, untar)
        await aiofiles.os.remove(tarfile)

    async def download(self, fname, target=None) -> str:
        """
        Fetch from all servers, but return when any succeeds
        :param fname: file name
        :param target: target (local) file path. If None then return tempfile
        :return: local path of downloaded file.
        """
        async def fetch(host):
            try:
                suffix = fname[fname.find('.'):]
                async with aiofiles.tempfile.NamedTemporaryFile('wb', delete=False, suffix=suffix) as f:
                    async with self.session.get(f'http://{host}/{fname}') as resp:
                        if resp.status != 200:
                            return None
                        async for chunk in resp.content.iter_chunked(settings.CHUNK_SIZE):
                            await f.write(chunk)
                    await f.flush()
                    if target:
                        await aioshutil.move(f.name, target)
                        return target
                    return f.name
            except ClientError:
                return None

        tasks = [asyncio.create_task(fetch(h)) for h in self.servers]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        if not done:
            raise FilestoreReadError("Failed to download from any replica")
        # cancel the others
        for task in pending:
            task.cancel()
        return list(done)[0].result()


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
        logger.info(f"Downloaded {file}")
    finally:
        await client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', choices=['set', 'get'])
    parser.add_argument('file', type=str)
    args = parser.parse_args()
    if args.cmd == 'set':
        asyncio.run(upload(args.file))
    else:
        print(asyncio.run(download(args.file)))

