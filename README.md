# Antigravity 2.0 Fedora Installer

Install Antigravity 2.0 or Antigravity IDE on Fedora, with a script or as an RPM package.

## Install with the script

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/jrobertogarcia/antigravity-2-fedora-installer/main/install.sh)
```

Or, from a clone of this repository, run `./install.sh`. Options go at the end of either command.

The script asks which app to install; `--mode app` or `--mode ide` skips the question.

- `--mode app|ide`: install Antigravity 2.0 or Antigravity IDE.
- `--user`: install for the current user only, without sudo.
- `--dry-run`: run the checks and download the package without installing.
- `-y`, `--yes`: answer yes to prompts.
- `--url <url>`: override the default download URL.

`./install.sh --help` lists all options.

By default the script needs sudo and installs to `/opt/<name>-Linux`, where `<name>` is `antigravity` or `antigravity-ide`. With `--user` it installs to `~/.local/share/<name>-Linux` with the command in `~/.local/bin`, and tells you how to add that to your PATH if needed.

Run `antigravity` (app) or `antigravity-ide` (IDE).

## Install as an RPM

From a clone of this repository:

```bash
sudo dnf install -y spectool rpkg tar gzip
./build.sh       # Antigravity 2.0
./build-ide.sh   # Antigravity IDE
sudo dnf install ~/rpkg/$(uname -m)/antigravity2-2.32.1-*.rpm
sudo dnf install ~/rpkg/$(uname -m)/antigravity2-ide-2.7.0-*.rpm
```

Build and install only the one you want. Packages land in `~/rpkg/`; set `OUTDIR` to change that, and use that path in the `dnf install` lines.

Run `antigravity2` or `antigravity2-ide`.

## Antigravity 1.x

If Antigravity 1.x is installed, `install.sh` keeps its launcher as `<name>-legacy.desktop` so both versions stay available.

## Uninstall

From a clone of this repository, `uninstall.sh` asks what to remove; pass `--app`, `--ide` or `--both` to skip the question, and `--user` for a user install.

```bash
./uninstall.sh
```

For an RPM install:

```bash
sudo dnf remove antigravity2 antigravity2-ide
```

## License

This project is under the [MIT License](LICENSE). The upstream Antigravity binaries it installs are proprietary and subject to Google Terms of Service.
