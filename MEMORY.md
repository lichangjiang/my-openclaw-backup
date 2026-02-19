# MEMORY.md - Long-term Memory

## 用户信息

### 基本信息
- **姓名:** 李长江 (River Lee)
- **称呼:** River 或 长江
- **职业:** 软件工程师
- **常住地:** 中国广东省广州市
- **时区:** UTC+8
- **偏好语言:** 中文（技术术语可用英语）

### 技术栈（2026-02-17 更新）

**主要开发技术:**
- **后端:** Java + Spring Boot
- **数据库:** PostgreSQL
- **缓存:** Redis
- **消息队列:** Kafka
- **ORM:** JPA 或 MyBatis Plus
- **AI应用开发:** Python

**感兴趣的技术:**
- Go
- TypeScript
- Scala
- 其他新兴技术栈

**技术特点:**
- 熟悉企业级 Java 后端开发
- 有 Kafka 消息队列经验
- 了解 Redis 缓存机制
- 熟悉 PostgreSQL 数据库
- 探索 AI 应用开发（Python）
- 了解 Kubernetes (K8s) 容器化部署

**技术组合示例:**
- Spring Boot + JPA/MyBatis Plus + PostgreSQL + Redis + Kafka
- Python + AI框架（用于AI应用）
- Docker + K8s（应用部署）

**部署流程:**
- 使用 Docker 打包应用镜像
- 通过 Kubernetes 进行容器编排和部署

**开发环境:**
- **服务器OS:** Linux（首选 Ubuntu）
- **个人电脑OS:** Windows
- **开发方式:** 必须结合 WSL (Windows Subsystem for Linux)

---

## 系统配置

### 每日技术摘要推送系统

⚠️ **关键问题：** Cron announce delivery 机制故障（2026-02-16 确认）

**问题详情：**
- 错误信息：`cron announce delivery failed`
- 连续失败次数：1+
- 根本原因：OpenClaw cron 的 announce 功能与 Feishu 集成存在故障
- 用户确认：从未收到自动化推送

**临时解决方案（已验证有效）：**
- 直接使用 `message` 工具发送到 Feishu
- 手动运行脚本后调用推送 API
- 时间：2026-02-16 16:15 UTC 成功验证

**Cron 任务：**
- 任务 ID：40c0b192-29af-4a9c-827a-d1a32e1e5edf
- 推送时间：每天 22:30（北京时间）14:30 UTC
- 会话类型：isolated（独立会话执行）
- 状态：⚠️ 配置正确但推送失败

**长期解决方案（待用户选择）：**

**方案 1：修改脚本直接调用 OpenClaw API（推荐）**
- 在 `daily_tech_digest_system.py` 中添加推送逻辑
- 脚本生成摘要后直接调用 `sessions_send` 或 `message` 工具
- 不依赖 cron 的 announce 功能
- 优点：完全控制推送流程，可靠性高，完全自动化
- 缺点：需要修改脚本代码
- 文件位置：`/home/lichangjiang/.openclaw/workspace/daily_tech_digest_system.py`

**方案 2：手动触发每天推送**
- 每天 22:30 由我手动运行脚本并推送
- 使用 `message` 工具直接推送
- 优点：快速解决，无需修改代码，立即可用
- 缺点：需要人工介入，不够自动化，依赖我在线

**用户要求：**
- "我希望我的定时任务都正常，而不是删除"
- 用户希望所有 cron 任务保持启用并正常工作
- 不接受删除任务作为解决方案

**推送脚本状态：**
- 文件：`/home/lichangjiang/.openclaw/workspace/daily_tech_digest_system.py`
- 依赖：feedparser (已安装)
- RSS 时间解析：✅ 已修复（2026-02-17）
  - 旧方法：`feedparser._parse_date`（不可用）
  - 新方法：`email.utils.parsedate_to_datetime`（支持 RFC 2822）
  - 验证：成功识别最新文章（3天内）
- 测试：✅ 成功获取 RSS 源并生成摘要
- 手动推送：✅ 2026-02-16 16:15 UTC 成功发送

**推送配置：**
- 每日文章数量：10 篇
- 初始比例：编程 3 篇（30%）/ AI 5 篇（50%）/ 产品 2 篇（20%）
- 动态调整：根据用户点击历史自动计算新比例

**数据源：**
- 主要源（BestBlogs 精选）：
  - 精选：https://www.bestblogs.dev/zh/feeds/rss?featured=y
  - 编程：https://www.bestblogs.dev/zh/feeds/rss?category=programming&type=article
  - AI：https://www.bestblogs.dev/en/feeds/rss?category=ai&minScore=90
  - 产品：https://www.bestblogs.dev/zh/feeds/rss?category=product
- 补充源：
  - Hacker News: https://hnrss.org/frontpage
  - Reddit: https://www.reddit.com/r/programming/.rss
  - OpenAI: https://openai.com/blog/rss.xml

**文章排序策略（多维度评分，满分 100）：**
1. AI 评分（40 分）：文章本身的质量评分
2. 主题相关度（30 分）：是否匹配用户关注的热门主题
3. 来源优先级（20 分）：BestBlogs > Hacker News > 其他
4. 时间新鲜度（10 分）：发布时间（越新越好）

**综合评分公式：**
```
综合评分 = (AI评分 × 4) + (主题相关度 × 30) + (来源优先级 × 20) + (时间新鲜度 × 10)
```

**个性化推荐：**
- 自动记录用户每次点击
- 分析类别偏好（编程/AI/产品）
- 识别热门主题（React/Python/Rust/Go 等）
- 每天动态计算并调整推荐比例
- 生成个性化推荐理由

**数据存储：**
- 存储位置：/home/lichangjiang/.openclaw/workspace/user_preferences.json
- 存储模式：全量保留（不限制历史记录数量）
- **自动归档：** 每 6 个月自动归档（Cron 任务已配置）
  - 任务 ID：612fedfc-4e45-497d-a3a1-28fbf8cb34a2
  - 归档周期：每 180 天（约 6 个月）
  - 归档内容：180 天前的点击记录
  - 归档文件：user_preferences_archive_YYYYMMDD.json

**CLI 管理工具：**
- 查看统计：`python3 preferences_cli.py stats`
- 分析偏好：`python3 preferences_cli.py analyze`
- 查询记录：`python3 preferences_cli.py query --start-date YYYY-MM-DD`
- 归档数据：`python3 preferences_cli.py archive 365`

**反馈机制：**
- 回复"编程更多" / "AI 更多" / "产品更多"调整明日比例
- 回复"偏好分析"查看阅读习惯分析报告
- 回复"重置偏好"恢复默认配置

### 用户决策

**RSS 订阅方案：** 用户选择了 RSS 订阅方案（而不是 API 集成）来获取每日技术摘要，因为：
- 更简单可靠
- 无需 API 密钥管理
- 可以直接在 RSS 阅读器中订阅

**数据存储策略：** 用户选择了全量保留模式（2026-02-16），因为：
- 本地机器内存和存储充足
- 希望保留完整的历史数据
- 支持长期的个性化分析和趋势分析

**Reddit 登录：** 用户决定延迟（2026-02-16），可能的解决方案：
1. 使用 Reddit API（需要创建应用获取凭证）
2. 从其他设备导出 Cookie
3. 安装 Reddit 相关技能直接使用 API

**阻塞原因：** agent-browser 在无头浏览器模式下被 Cloudflare 拦截
**环境限制：** Ubuntu 24.04.2 LTS 无图形界面服务器

### OneDrive 配置（2026-02-16）

**安装信息：**
- 客户端：onedrive-cli (Snap v2.5.9)
- 安装方式：`sudo snap install onedrive-cli`
- 安装时间：2026-02-16 07:38 UTC

**认证配置：**
- 认证方式：OAuth2（网页授权）
- 授权完成：2026-02-16 08:04 UTC
- 刷新令牌：已生成并保存

**同步配置：**
- 同步目录：`~/onedrive`
- 配置文件：`~/snap/onedrive-cli/40/.config/onedrive/config`
- 数据库：`~/snap/onedrive-cli/40/.config/onedrive/items.sqlite3`
- 后台服务：已启动，进程 ID：801343

**功能特性：**
- ✅ 多端共享：所有文件自动同步到 OneDrive
- ✅ 实时监控：文件变化 5 分钟内自动同步
- ✅ 双向同步：本地和远程保持一致
- ✅ 选择性同步：支持排除特定文件和目录

**使用方式：**
```bash
# 查看同步目录
ls -lh ~/onedrive

# 查看同步日志
tail -f ~/onedrive.log

# 查看同步状态
/snap/bin/onedrive-cli --display-sync-status

# 手动触发同步
cd ~/onedrive && /snap/bin/onedrive-cli --sync
```

**注意事项：**
- OneDrive 客户端在后台持续运行，不要手动停止进程
- 将需要多端共享的文件放入 `~/onedrive` 目录
- 其他设备上的 OneDrive 客户端会自动同步

### OpenWrt 软路由配置（2026-02-16）

**网络信息：**
- IP 地址：192.168.1.201
- SSH 端口：22（开放）
- 网络延迟：1.4-2.0 ms（正常）
- 连接状态：✅ 正常

**SSH 配置：**
- 用户名：root（密码认证已验证）
- 密码：9kON!ZXq3RyxZ5（已确认正确）
- 认证状态：✅ 密码认证成功

**SSH 公钥认证：**
- ❌ **公钥认证失败**（Dropbear 固件版本过旧）
- 公钥位置：`/etc/dropbear/authorized_keys`
- 公钥类型：RSA (ed25519)
- 错误原因：Dropbear 版本过旧，不支持现代 SSH 客户端的签名算法

**问题诊断：**
- ✅ authorized_keys 文件存在
- ✅ 文件权限正确（600）
- ✅ 文件内容包含正确的公钥
- ❌ Dropbear 日志显示："Pubkey auth attempt with unknown algo"

**解决方法：**
- 当前：使用密码认证（工作正常）
- 建议：升级 OpenWrt 固件以支持现代 SSH 算法（rsa-sha2-256）
- 备选：安装支持现代算法的 SSH 服务器

**配置文件：**
- authorized_keys：`/etc/dropbear/authorized_keys`
- Dropbear UCI：`/etc/config/dropbear`

**管理命令：**
```bash
# 密码认证（推荐，当前唯一可靠方法）
sshpass -p '9kON!ZXq3RyxZ5' ssh root@192.168.1.201 <command>

# 交互式登录
ssh root@192.168.1.201

# 执行多个命令
sshpass -p '9kON!ZXq3RyxZ5' ssh root@192.168.1.201 'echo "命令1"; echo "命令2"'

# 查看系统信息
sshpass -p '9kON!ZXq3RyxZ5' ssh root@192.168.1.201 'uname -a; df -h; free -m'
```

**注意事项：**
- 当前必须使用密码认证
- 公钥认证暂时不可用，直到固件升级
- 密码已妥善保存在配置文件中

### 工作流程偏好

**代码开发和 Code Review（2026-02-18）：**
- **优先工具：** coding-agent 驱动 Claude Code
- **适用场景：**
  - 代码开发任务
  - Code Review 任务
  - 代码重构
  - Bug 修复
  - 功能实现
- **使用方式：**
  ```bash
  # 一次性任务
  bash pty:true workdir:~/project command:"claude 'Your task'"

  # 后台长时间任务
  bash pty:true workdir:~/project background:true command:"claude 'Your task'"
  ```
- **关键要点：** 必须使用 `pty:true` 参数，确保 Claude Code 正常运行
- **备注：** 对于简单或快速的任务，可以直接处理；对于复杂的代码任务，优先使用 Claude Code

**浏览器自动化（2026-02-18）：**
- **优先工具：** agent-browser CLI（内置 Playwright 浏览器）
- **适用场景：**
  - 网页数据抓取
  - 表单自动填写
  - 网站测试
  - 登录流程自动化
  - 生成截图和 PDF
- **使用方式：**
  ```bash
  # 基本流程
  agent-browser open <url>
  agent-browser snapshot -i  # 获取元素引用（@e1, @e2...）
  agent-browser click @e1     # 交互
  agent-browser screenshot [path]  # 截图

  # 复杂示例
  agent-browser open https://example.com/login
  agent-browser snapshot -i
  agent-browser fill @e1 "user@example.com"
  agent-browser fill @e2 "password"
  agent-browser click @e3
  agent-browser wait --load networkidle
  ```
- **关键要点：**
  - 内置浏览器支持，无需额外安装依赖
  - 每次页面变化后需要重新 snapshot（元素引用会失效）
  - 支持有头和无头模式
  - 支持会话持久化（保存登录状态）
- **备注：** 优先使用 agent-browser CLI，而非 OpenClaw browser tool（后者需要 Chrome 扩展）

### 技能配置

**已安装的文档处理技能（2026-02-16）：**
1. docx - Word 文档处理
2. pdf - PDF 文件处理
3. pptx - PowerPoint 演示文稿处理
4. xlsx - Excel 表格处理

**Python 依赖：**
- pypdf 6.7.0
- pdfplumber 0.11.9
- pandas 3.0.0
- openpyxl 3.1.5
- markitdown 0.1.4

**系统工具：**
- pandoc 3.1.3
- LibreOffice 24.2.7.2
- docx 9.5.3 (npm)

### 系统环境

**操作系统：** Ubuntu 24.04.2 LTS (Noble)
**内核：** 6.8.0-64-generic
**环境：** 无图形界面（headless Linux server）
**Sudo：** 无需密码（2026-02-16 确认）

**Kubernetes：**
- 集群：microk8s v1.28.15（snap）
- 地址：https://10.0.0.23:16443
- 上下文：microk8s
- 用户：lichangjiang

**SRS 服务：**
- 命名空间：srs
- 部署：srs-web-deployment
- 镜像：lichangj/srs-word:v1.0.10
- API：http://10.0.0.23:30080

**工作目录：** /home/lichangjiang/.openclaw/workspace
**主项目目录：** ~/project

## 重要上下文

### 项目位置

所有本地代码项目存储在：`~/project`

当前项目：
- claude-code-log - Claude Code 日志
- feishu-scripts - Feishu/Lark 集成脚本
- srs-word - SRS Word 项目
- tradingagents-demo - 交易代理演示
- TrendRadar - 趋势雷达项目

### Kubectl 命令（OpenClaw 执行环境）

```bash
sudo /snap/bin/microk8s.kubectl get pods --all-namespaces
sudo /snap/bin/microk8s.kubectl get deployments --all-namespaces
sudo /snap/bin/microk8s.kubectl describe deployment <name> -n <namespace>
sudo /snap/bin/microk8s.kubectl set image deployment/<deployment> <container>=<image> -n <namespace>
sudo /snap/bin/microk8s.kubectl rollout status deployment/<deployment> -n <namespace>
```

## 待办事项

- [ ] Reddit 登录解决方案（已延迟决定）
- [ ] 考虑是否需要将 JSON 数据迁移到 SQLite（长期）
