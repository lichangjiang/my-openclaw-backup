# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### OneDrive Configuration

**Client:** onedrive-cli (Snap v2.5.9)
**Sync Directory:** ~/onedrive
**Config File:** ~/snap/onedrive-cli/40/.config/onedrive/config
**Authentication:** OAuth2 (completed)
**Sync Status:** Running in background

**Multi-Device Sharing:**
- Use `~/onedrive` directory for files you want to share across devices
- Other OneDrive clients will automatically sync changes

**AI-Generated Notes Directory:**
- **Path:** `~/onedrive/auto-notes/01-技术学习/AI-学习笔记`
- **Purpose:** 存放 OpenClaw (mirrorLee) 生成的学习笔记内容
- **Created:** 2026-02-17
- **Rule:** 所有 AI 助手生成的学习笔记、教程、技术文档都应存放于此目录

### OpenWrt Soft Router

**IP Address:** 192.168.1.201
**User:** root (password authentication working)
**Password:** 9kON!ZXq3RyxZ5
**SSH Status:** Password authentication works, SSH key authentication failed (outdated firmware)
**Config File:** /etc/dropbear/authorized_keys
**Issue:** Dropbear version is outdated and doesn't support modern RSA signature algorithms
**Workaround:** Use password authentication (working perfectly)

**SSH Commands (for OpenClaw):**
```bash
# Password authentication (working)
sshpass -p '9kON!ZXq3RyxZ5' ssh root@192.168.1.201 <command>

# Key authentication (not working due to firmware)
ssh -i ~/.ssh/id_rsa root@192.168.1.201 <command>
```

### Local Projects

**Main project directory:** `~/project` - All local code projects are stored here

Current projects:
- `claude-code-log` - Claude Code logging
- `feishu-scripts` - Feishu/Lark integration scripts
- `srs-word` - SRS Word project
- `tradingagents-demo` - Trading agents demo
- `TrendRadar` - Trend radar project

### Kubernetes

**Cluster:** microk8s v1.28.15 (snap)
- Address: https://10.0.0.23:16443
- Context: microk8s
- User: lichangjiang

**Kubectl commands (OpenClaw execution环境):**
```bash
sudo /snap/bin/microk8s.kubectl get pods --all-namespaces
sudo /snap/bin/microk8s.kubectl get deployments --all-namespaces
sudo /snap/bin/microk8s.kubectl describe deployment <name> -n <namespace>
sudo /snap/bin/microk8s.kubectl set image deployment/<deployment> <container>=<image> -n <namespace>
sudo /snap/bin/microk8s.kubectl rollout status deployment/<deployment> -n <namespace>
```

**SRS Service:**
- Namespace: srs
- Deployment: srs-web-deployment
- Image: lichangj/srs-word:v1.0.10
- API: http://10.0.0.23:30080
- Test endpoint: GET /api/knowledge_items

**Kuboard:**
- Namespace: kuboard
- URL: http://10.0.0.23:30080 (如果配置了 NodePort)

### System Configuration

**Sudo access:**
- No password required for sudo commands (confirmed: 2026-02-16)
- Can execute `sudo` commands without prompts
- Verified with: `sudo -n true`

**OS Environment:**
- Ubuntu 24.04.2 LTS (Noble)
- Kernel: 6.8.0-64-generic
- No GUI (headless Linux server)
