# Universal API Tester & Auto Scanner

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-termux%20%7C%20linux%20%7C%20windows-brightgreen)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

**Automated API Detection, Testing, and Bot Code Generation Tool**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Demo](#demo) • [Contributing](#contributing)

</div>

## 🚀 Overview

Universal API Tester is a professional tool that automatically detects, tests, and generates bot-ready code from any web-based SMS/API panel. It features dual-mode operation (CLI + Desktop GUI) with full browser integration for comprehensive API analysis.

## ✨ Features

### 🔍 Smart API Detection
- **DevTools Integration**: Parse raw requests from browser DevTools
- **Auto URL Extraction**: Intelligent API endpoint detection
- **Parameter Analysis**: Extract headers, cookies, and parameters automatically

### 🔐 Dual Login System
- **Login Mode**: Full session handling with captcha solving
- **Direct API Mode**: Authentication-free API testing
- **Auto-detection**: Smart mode selection based on credentials

### 🧪 Multi-API Testing
- **Sequential Testing**: Test multiple APIs automatically
- **Response Analysis**: JSON/HTML response parsing
- **Working API Identification**: Highlight functional endpoints

### 💻 Multi-Platform Support
- **CLI Mode**: Lightweight command-line interface
- **Desktop GUI**: Professional dashboard via Termux-X11
- **Browser Integration**: Full desktop browsers in Termux

### 🔧 Code Generation
- **Python Templates**: Requests & aiohttp versions
- **cURL Commands**: Ready-to-use curl snippets
- **Bot-Ready Code**: Production-ready bot templates

## 📦 Installation

### Quick Install (All Platforms)
```bash
# Download and run installer
curl -s https://raw.githubusercontent.com/Md-Abu-Bakkar/Universal-API-Testing/main/installer.sh | bash




pip install flask
python web_interface.py
# তারপর ব্রাউজারে যান: http://localhost:5000
