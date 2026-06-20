# Antigravity 2.0 Fedora Installer

Native installation and packaging utility for running **Antigravity 2.0 Agent** and **Antigravity 2.0 IDE** on Fedora Workstation.

This project supports installation via direct scripts (`install.sh`) or native Fedora RPM packages built locally.

---

## 🛠️ Method A: Direct Script Installation

The easiest way to install Antigravity is by running the installer directly or using the local shell script.

### Usage

**One-liner (No clone required):**
Run the installer directly from the repository (supports interactive prompts and options):
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/jssroberto/antigravity-2-fedora-installer/main/install.sh) [options]
```

**Local script:**
Clone the repository and run the script:
```bash
./install.sh [options]
```

Unless `--mode` is specified, the installer runs interactively and prompts you to select the target variant:
1. **Antigravity 2.0 IDE** (Development Environment)
2. **Antigravity 2.0 Agent** (Background Agent / Hub)

### Command-Line Arguments
| Option | Argument | Description |
| :--- | :--- | :--- |
| `--mode` | `ide` \| `agent` | Choose the target variant to install (bypasses interactive menu). |
| `--user` | *None* | Install to user space (`~/.local`) without requiring root/sudo. |
| `--url` | `<url>` | Override the default download URL. |
| `--dry-run` | *None* | Perform validation checks and download the package without writing files. |
| `-y, --yes` | *None* | Automatically accept prompts during updates or reinstallations. |
| `-h, --help` | *None* | Display usage guide and exit. |

### Installation Paths & Scope
Depending on the install scope (system-wide vs. user-local) and the selected mode:

*   **System-Wide (Default, requires `sudo`)**:
    *   **Installation Directory**: `/opt/antigravity-Linux` or `/opt/antigravity-ide-Linux`
    *   **Binary Symlink**: `/usr/local/bin/antigravity` or `/usr/local/bin/antigravity-ide`
    *   **Launcher Path**: `/usr/share/applications/antigravity.desktop` or `/usr/share/applications/antigravity-ide.desktop`
*   **User-Local (`--user`, passwordless)**:
    *   **Installation Directory**: `~/.local/share/antigravity-Linux` or `~/.local/share/antigravity-ide-Linux`
    *   **Binary Symlink**: `~/.local/bin/antigravity` or `~/.local/bin/antigravity-ide`
    *   **Launcher Path**: `~/.local/share/applications/antigravity.desktop` or `~/.local/share/applications/antigravity-ide.desktop`

*Note: If `~/.local/bin` is not in your `$PATH` during a user-local installation, the installer will display shell configuration commands to help you add it.*

---

## 📦 Method B: RPM Package Distribution

You can build and install native RPM packages for Fedora using the provided spec files.

### 1. Install Build Prerequisites
Install the required packaging tools and dependencies (no compilers are required since the RPMs repackage precompiled upstream binaries):
```bash
sudo dnf install -y spectool rpkg tar gzip
```

### 2. Build the RPMs
Run the corresponding build script to download the upstream archives and package them locally:
*   **Build Agent RPM (`antigravity2`)**:
    ```bash
    ./build.sh
    ```
*   **Build IDE RPM (`antigravity2-ide`)**:
    ```bash
    ./build-ide.sh
    ```
The output RPM files will be generated in `~/rpkg/` (or the folder defined by `$OUTDIR`).

### 3. Install the RPMs
Install the compiled RPMs via `dnf`:
```bash
# Install the Antigravity Agent
sudo dnf install ~/rpkg/$(uname -m)/antigravity2-2.1.4-*.rpm

# Install the Antigravity IDE
sudo dnf install ~/rpkg/$(uname -m)/antigravity2-ide-2.0.4-*.rpm
```

---

## 🚀 Execution & Command-Line Interfaces

The CLI command name depends on your chosen installation method:

| Application | Installed via Script (`install.sh`) | Installed via RPM |
| :--- | :--- | :--- |
| **Antigravity 2.0 Agent** | `antigravity` | `antigravity2` |
| **Antigravity 2.0 IDE** | `antigravity-ide` | `antigravity2-ide` |

### Wayland & Performance Optimizations
The generated desktop entries run Chromium/Electron using native Wayland flags for accelerated hardware rendering:
`--ozone-platform-hint=wayland --enable-features=WaylandWindowDecorations,CanvasOopRasterization --enable-gpu-rasterization --enable-zero-copy`

---

## 🧹 Coexistence & Uninstallation

### Dual-Version Coexistence
If legacy Antigravity 1.x is present on the system, the installer handles compatibility by renaming legacy launcher files to `*-legacy.desktop` (e.g. `antigravity-legacy.desktop`), allowing v1.x and v2.0 to run side-by-side.

### Uninstallation

#### Script-Based Uninstallation
Use the [uninstall.sh](uninstall.sh) utility to cleanly remove all files, directories, desktop launchers, and databases.
```bash
./uninstall.sh [options]
```
*   **CLI Options**: `--ide` (IDE only), `--agent` (Agent only), `--both` (complete cleanup), or `--user` (limit scope to user space).
*   **Interactive Menu**: Run `./uninstall.sh` without options to choose via terminal prompt.

#### RPM-Based Uninstallation
If you installed via RPM, remove the packages directly via `dnf`:
```bash
sudo dnf remove antigravity2 antigravity2-ide
```

---

## 📄 License
This installer project is open-source and available under the [MIT License](LICENSE).
The upstream Antigravity binaries packaged by this utility are proprietary and subject to Google Terms of Service.
