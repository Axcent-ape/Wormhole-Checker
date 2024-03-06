import asyncio
import aiohttp
import random
from fake_useragent import UserAgent


class CheckEligible:
    def __init__(self, thread: int):
        self.thread = thread

        headers = {"User-Agent": UserAgent().random}
        self.session = aiohttp.ClientSession(trust_env=True, headers=headers)

    async def check_eligible(self):
        act: str = self.get_account()
        if not act: return False

        if '::' in act:
            address, proxy = act.split('::')
        else:
            address = act
            proxy = None

        if address:
            # is evm
            if address.startswith('0x') and len(address) == 42:
                url = f"https://prod-flat-files-min.wormhole.com/{address}_2.json"
                ape = 1e18

            # is aptos/sui
            elif address.startswith('0x') and len(address) == 66:
                url = f"https://prod-flat-files-min.wormhole.com/{address}_22.json"
                ape = 1e18

            # is solana
            elif len(address) == 44:
                url = f"https://prod-flat-files-min.wormhole.com/{address}_1.json"
                ape = 1e9

            else: return True

            resp = await self.session.get(url, proxy=proxy)
            try:
                resp_json = await resp.json()

                if resp_json:
                    res_text = f"{address}:{resp_json.get('amount') / ape}"
                    print(f'{self.thread} | {res_text}')

                    with open('data/eligible.txt', 'a') as f:
                        f.write(f'\n{res_text}')
            except: pass

            return True
        return False

    async def logout(self):
        await self.session.close()

    @staticmethod
    def get_account():
        with open('data/accounts.txt', 'r') as file:
            keys = file.readlines()

        if not keys: return False
        random_key = random.choice(keys)
        keys.remove(random_key)

        with open('data/accounts.txt', 'w') as file:
            file.writelines(keys)

        return random_key.strip()

    async def change_useragent(self):
        self.session.headers['User-Agent'] = UserAgent().random


async def check(thread):
    checker = CheckEligible(thread)

    while True:
        if not await checker.check_eligible(): break
        await checker.change_useragent()
    await checker.logout()


async def main():
    print("Автор чекера: https://t.me/ApeCryptor")

    thread_count = int(input("Введите кол-во потоков: "))
    thread_count = 50 if thread_count > 50 else thread_count
    tasks = []
    for thread in range(1, thread_count+1):
        tasks.append(asyncio.create_task(check(thread)))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
