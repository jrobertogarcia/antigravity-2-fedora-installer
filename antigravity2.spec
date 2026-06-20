# Disable debug packages as we're packaging precompiled binaries
%global debug_package %{nil}
%undefine __brp_check_rpaths

# Exclude private shared libraries from being registered as provides or requirements
%global __provides_exclude_from ^/opt/antigravity2-Linux/.*\\.so.*$
%global __requires_exclude_from ^/opt/antigravity2-Linux/.*\\.so.*$
%global __requires_exclude ^(libffmpeg\\.so|/usr/bin/node)


Name:           antigravity2
Version:        2.1.4
Release:        1%{?dist}
Summary:        Antigravity 2.0 Agent

License:        Proprietary (Google Terms of Service)
URL:            https://storage.googleapis.com/antigravity-public/antigravity-hub/index.html
ExclusiveArch:  x86_64 aarch64

Source0:        https://storage.googleapis.com/antigravity-public/antigravity-hub/2.1.4-6481382726303744/linux-x64/Antigravity.tar.gz
Source1:        https://storage.googleapis.com/antigravity-public/antigravity-hub/2.1.4-6481382726303744/linux-arm/Antigravity.tar.gz
Source2:        antigravity2.desktop
Source3:        antigravity.png

BuildRequires:  tar
BuildRequires:  gzip

%description
Antigravity 2.0 Agent (Background Agent / Hub) repackaged for Fedora.
Experience liftoff (v2.0 Agent).

%prep
%setup -c -T
%ifarch x86_64
tar -xzf %{SOURCE0}
mv Antigravity-x64 %{name}-Linux
%endif
%ifarch aarch64
tar -xzf %{SOURCE1}
mv Antigravity-arm64 %{name}-Linux
%endif

# Rename the internal executable to prevent conflict with v1.0
mv %{name}-Linux/antigravity %{name}-Linux/%{name}

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
* Sun Jun 21 2026 Roberto Garcia <jrobertogarcia16@gmail.com> - 2.1.4-1
- Update to version 2.1.4 with new GCS download URLs

* Thu Jun 04 2026 Roberto Garcia <jrobertogarcia16@gmail.com> - 2.0.11-1
- Update to version 2.0.11 with new GCS download URLs

* Thu May 28 2026 Roberto Garcia <jrobertogarcia16@gmail.com> - 2.0.10-1
- Various reliability and usability improvements
- Fix G1 credit bug

* Fri May 22 2026 Roberto Garcia <jrobertogarcia16@gmail.com> - 2.0.6-1
- Add an install IDE button if Antigravity IDE is not installed
- Add an open IDE button if Antigravity IDE is installed

* Tue May 19 2026 Roberto Garcia <jrobertogarcia16@gmail.com> - 2.0.1-1
- Fix project migration issues for projects with CJK characters in their titles
- Fix issue causing duplicate projects when importing from Antigravity 1.0
- Resolve issue where Google One credits were not being applied or utilized
