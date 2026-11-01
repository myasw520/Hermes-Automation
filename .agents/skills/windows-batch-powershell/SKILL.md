---
name: windows-batch-powershell
description: Best practices and rules for authoring Windows batch (.bat) and PowerShell (.ps1) scripts to avoid character encoding (GBK vs UTF-8) corruption, escaping issues, and UAC elevation failures.
---

# Windows 自动化与脚本规范指南 (Windows Batch & PowerShell Best Practices)

当在 Windows 系统中编写、生成自动化脚本（特别是涉及管理员提权、桌面快捷执行、中文提示信息）时，必须严格遵守以下规范，杜绝 `'...' 不是内部或外部命令`、乱码报错及参数截断问题。

---

## 1. 根本原因剖析：为什么 Windows .bat 极易出现乱码与命令报错？

1. **代码页冲突**：
   * 中文版 Windows 的 `cmd.exe` 默认代码页是 **CP936 (GBK)**；
   * 现代编辑器（VS Code、Antigravity、Git）默认保存文件为 **UTF-8**；
   * 当 `cmd.exe` 以 GBK 方式逐字节解析 UTF-8 的中文字符时，中文字节中的某些二进制值恰好与 ASCII 的操作符（如 `%`, `&`, `|`, `<`, `>`, `"`）重合，导致：
     - 变量被意外截断（如 `%SystemRoot%` 变成 `'TS_FILE'`）；
     - 命令被意外拆分执行（提示 `'xxx' 不是内部或外部命令`）；
     - 复杂的逻辑判断（`if %errorlevel% neq 0`）崩溃。

2. **`@chcp 65001` 的局限性**：
   * 仅在当前 cmd 会话中生效，无法解决批处理解释器在读取包含中文字符的 `for` 循环或代码块时的词法分析错误。

---

## 2. 核心架构原则：黄金法则

> **永远遵循：PowerShell 负责业务逻辑，.bat 仅充当 100% 纯 ASCII 的极简转发入口！**

### 规则一：.bat 入口必须是纯 ASCII 字符（严禁包含任何中文或特殊字符）
如果需要给用户提供双击运行的桌面 `.bat` 文件，该文件内**不得出现任何中文字符**，只负责以 Bypass 策略调用 PowerShell 脚本。

**标准 .bat 模板（无中文、无复杂语法、纯 ASCII）：**
```bat
@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0script.ps1"
```

如果该脚本需要**管理员权限 (UAC)**，直接用一行纯 ASCII 调用提权：
```bat
@echo off
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0script_admin.ps1\"'"
```

---

### 规则二：所有复杂逻辑、文本处理、系统配置一律编写为 `.ps1`
* PowerShell 原生支持 UTF-8 编码，对象化管道，拥有强大的正则替换、文件读写、异常处理（`try/catch`）能力；
* 所有的文本提示（中文字符串）统一写在 `.ps1` 文件内，保存为 UTF-8；
* 修改系统敏感路径（如 `C:\Windows\System32\drivers\etc\hosts`）时，使用 `[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)`，保证编码无损。

---

### 规则三：命令行调用 PowerShell 时的引号转义
在执行单行 PowerShell 命令时，避免在外层双引号内嵌套双引号：
* 推荐使用单引号包裹字符串参数：`-Command "Get-Content -Path 'C:\path\file.txt'"`
* 若必须嵌套双引号，使用反斜杠或重音符转义：`\"` 或 ``"`
