# BestBlogs RSS 源故障排查指南

## 问题现象

每日技术摘要无法从 BestBlogs 获取文章，显示超时或失败。

---

## 手动检查步骤

### 步骤 1：检查网络连接

```bash
# 测试基本连接
ping -c 3 www.bestblogs.dev

# 预期结果：
# ✓ 3 packets transmitted, 3 received
# ✓ 平均延迟 < 100ms
```

**如果失败：**
- 检查网络连接
- 检查防火墙设置
- 尝试访问其他网站

---

### 步骤 2：检查 DNS 解析

```bash
# 检查 DNS 解析
nslookup www.bestblogs.dev

# 预期结果：
# ✓ Name: www.bestblogs.dev
# ✓ Address: xxx.xxx.xxx.xxx
```

**如果失败：**
- 检查 DNS 配置：`/etc/resolv.conf`
- 尝试更换 DNS 服务器（如 8.8.8.8, 1.1.1.1）
- 重启 DNS 服务

---

### 步骤 3：检查 HTTPS 连接

```bash
# 测试 HTTPS 连接
curl -I --connect-timeout 10 https://www.bestblogs.dev

# 预期结果：
# ✓ HTTP/2 200
# ✓ server: nginx
```

**如果失败：**
- 检查系统时间是否正确
- 检查证书是否有效
- 检查代理设置

---

### 步骤 4：检查 RSS 源（最关键）

```bash
# 测试 RSS 源（带重定向）
curl -L --connect-timeout 10 "https://www.bestblogs.dev/zh/feeds/rss?featured=y"

# 预期结果：
# ✓ <?xml version="1.0" encoding="UTF-8" ?>
# ✓ <rss version="2.0">
# ✓ <channel>
# ✓   <title>BestBlogs.dev - 精选文章</title>
# ✓   <item>
# ✓     <title>文章标题...</title>
# ✓     <link>https://www.bestblogs.dev/article/xxx</link>
```

**如果失败：**
- 检查是否返回 307 重定向
- 使用 `-L` 参数跟随重定向
- 检查连接时间（可能需要 5-7 秒）

**成功标志：**
- 返回 XML 格式数据
- 包含 <rss> 和 <item> 标签
- 包含文章标题和链接

---

### 步骤 5：测试 Python 脚本

```bash
# 进入脚本目录
cd /home/lichangjiang/.openclaw/workspace

# 运行脚本（带超时）
timeout 30 python3 daily_tech_digest_final.py

# 预期结果：
# ✓ 🚀 每日技术摘要（BestBlogs 源）
# ✓ 📡 正在获取 BestBlogs RSS 源...
# ✓   → BestBlogs 精选
# ✓      ✅ 获取 N 篇文章
# ✓ ✅ 共获取 N 篇文章
# ✓ 📝 摘要生成完成
```

**如果超时：**
- 检查 Python 环境：`python3 --version`
- 检查依赖：`pip3 list | grep feedparser`
- 尝试安装依赖：`pip3 install feedparser --break-system-packages`

---

## 常见问题和解决方案

### 问题 1：连接超时

**症状：**
```
curl: (28) Operation timed out after 10000 milliseconds
```

**解决方案：**
1. 增加超时时间：`curl -L --connect-timeout 30`
2. 检查防火墙规则
3. 检查代理设置

---

### 问题 2：DNS 解析失败

**症状：**
```
nslookup: can't find 'www.bestblogs.dev': NXDOMAIN
```

**解决方案：**
1. 修改 DNS 配置：
```bash
sudo nano /etc/resolv.conf

# 添加：
nameserver 8.8.8.8
nameserver 1.1.1.1
```

2. 重启网络服务
```bash
sudo systemctl restart systemd-resolved
```

---

### 问题 3：SSL 证书错误

**症状：**
```
curl: (60) SSL certificate problem: unable to get local issuer certificate
```

**解决方案：**
1. 更新 CA 证书：
```bash
sudo apt-get update
sudo apt-get install ca-certificates
```

2. 更新系统时间：
```bash
sudo timedatectl set-ntp true
```

---

### 问题 4：Python 依赖缺失

**症状：**
```
ModuleNotFoundError: No module named 'feedparser'
```

**解决方案：**
```bash
pip3 install feedparser --break-system-packages
```

---

### 问题 5：网络速度慢

**症状：**
- RSS 获取时间 > 30 秒
- curl 响应很慢

**解决方案：**
1. 检查网络带宽
2. 测试其他网站速度
3. 考虑使用 CDN 或代理

---

## 诊断命令总结

```bash
# 一键诊断
echo "=== 网络连接 ==="
ping -c 3 www.bestblogs.dev

echo -e "\n=== DNS 解析 ==="
nslookup www.bestblogs.dev

echo -e "\n=== HTTPS 连接 ==="
curl -I --connect-timeout 10 https://www.bestblogs.dev

echo -e "\n=== RSS 源 ==="
curl -L --connect-timeout 10 "https://www.bestblogs.dev/zh/feeds/rss?featured=y" | head -20

echo -e "\n=== Python 版本 ==="
python3 --version

echo -e "\n=== 依赖检查 ==="
pip3 list | grep feedparser

echo -e "\n=== 脚本测试 ==="
cd /home/lichangjiang/.openclaw/workspace
timeout 30 python3 daily_tech_digest_final.py 2>&1 | head -50
```

---

## 备用方案

如果 BestBlogs 持续无法访问，可以使用：

1. **Hacker News**：`https://hnrss.org/frontpage`
2. **GitHub Trending**：`https://github.com/trending/developers.atom`
3. **Reddit**：`https://www.reddit.com/r/programming/.rss`

---

## 联系支持

如果以上步骤都无法解决问题，请提供以下信息：

1. 网络连接测试结果
2. DNS 解析测试结果
3. RSS 源测试结果
4. Python 脚本错误日志
5. 系统信息：
```bash
uname -a
python3 --version
pip3 list | grep feedparser
```

---

**最后更新：** 2026-02-16
**测试状态：** ✅ 脚本可正常运行
