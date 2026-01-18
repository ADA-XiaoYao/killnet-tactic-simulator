# 步骤 1: 选择一个官方的 Nginx 镜像
# 我们选择一个基于 Alpine Linux 的 Nginx 镜像，它非常轻量。
FROM nginx:1.21-alpine

# 步骤 2: 安装基础网络分析工具
# 虽然这是靶机，但安装一些工具可以方便我们登录进去排查问题。
# - apk add --no-cache: Alpine Linux 使用 apk 作为包管理器。--no-cache 表示不保留缓存，减小镜像体积。
#   - iputils: 提供 ping 命令。
#   - net-tools: 提供 netstat 命令，对于观察SYN_RECV状态至关重要。
#   - tcpdump: 可以在靶机端抓包，从受害者视角分析攻击流量。
RUN apk add --no-cache iputils net-tools tcpdump

# 步骤 3: 复制自定义的 Nginx 配置文件
# 我们将使用一个自定义的配置文件来代替默认配置。
# 这个文件将从同级目录复制到容器内的 Nginx 配置目录。
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 步骤 4: 创建一个简单的网页作为攻击目标
# 这可以让我们在浏览器中访问时，确认服务是否正常。
RUN echo "<html><head><title>Target Server</title></head><body><h1>This is the Target Server.</h1><p>Ready for simulation.</p></body></html>" > /usr/share/nginx/html/index.html

# Nginx 基础镜像已经包含了暴露80端口和启动Nginx的指令，我们无需重复。
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]

