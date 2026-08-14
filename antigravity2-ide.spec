# Disable debug packages as we're packaging precompiled binaries
%global debug_package %{nil}
%undefine __brp_check_rpaths

# Exclude private shared libraries from being registered as provides or requirements
%global __provides_exclude_from ^/opt/antigravity2-ide-Linux/.*\\.so.*$
%global __requires_exclude_from ^/opt/antigravity2-ide-Linux/.*\\.so.*$
%global __requires_exclude ^(libffmpeg\\.so|libmsalruntime\\.so|/usr/bin/node|/usr/bin/perl|/usr/bin/python3)


Name:           antigravity2-ide
Version:        2.5.5
Release:        1%{?dist}
Summary:        Antigravity 2.0 IDE

License:        Proprietary (Google Terms of Service)
URL:            https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/index.html
ExclusiveArch:  x86_64 aarch64

Source0:        https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.5.5-4923483625488384/linux-x64/Antigravity%20IDE.tar.gz#/Antigravity-IDE-x64.tar.gz
Source1:        https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.5.5-4923483625488384/linux-arm/Antigravity%20IDE.tar.gz#/Antigravity-IDE-arm64.tar.gz
Source2:        antigravity2-ide.desktop
Source3:        antigravity.png

BuildRequires:  tar
BuildRequires:  gzip

%description
Antigravity 2.0 IDE repackaged for Fedora.
Experience liftoff (v2.0 Standalone IDE).

%prep
%setup -c -T
%ifarch x86_64
tar -xzf %{SOURCE0}
%endif
%ifarch aarch64
tar -xzf %{SOURCE1}
%endif
mv "Antigravity IDE" %{name}-Linux

# Rename the internal executable to prevent conflict with v1.0
mv %{name}-Linux/antigravity-ide %{name}-Linux/%{name}

%build
# No build steps needed for repackaged binaries

%install
mkdir -p %{buildroot}/opt
mv %{name}-Linux %{buildroot}/opt/%{name}-Linux

# Write version file
echo "%{version}" > %{buildroot}/opt/%{name}-Linux/version.txt

# Ensure executable permission
chmod +x %{buildroot}/opt/%{name}-Linux/%{name}

# Create symlink in /usr/bin
mkdir -p %{buildroot}%{_bindir}
ln -s /opt/%{name}-Linux/%{name} %{buildroot}%{_bindir}/%{name}

# Install desktop file
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 %{SOURCE2} %{buildroot}%{_datadir}/applications/%{name}.desktop

# Install icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
install -m 644 %{SOURCE3} %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/%{name}.png

%post
/usr/bin/update-desktop-database &> /dev/null || :
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &> /dev/null || :

%postun
/usr/bin/update-desktop-database &> /dev/null || :
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &> /dev/null || :

%files
/opt/%{name}-Linux/
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/512x512/apps/%{name}.png

%changelog
* Fri Aug 14 2026 pjv <ezelspinguin@gmail.com> - 2.5.5-1
- Update to version 2.5.5 with new download URLs

* Thu Jun 25 2026 Roberto Garcia <jrobertogarcia16@gmail.com> - 2.1.1-1
- Update to version 2.1.1 with new download URLs and native ARM64 support

* Thu Jun 04 2026 Roberto Garcia <jrobertogarcia16@gmail.com> - 2.0.4-1
- Update to version 2.0.4 with new download URLs and native ARM64 support

* Thu May 28 2026 ApicalShark - 2.0.3-2
- Fix StartupWMClass to match applicationName (antigravity-ide) so taskbar icon appears correctly

* Thu May 28 2026 ApicalShark - 2.0.3-1
- Initial RPM release of Antigravity 2.0 IDE renamed to antigravity2-ide
