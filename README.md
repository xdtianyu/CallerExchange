# CallerExchange
CallerInfo 离线数据管理服务, 服务主要有三个过程

1\. 从 leancloud 下载所有用户上报的数据

2\. 对数据进行过滤处理，生成离线数据库文件

3\. 上传文件到七牛存储

## 运行

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt -I
python exchange.py
```
