# Save this script as build_kivy_app.ps1

# Automatically detected variables
$username = [System.Environment]::UserName
$pythonVersion = (python --version 2>&1 | ForEach-Object { $_.Split(" ")[1].Substring(0, 3).Replace(".", "") })

# User-configurable variables
$androidHome = "C:\Users\$username\AppData\Local\Android\sdk"
$androidNdkHome = "C:\Users\$username\AppData\Local\Android\ndk"
$javaHome = "D:\apps-dev\Android\Android Studio\jbr" # Path to the embedded JDK in Android Studio

# Ensure PowerShell is running as Administrator
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))
{
    Write-Host "This script must be run as an administrator. Please run PowerShell as an administrator and try again."
    exit
}

# Function to add Python Scripts directory to PATH
function Add-PythonScriptsToPath {
    param (
        [string]$username,
        [string]$pythonVersion
    )

    $scriptsPath = "C:\Users\ignis\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts"
    $currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')

    if ($currentPath -notlike "*$scriptsPath*") {
        [System.Environment]::SetEnvironmentVariable('Path', "$currentPath;$scriptsPath", 'User')
        Write-Host "Added $scriptsPath to PATH."
    } else {
        Write-Host "$scriptsPath is already in PATH."
    }
}

# Add Python Scripts directory to PATH
Add-PythonScriptsToPath -username $username -pythonVersion $pythonVersion

# Restart PowerShell to apply changes
Write-Host "Please restart PowerShell to apply PATH changes if you have not done so already."

# Check if Buildozer is installed
$buildozerInstalled = pip show buildozer

if (-not $buildozerInstalled) {
    # Install Buildozer if not installed
    Write-Host "Installing Buildozer..."
    pip install buildozer
} else {
    Write-Host "Buildozer is already installed."
}

# Check if Cython is installed
$cythonInstalled = pip show cython

if (-not $cythonInstalled) {
    # Install Cython if not installed
    Write-Host "Installing Cython..."
    pip install cython
} else {
    Write-Host "Cython is already installed."
}

# Check if Git is installed
try {
    git --version
} catch {
    # Install Git if not installed
    Write-Host "Git is not installed. Please install Git from https://git-scm.com/download/win."
    exit
}

# Ensure Java JDK is installed and set JAVA_HOME
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', $javaHome, 'User')
Write-Host "JAVA_HOME is set to $javaHome"

# Set Android SDK and NDK paths
[System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $androidHome, 'User')
[System.Environment]::SetEnvironmentVariable('ANDROID_NDK_HOME', $androidNdkHome, 'User')

Write-Host "ANDROID_HOME is set to $androidHome"
Write-Host "ANDROID_NDK_HOME is set to $androidNdkHome"

# Navigate to the current project directory
$projectPath = Get-Location
Write-Host "Current project directory: $projectPath"

# Initialize Buildozer if not already done
if (-not (Test-Path -Path "buildozer.spec")) {
    Write-Host "Initializing Buildozer..."
    buildozer init
} else {
    Write-Host "Buildozer is already initialized."
}

# Build the APK
Write-Host "Building the APK..."
buildozer -v android debug

Write-Host "Build process complete."
