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
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    if command -v pip3 &>/dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 is required but not installed"
        exit 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if pip3 install -r requirements.txt; then
        print_success "Python dependencies installed successfully"
    else
        print_error "Failed to install Python dependencies"
        exit 1
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
    fi
}

# Install the package
install_package() {
    print_status "Installing universal-api-tester package..."
    
    if pip3 install -e .; then
        print_success "Package installed successfully"
    else
        print_error "Failed to install package"
        exit 1
    fi
}

# Create desktop entry (for Linux)
create_desktop_entry() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Creating desktop entry..."
        
        DESKTOP_FILE="$HOME/.local/share/applications/universal-api-tester.desktop"
        mkdir -p "$(dirname "$DESKTOP_FILE")"
        
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Universal API Tester
Comment=Automated API Detection and Testing Tool
Exec=api-tester --gui
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
    
    # Create desktop entry
    create_desktop_entry
    
    echo ""
    print_success "🎉 Installation completed successfully!"
    echo ""
    echo "📖 Quick Start:"
    echo "  CLI Mode:    python main.py --cli"
    echo "  GUI Mode:    python main.py --gui"
    echo "  Auto Mode:   python main.py"
    echo ""
    echo "🔧 Configuration: ~/.config/universal-api-tester/config.json"
    echo "📚 Documentation: https://github.com/Md-Abu-Bakkar/Universal-API-Testing"
    echo ""
}

# Run main function
main "$@"
