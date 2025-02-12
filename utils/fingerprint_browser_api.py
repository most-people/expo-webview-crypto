import time
from functools import wraps
from threading import RLock

import requests


def wait_before_calling(wait_time=2.0):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with self.lock:
                time.sleep(wait_time)
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


# 定义一个基础的浏览器实例类
class BrowserInstance:
    def __init__(self, browser_id, seq, response_data):
        self.browser_id = browser_id
        self.seq = seq
        self.response_data = response_data

    @property
    def port(self):
        return self.response_data.get("data", {}).get("http")

    @property
    def ws(self):
        return self.response_data.get("data", {}).get("ws")

    @property
    def msg(self):
        return self.response_data.get("msg")

    @property
    def success(self):
        return self.response_data.get("success")

    def __str__(self):
        return (
            f"BrowserInstance(browser_id={self.browser_id}, seq={self.seq}, port={self.port}, "
            f"raw_response={self.response_data})"
        )


# 针对 BitBrowser 的特定实现，继承自 BrowserInstance


# 针对 AdsPower 的特定实现，继承自 BrowserInstance
class AdsPowerInstance(BrowserInstance):
    @property
    def port(self):
        try:
            return int(self.response_data.get("data", {}).get("debug_port", ""))
        except ValueError:
            return None
        # return int(self.response_data.get("data", {}).get("debug_port", ""))


class ApiBase:
    def __init__(self, host, port, headers):
        self.base_url = f"http://{host}:{port}"
        self.headers = headers
        self.lock = RLock()
        self.sleep_time = 2

    def _send_request(self, endpoint, method="post", **params):
        with self.lock:
            time.sleep(self.sleep_time)
            url = f"{self.base_url}/{endpoint}"
            params = {k: v for k, v in params.items() if v is not None}
            # 使用 `json` 参数直接传递字典数据，而不手动转换
            if method.lower() == "post":
                response = requests.post(
                    url,
                    json=params,
                    headers=self.headers,
                    proxies={"http": None, "https": None},
                )
            else:
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    proxies={"http": None, "https": None},
                )

            return response.json()


class AdsPowerApi(ApiBase):
    def __init__(self, host="127.0.0.1", port=50325):
        super().__init__(host, port, {"Content-Type": "application/json"})
        self.group_infos = None

    def check_api(self):
        return self._send_request("status", "get")

    def group_list(self, group_name="", page=1, page_size=2000):
        res = self._send_request(
            "api/v1/group/list",
            "get",
            **{"group_name": group_name, "page": page, "page_size": page_size},
        )
        group_infos = []
        for group in res["data"]["list"]:
            group_infos.append(
                {
                    "group_id": group["group_id"],
                    "group_name": group["group_name"],
                    "remark": group["remark"],
                }
            )
        # self.group_infos = res["data"]["list"]
        self.group_infos = group_infos
        return res

    def browser_list(
            self, group_id=None, user_id=None, serial_number=None, page=1, page_size=100
    ):
        return self._send_request(
            "api/v1/user/list",
            "get",
            **{
                "group_id": group_id,
                "user_id": user_id,
                "serial_number": serial_number,
                "page": page,
                "page_size": page_size,
            },
        )

    def create_browser(
            self,
            name="api创建",
            open_urls=None,
            group_id="0",
            user_proxy_config=None,
            fingerprint_config=None,
    ):
        # user_proxy_config对象是账号代理配置的参数信息，AdsPower支持市面上常用的代理软件和协议。
        # 属性名称	类型	必需	默认值	示例	说明
        # proxy_soft	text	是	-	luminati	目前支持的代理有luminati，lumauto，oxylabsauto，922S5，ipideaauto，ipfoxyauto，922S5auth，kookauto，ssh，other，no_proxy
        # proxy_type	text	否	-	socks5	代理的类型，目前支持的类型有http，https，socks5；no_proxy可不传
        # proxy_host	text	否	-	pr.oxylabs.io	代理服务器的地址，可以填域名或者IP；no_proxy可不传
        # proxy_port	text	否	-	123	代理服务器的端口号；no_proxy可不传
        # proxy_user	text	否	-	abc	代理需要登录时的账号
        # proxy_password	text	否	-	xyz	代理需要登录时的密码
        # proxy_url	text	否	-	http://www.xxx.com/	该URL用于移动代理，仅支持http/https/socks5的代理。
        if user_proxy_config is None:
            user_proxy_config = {"proxy_soft": "no_proxy"}
        if fingerprint_config is None:
            fingerprint_config = {}
        return self._send_request(
            "api/v1/user/create",
            **{
                "name": name,
                "open_urls": open_urls,
                "group_id": group_id,
                "user_proxy_config": user_proxy_config,
                "fingerprint_config": fingerprint_config,
            },
        )

    def open_browser(
            self,
            user_id="",
            serial_number="",
            open_tabs=0,
            ip_tab=1,
            new_first_tab=0,
            launch_args=None,
            headless=0,
            disable_password_filling=0,
            clear_cache_after_closing=0,
            enable_password_saving=0,
    ):
        params = {
            "user_id": user_id if user_id else None,
            "serial_number": serial_number if serial_number else None,
            "open_tabs": open_tabs,
            "ip_tab": ip_tab,
            "new_first_tab": new_first_tab,
            "launch_args": launch_args,
            "headless": headless,
            "disable_password_filling": disable_password_filling,
            "clear_cache_after_closing": clear_cache_after_closing,
            "enable_password_saving": enable_password_saving,
        }
        res = self._send_request("api/v1/browser/start", "get", **params)
        # return self._send_request("api/v1/browser/start", "get", **params)
        return AdsPowerInstance(user_id, serial_number, res)

    def close_browser(self, user_id=None, serial_number=None):
        return self._send_request(
            "api/v1/browser/stop",
            "get",
            **{"user_id": user_id, "serial_number": serial_number},
        )

    def delete_browsers(self, user_ids: list = None):
        # ["xxx", "yyy", "zzz"]
        if user_ids is None:
            user_ids = []
        # user_ids = json.dumps(user_ids) if user_ids is not None else None
        # print(user_ids)
        return self._send_request("api/v1/user/delete", **{"user_ids": user_ids})

    def update_browser(
            self,
            user_id: str,
            open_urls=None,
            user_proxy_config=None,
            fingerprint_config=None,
    ):
        return self._send_request(
            "api/v1/user/update",
            **{
                "user_id": user_id,
                "open_urls": open_urls,
                "user_proxy_config": user_proxy_config,
                "fingerprint_config": fingerprint_config,
            },
        )


if __name__ == "__main__":
    pass
    # import sys
    # from pathlib import Path
    #
    # BASEDIR = Path(sys.argv[0]).parent.resolve()
    # api = BitBrowserApi(cache_folder=BASEDIR)
    # api = AdsPowerApi()
    # api = BitBrowserApi()
    # api = FbBrowserApi()
    # r = api.open_browser(54)
    # print(r.port)
    # # print(window.response_data)
    # print(r.msg)
    # res = api.update_browser_detail_cache()
    # start_time = time.time()
    # print(api.get_seq_from_cache("6789f03e8e5e46b4bc33b006664cd980"))
    # print(api.get_seq_from_cache("6789f03e8e5e46b4bc33b006664cd980"))
    # print(time.time() - start_time)
    # hub_api = HubStudioApi()
    # response = hub_api.env_list(tagNames=["001"])
    # print(response)
    # print(len(response))
