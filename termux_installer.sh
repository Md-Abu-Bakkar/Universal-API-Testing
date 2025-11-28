#!/bin/bash
# Special Termux Installer for Universal API Tester

echo "🔧 Universal API Tester - Termux Installation"
echo "=============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running in Termux
if [ ! -d "/data/data/com.termux" ]; then
    print_error "This script is for Termux only!"
    exit 1
fi

# Update and upgrade
print_status "Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install essential packages
print_status "Installing essential packages..."
pkg install -y python git wget curl

# Install X11 packages
print_status "Installing X11 packages..."
pkg install -y x11-repo tur-repo
pkg install -y termux-x11-nightly termux-api

# Install desktop environment (optional)
print_status "Installing desktop environment..."
pkg install -y xfce4 xfce4-terminal thunar

# Install browsers
print_status "Installing web browsers..."
pkg install -y firefox chromium

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install requests beautifulsoup4 pyperclip colorama rich prompt-toolkit
pip install lxml aiohttp fake-useragent urllib3

# Optional: GUI dependencies
print_status "Installing GUI dependencies..."
pip install pyqt5 tkinter

# Setup permissions
print_status "Setting up permissions..."
termux-setup-storage

# Create startup script
print_status "Creating startup scripts..."
cat > ~/start-api-tester.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Universal API Tester..."
cd ~/Universal-API-Testing
python termux_desktop_launcher.py "$@"
EOF

chmod +x ~/start-api-tester.sh

# Create desktop shortcut
cat > ~/.shortcuts/Universal-API-Tester << 'EOF'
#!/bin/bash
termux-wake-lock
cd ~/Universal-API-Testing
python termux_desktop_launcher.py --gui
termux-wake-unlock
EOF

chmod +x ~/.shortcuts/Universal-API-Tester

print_success "Installation completed!"
echo ""
echo "📖 Usage Instructions:"
echo "  GUI Mode:    ./start-api-tester.sh --gui"
echo "  CLI Mode:    ./start-api-tester.sh --cli"
echo "  Auto Mode:   ./start-api-tester.sh"
echo ""
echo "🎯 Quick Start:"
echo "  1. Open Termux-X11 app"
echo "  2. Run: ./start-api-tester.sh --gui"
echo ""
echo "💡 Tips:"
echo "  - Grant storage permission: termux-setup-storage"
echo "  - Keep Termux-X11 app running in background"
echo "  - Use termux-wake-lock to prevent sleep"
