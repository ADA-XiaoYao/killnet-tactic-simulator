# 步骤 1: 选择一个基础镜像
# 我们选择一个官方的、轻量级的 Python 3.10 镜像作为起点。
FROM python:3.10-slim

# 步骤 2: 设置工作目录
# 在容器内部创建一个名为 /app 的目录，并将其设置为后续命令的执行目录。
WORKDIR /app

# 步骤 3: 更新包管理器并安装基础网络工具
# - apt-get update: 更新apt包列表，确保能安装最新的软件。
# - apt-get install -y: "-y"表示自动确认安装。
#   - iputils-ping: 提供 ping 命令，用于测试网络连通性。
#   - net-tools: 提供 netstat 等命令，用于查看网络状态。
#   - tcpdump: 一个强大的网络抓包工具，非常适合在调试时分析流量。
# - && rm -rf /var/lib/apt/lists/*: 安装后清理apt缓存，减小最终镜像的体积。
RUN apt-get update && apt-get install -y \
    iputils-ping \
    net-tools \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# 步骤 4: 复制并安装所有攻击脚本的Python依赖
# 我们在 docker-compose.yml 中会将 attack-scripts 目录挂载到容器的 /scripts 目录。
# 在构建镜像时，我们需要先将这些 requirements.txt 文件复制进来并安装依赖。
# 注意：COPY指令的源路径是相对于构建上下文（项目根目录）的。
COPY ./attack-scripts/1_volume_based/requirements.txt /tmp/reqs_volume.txt
COPY ./attack-scripts/2_protocol_exhaustion/requirements.txt /tmp/reqs_protocol.txt
COPY ./attack-scripts/3_application_flood/requirements.txt /tmp/reqs_application.txt
COPY ./attack-scripts/4_multi_vector/requirements.txt /tmp/reqs_multi_vector.txt

# 使用 pip 安装所有依赖。
# --no-cache-dir: 不缓存下载的包，可以减小镜像体积。
# 我们将所有安装命令串联起来，以减少镜像的层数。
RUN pip install --no-cache-dir -r /tmp/reqs_volume.txt && \
    pip install --no-cache-dir -r /tmp/reqs_protocol.txt && \
    pip install --no-cache-dir -r /tmp/reqs_application.txt && \
    pip install --no-cache-dir -r /tmp/reqs_multi_vector.txt

# 步骤 5: 设置容器启动后执行的默认命令
# CMD ["/bin/bash"]: 当我们通过 `docker-compose exec attacker bash` 进入容器时，
# 这个命令不是必须的。但如果我们直接运行 `docker run attacker`，
# 它会默认启动一个bash shell，让我们直接进入交互式环境。
CMD ["/bin/bash"]

