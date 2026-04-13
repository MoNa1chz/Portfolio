# .bashrc - Mockup Infrastructure Shell Configuration
# Works with: Git Bash, WSL, MSYS2, Cygwin on Windows

# ============================================================================
# ENVIRONMENT DETECTION
# ============================================================================

# Detect OS and shell
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    SHELL_ENV="WINDOWS_BASH"
    PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    SHELL_ENV="LINUX"
    PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
elif [[ "$OSTYPE" == "darwin"* ]]; then
    SHELL_ENV="MACOS"
    PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
else
    SHELL_ENV="UNKNOWN"
    PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null || pwd)
fi

# ============================================================================
# ALIASES FOR MOCKUP-INFRA MANAGEMENT
# ============================================================================

# Management commands
alias minit='python manage.py init'
alias mdeploy='python manage.py deploy'
alias mstop='python manage.py stop'
alias mrestart='python manage.py restart'
alias mstatus='python manage.py status'
alias mlogs='python manage.py logs'
alias mtest='python manage.py test'
alias mcerts='python manage.py certs'
alias mtls='python manage.py tls'
alias misolate='python manage.py isolate'

# Test scripts
alias test-standalone='python test_infra.py'
alias test-all='python manage.py test && python test_infra.py'

# Quick access
alias infra-cd='cd "$PROJECT_ROOT"'
alias infra-status='infra-cd && python manage.py status'
alias infra-logs='infra-cd && python manage.py logs'

# ============================================================================
# FUNCTIONS FOR MOCKUP-INFRA
# ============================================================================

# Initialize and deploy infrastructure
infra-setup() {
    echo "🚀 Setting up Mockup Infrastructure..."
    cd "$PROJECT_ROOT" || return 1
    python manage.py init && python manage.py deploy
    echo "✅ Setup complete!"
}

# Full test suite
infra-test() {
    echo "🧪 Running comprehensive infrastructure tests..."
    cd "$PROJECT_ROOT" || return 1
    echo ""
    echo "=== Running manage.py test ==="
    python manage.py test
    echo ""
    echo "=== Running test_infra.py ==="
    python test_infra.py
    echo "✅ All tests complete!"
}

# Check infrastructure status
infra-check() {
    echo "📊 Checking Infrastructure Health..."
    cd "$PROJECT_ROOT" || return 1
    python manage.py status
    echo ""
    python manage.py isolate
}

# View all logs
infra-logs-all() {
    echo "📋 Showing all service logs..."
    cd "$PROJECT_ROOT" || return 1
    python manage.py logs
}

# View specific service logs
infra-logs-service() {
    if [ -z "$1" ]; then
        echo "Usage: infra-logs-service <service-name>"
        echo "Services: nginx-gateway, public_app, intranet_api"
        return 1
    fi
    cd "$PROJECT_ROOT" || return 1
    python manage.py logs "$1"
}

# Quick deploy
infra-quick-deploy() {
    echo "⚡ Quick deploy (existing certs)..."
    cd "$PROJECT_ROOT" || return 1
    python manage.py deploy
    echo "✅ Deploy complete!"
}

# Restart services
infra-restart-all() {
    echo "🔄 Restarting all services..."
    cd "$PROJECT_ROOT" || return 1
    python manage.py restart
    echo "✅ Services restarted!"
}

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

# Set Python environment
export PYTHONIOENCODING=utf-8
export PYTHONDONTWRITEBYTECODE=1

# Infrastructure paths
export INFRA_ROOT="$PROJECT_ROOT"
export INFRA_CERTS="$PROJECT_ROOT/certs"
export INFRA_GATEWAY="$PROJECT_ROOT/gateway"
export INFRA_SERVICES="$PROJECT_ROOT/services"

# ============================================================================
# HELPFUL INFORMATION
# ============================================================================

# Display welcome message
if [ -n "$BASH" ]; then
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║        Mockup Infrastructure - Bash Configuration         ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Environment: $SHELL_ENV"
    echo "Project Root: $PROJECT_ROOT"
    echo ""
    echo "Quick Commands:"
    echo "  infra-cd              - Navigate to project root"
    echo "  infra-setup           - Initialize and deploy infrastructure"
    echo "  infra-status          - Check service status"
    echo "  infra-test            - Run all tests"
    echo "  infra-check           - Full health check"
    echo "  infra-logs-all        - View all logs"
    echo "  infra-restart-all     - Restart services"
    echo ""
    echo "Aliases (shorter versions):"
    echo "  minit, mdeploy, mstop, mrestart, mstatus, mlogs, mtest"
    echo "  mcerts, mtls, misolate"
    echo ""
    echo "Test Commands:"
    echo "  mtest                 - Run manage.py tests"
    echo "  test-standalone       - Run test_infra.py"
    echo "  test-all              - Run both test suites"
    echo ""
fi

# ============================================================================
# SHELL-SPECIFIC CONFIGURATIONS
# ============================================================================

# Git Bash specific
if [[ "$OSTYPE" == "msys" ]]; then
    # Enable colors in Git Bash
    export CLICOLOR=1
    export LSCOLORS=ExFxCxDxBxegedabagacad
fi

# WSL specific
if [[ -n "$WSL_INTEROP" ]]; then
    # WSL-specific configurations can go here
    export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0
fi

# ============================================================================
# COMPLETION AND HISTORY
# ============================================================================

# Enhanced history
export HISTSIZE=10000
export HISTFILESIZE=10000
export HISTCONTROL=ignoredups:ignorespace

# ============================================================================
# END OF .bashrc
# ============================================================================
