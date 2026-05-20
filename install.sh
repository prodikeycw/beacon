#!/bin/bash
# notify — universal notification CLI
# One-line install: curl -fsSL https://raw.githubusercontent.com/prodikeycw/notify/main/install.sh | bash

set -e

REPO="https://github.com/prodikeycw/notify.git"
INSTALL_DIR="$HOME/notify"

echo "📬 notify installer"
echo ""

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "→ Updating existing installation at $INSTALL_DIR"
    cd "$INSTALL_DIR"
    git pull --quiet
else
    if [ -d "$INSTALL_DIR" ]; then
        echo "→ $INSTALL_DIR exists but isn't a git repo. Backing up to ${INSTALL_DIR}.bak"
        mv "$INSTALL_DIR" "${INSTALL_DIR}.bak"
    fi
    echo "→ Cloning $REPO to $INSTALL_DIR"
    git clone --quiet "$REPO" "$INSTALL_DIR"
fi

# Install Python dependencies
echo "→ Installing Python dependencies (requests)"
if command -v pip3 &> /dev/null; then
    pip3 install --quiet --break-system-packages requests 2>/dev/null || \
        pip3 install --quiet --user requests 2>/dev/null || \
        pip3 install --quiet requests
fi

# Set up .env from template if missing
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp "$INSTALL_DIR/.env.template" "$INSTALL_DIR/.env"
    echo "→ Created $INSTALL_DIR/.env from template"
    NEEDS_CONFIG=1
fi

# Make scripts executable
chmod +x "$INSTALL_DIR/notify.sh"

# Add alias to shell rc files
add_alias() {
    local rc="$1"
    [ -f "$rc" ] || return
    if ! grep -q "alias notify=" "$rc" 2>/dev/null; then
        echo "" >> "$rc"
        echo "# notify — universal notification CLI" >> "$rc"
        echo "alias notify=\"$INSTALL_DIR/notify.sh\"" >> "$rc"
        echo "→ Added 'notify' alias to $rc"
    fi
}

add_alias "$HOME/.zshrc"
add_alias "$HOME/.bashrc"

echo ""
echo "✅ Install complete!"
echo ""

if [ -n "$NEEDS_CONFIG" ]; then
    echo "⚠️  Next steps:"
    echo "   1. Edit credentials:  open -e $INSTALL_DIR/.env"
    echo "   2. Restart terminal (or run: source ~/.zshrc)"
    echo "   3. Test:              notify 'Hello' 'World'"
    echo ""
    echo "📖 Channel setup guides:"
    echo "   https://github.com/prodikeycw/notify#setup"
else
    echo "Test it:  notify 'Hello' 'World'"
fi
