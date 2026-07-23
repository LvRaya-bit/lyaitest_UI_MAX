# Docker 镜像构建与推送操作文档

## 概述
本文档记录如何将 LYAITEST 项目打包成 Docker 镜像，并推送到 Docker Hub 仓库，以便在任何安装了 Docker 的机器上快速部署运行。

---

## 第1步：创建 Dockerfile

在项目根目录创建 `Dockerfile`（无后缀名）：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
第2步：构建镜像
bash
docker build -t lyaitest .
参数	说明
-t lyaitest	给镜像命名为 lyaitest
.	使用当前目录作为构建上下文
首次构建约需 15-30 分钟（取决于网络和依赖数量），后续构建会使用缓存加快速度。

第3步：登录 Docker Hub
bash
docker login
输入你的 Docker Hub 用户名和密码。

第4步：给镜像打标签
bash
docker tag lyaitest 你的用户名/lyaitest:latest
示例：

bash
docker tag lyaitest lvraya/lyaitest:latest
部分	说明
lyaitest	本地镜像名
你的用户名/lyaitest	远程仓库地址
:latest	标签（版本号）
第5步：推送镜像到 Docker Hub
bash
docker push 你的用户名/lyaitest:latest
第6步：查看推送结果
打开 https://hub.docker.com

点击右上角头像 → My Profile

点击 Repositories 选项卡

确认镜像仓库已出现

第7步：在其他电脑上运行
bash
docker pull 你的用户名/lyaitest:latest
docker run -p 8000:8000 你的用户名/lyaitest:latest
常用命令速查
命令	说明
docker build -t 镜像名 .	构建镜像
docker images	查看本地所有镜像
docker rmi 镜像名	删除本地镜像
docker login	登录 Docker Hub
docker tag 本地镜像 仓库地址	给镜像打标签
docker push 仓库地址	推送到 Docker Hub
docker pull 仓库地址	从 Docker Hub 拉取镜像
docker run -p 8000:8000 镜像名	运行容器
docker ps	查看运行中的容器
docker stop 容器ID	停止容器
修改镜像可见性（公开 / 私有）
类型	说明
公开（Public）	所有人可以拉取使用，适合开源项目
私有（Private）	仅自己和授权用户可以拉取
登录 Docker Hub，进入仓库页面

点击 Settings 选项卡

找到 Visibility → Change visibility

选择 Public 或 Private

常见问题
问题	解决方案
docker: command not found	Docker Desktop 未安装或未启动
denied: requested access to the resource is denied	未登录或仓库名错误，执行 docker login
推送速度慢	镜像较大，首次推送需要时间，与网络有关
镜像太大	考虑使用更轻量的基础镜像（如 alpine）
私有仓库拉取失败	需要先 docker login 登录才能拉取私有镜像
