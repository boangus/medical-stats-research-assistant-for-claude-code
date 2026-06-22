# Security Policy

## 报告安全漏洞

如果你发现本项目的安全漏洞，请**不要**在公开 Issue 中报告。

请通过以下方式联系：
- 发送邮件至项目维护者（见 README.md 底部）
- 在 GitHub 上使用 "Report a vulnerability" 功能

## 安全承诺

- 我们会在 7 个工作日内确认收到报告
- 我们会在确认后 30 天内发布修复
- 修复后会在 CHANGELOG.md 中记录（不包含漏洞细节）

## 数据安全

- 本项目不收集任何用户数据
- 所有分析在本地完成，不依赖外部 API
- 用户数据不会被上传到任何服务器
- 详见 README.md 的 "Privacy & Data Security" 章节

## 依赖安全

- Python 依赖均为开源科学计算库
- 建议使用 `pip-audit` 定期检查依赖漏洞
- R 包通过 CRAN 安装，来源可信
