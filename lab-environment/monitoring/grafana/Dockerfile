# 步骤 1: 选择一个官方的 Grafana 镜像作为基础
# 我们选择一个具体的版本以保证可复现性。
FROM grafana/grafana:9.2.0

# 步骤 2: 切换到 root 用户以修改文件权限
# Grafana 官方镜像默认使用非 root 用户 (grafana)，我们需要临时切换以复制文件。
USER root

# 步骤 3: 复制数据源配置文件
# 将我们本地的 datasource.yml 文件复制到容器内 Grafana 的预配置数据源目录。
# Grafana 启动时会自动扫描这个目录并加载所有 .yml 文件。
COPY ./datasource.yml /etc/grafana/provisioning/datasources/datasource.yml

# 步骤 4: 复制仪表盘定义文件
# 将我们本地的 dashboard.json 文件复制到容器内 Grafana 的预配置仪表盘目录。
# Grafana 启动时会自动扫描这个目录并加载所有 .json 文件。
COPY ./dashboard.json /etc/grafana/provisioning/dashboards/main.json

# 步骤 5: 将用户切换回非 root 的 grafana 用户
# 这是安全最佳实践，确保容器内的进程以最小权限运行。
USER grafana

