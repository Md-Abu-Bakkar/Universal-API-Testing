#!/bin/bash

# Universal API Tester - Installation Script
set -e

echo "🔧 Universal API Tester Installation"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.8+ is required but not installed"
        print_status "Please install Python from https://python.org"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    if command -v pip3 &>/dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 is required but not installed"
        print_status "Installing pip..."
        if python3 -m ensurepip --upgrade; then
            print_success "pip installed successfully"
        else
            print_error "Failed to install pip"
            exit 1
        fi
    fi
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip first
    python3 -m pip install --upgrade pip
    
    if pip3 install -r requirements.txt; then
        print_success "Python dependencies installed successfully"
    else
        print_error "Failed to install Python dependencies"
        print_status "Trying alternative installation method..."
        
        # Try installing packages one by one
        for package in requests beautifulsoup4 pyperclip colorama rich prompt-toolkit lxml aiohttp fake-useragent urllib3 qrcode pycryptodome; do
            print_status "Installing $package..."
            if pip3 install "$package"; then
                print_success "Installed $package"
            else
                print_warning "Failed to install $package"
            fi
        done
    fi
}

# Setup termux-x11 (if in Termux)
setup_termux() {
    if [[ "$OSTYPE" == *"android"* ]] || [[ -d "/data/data/com.termux" ]]; then
        print_status "Detected Termux environment"
        
        # Update packages
        pkg update -y
        
        # Install required packages
        pkg install -y python python-pip git
        
        # Install X11 packages if not installed
        if ! pkg list-installed | grep -q "termux-x11"; then
            print_status "Installing Termux-X11..."
            pkg install -y x11-repo
            pkg install -y termux-x11
        fi
        
        # Install browsers
        print_status "Installing browsers..."
        pkg install -y firefox chromium
        
        print_success "Termux setup completed"
    fi
}

# Create configuration directory
create_config() {
    print_status "Creating configuration directory..."
    
    CONFIG_DIR="$HOME/.config/universal-api-tester"
    mkdir -p "$CONFIG_DIR"
    
    # Copy default config if it doesn't exist
    if [[ -f "config.json" ]] && [[ ! -f "$CONFIG_DIR/config.json" ]]; then
        cp "config.json" "$CONFIG_DIR/config.json"
        print_success "Default configuration created"
    else
        # Create basic config file
        cat > "$CONFIG_DIR/config.json" << EOF
{
  "app": {
    "name": "Universal API Tester",
    "version": "1.0.0"
  },
  "api_detection": {
    "timeout": 30,
    "retry_attempts": 3
  },
  "export": {
    "default_output_dir": "./exports"
  }
}
EOF
        print_success "Basic configuration created"
    fi
}

# Install the package
install_package() {
    print_status "Installing universal-api-tester package..."
    
    if pip3 install -e .; then
        print_success "Package installed successfully"
    else
        print_warning "Failed to install package in development mode"
        print_status "Continuing with basic installation..."
    fi
}

# Create desktop entry (for Linux)
create_desktop_entry() {
    if [[ "$OSTYPE" == "linux-gnu"* ]] && [[ -d "$HOME/.local/share/applications" ]]; then
        print_status "Creating desktop entry..."
        
        DESKTOP_FILE="$HOME/.local/share/applications/universal-api-tester.desktop"
        
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Universal API Tester
Comment=Automated API Detection and Testing Tool
Exec=python3 $PWD/main.py --gui
Icon=utilities-terminal
Categories=Development;Network;
Terminal=false
StartupWMClass=UniversalApiTester
EOF
        
        if [[ -f "$DESKTOP_FILE" ]]; then
            chmod +x "$DESKTOP_FILE"
            print_success "Desktop entry created"
        fi
    fi
}

# Create startup script
create_startup_script() {
    print_status "Creating startup script..."
    
    STARTUP_SCRIPT="api-tester"
    
    cat > "$STARTUP_SCRIPT" << 'EOF'
#!/bin/bash
# Universal API Tester Startup Script

cd "$(dirname "$0")"
python3 main.py "$@"
EOF
    
    chmod +x "$STARTUP_SCRIPT"
    print_success "Startup script created: ./api-tester"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    if python3 -c "from core.api_scanner import APIScanner; print('✅ Core modules imported successfully')"; then
        print_success "Core functionality test passed"
    else
        print_error "Core functionality test failed"
        return 1
    fi
    
    if python3 -c "import requests; print('✅ Dependencies imported successfully')"; then
        print_success "Dependencies test passed"
    else
        print_error "Dependencies test failed"
        return 1
    fi
    
    return 0
}

# Main installation function
main() {
    echo ""
    print_status "Starting Universal API Tester Installation..."
    echo ""
    
    # Check prerequisites
    check_python
    check_pip
    
    # Setup environment
    setup_termux
    
    # Install dependencies
    install_dependencies
    
    # Install package
    install_package
    
    # Create configuration
    create_config
    
    # Create startup script
    create_startup_script
    
    # Create desktop entry
    create_desktop_entry
    
    # Test installation
    if test_installation; then
        echo ""
        print_success "🎉 Installation completed successfully!"
        echo ""
        echo "📖 Quick Start:"
        echo "  CLI Mode:    python3 main.py --cli"
        echo "  GUI Mode:    python3 main.py --gui"
        echo "  Auto Mode:   python3 main.py"
        echo "  Script:      ./api-tester"
        echo ""
        echo "🔧 Configuration: ~/.config/universal-api-tester/config.json"
        echo "📚 Documentation: https://github.com/Md-Abu-Bakkar/Universal-API-Testing"
        echo ""
        echo "💡 Tip: Run './api-tester --help' to see all options"
    else
        echo ""
        print_warning "⚠️  Installation completed with warnings"
        print_status "Some features might not work properly"
        print_status "Please check the error messages above"
    fi
}

# Run main function
main "$@"
