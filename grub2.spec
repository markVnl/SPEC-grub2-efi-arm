%undefine _hardened_build
%undefine _missing_build_ids_terminate_build
%global githash na

%ifarch aarch64
%global grubefiarch arm64-efi
%global grubefiname grubaa64.efi
%global grubeficdname gcdaa64.efi
%global grububootname BOOTAA64.EFI
%endif
%ifarch %{arm}
%global grubefiarch arm-efi
%global grubefiname grubarm.efi
%global grubeficdname gcdarm.efi
%global grububootname BOOTARM.EFI
%endif

# Figure out the right file path to use
%global efidir %(eval echo $(grep ^ID= /etc/os-release | sed -e 's/^ID=//' -e 's/rhel/redhat/'))


Name:          grub2
Epoch:         2
Version:       2.04
Release:       1%{?dist}
Summary:       Bootloader with support for Linux, Multiboot and more

Group:         System Environment/Base
License:       GPLv3+
URL:           http://www.gnu.org/software/grub/
Source0:       https://ftp.gnu.org/gnu/grub/grub-%{version}.tar.xz
Source1:       unifont-5.1.20080820.pcf.gz
Source2:       custom.cfg

# Fedora Patches
Patch0011:     0011-Honor-a-symlink-when-generating-configuration-by-gru.patch
Patch0012:     0012-Move-bash-completion-script-922997.patch
Patch0013:     0013-Update-to-minilzo-2.08.patch
Patch0020:     0020-Fix-bad-test-on-GRUB_DISABLE_SUBMENU.patch
# do not need 0028, it's here for appliance with the next patch
Patch0028:     0028-Add-devicetree-loading.patch  
Patch0029:     0029-Don-t-write-messages-to-the-screen.patch
Patch0030:     0030-Don-t-print-GNU-GRUB-header.patch
Patch0031:     0031-Don-t-add-to-highlighted-row.patch
Patch0032:     0032-Message-string-cleanups.patch
Patch0033:     0033-Fix-border-spacing-now-that-we-aren-t-displaying-it.patch
Patch0034:     0034-Use-the-correct-indentation-for-the-term-help-text.patch
Patch0035:     0035-Indent-menu-entries.patch
Patch0036:     0036-Fix-margins.patch
Patch0037:     0037-Use-2-instead-of-1-for-our-right-hand-margin-so-line.patch
Patch0038:     0038-Enable-pager-by-default.-985860.patch
Patch0039:     0039-F10-doesn-t-work-on-serial-so-don-t-tell-the-user-to.patch
Patch0040:     0040-Don-t-say-GNU-Linux-in-generated-menus.patch
Patch0041:     0041-Don-t-draw-a-border-around-the-menu.patch
Patch0042:     0042-Use-the-standard-margin-for-the-timeout-string.patch

BuildRequires: flex bison binutils python
BuildRequires: ncurses-devel xz-devel bzip2-devel
BuildRequires: freetype-devel libusb-devel
BuildRequires: rpm-devel
%ifarch %{sparc} x86_64 aarch64 ppc64le
# sparc builds need 64 bit glibc-devel - also for 32 bit userland
BuildRequires: /usr/lib64/crt1.o glibc-static
%else
# ppc64 builds need the ppc crt1.o
BuildRequires: /usr/lib/crt1.o glibc-static
%endif
BuildRequires: gcc
BuildRequires: autoconf automake autogen device-mapper-devel
BuildRequires: freetype-devel gettext-devel git
BuildRequires: texinfo
BuildRequires: dejavu-sans-fonts
BuildRequires: help2man

Requires:      gettext which file
Requires:      %{name}-tools = %{epoch}:%{version}-%{release}
Requires:      os-prober >= 1.58-11
Requires(pre): dracut
Requires(post):dracut

ExcludeArch:   s390 s390x
Obsoletes:     %{name} <= 1:2.00-20%{?dist}

%description
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.  It support rich varietyof kernel formats,
file systems, computer architectures and hardware devices.  This subpackage
provides support for PC BIOS systems.

%package efi
Summary:       GRUB for EFI systems.
Group:         System Environment/Base
Requires:      %{name}-tools = %{epoch}:%{version}-%{release}
Obsoletes:     %{name}-efi <= 1:2.00-20%{?dist}

%description efi
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.  It support rich varietyof kernel formats,
file systems, computer architectures and hardware devices.  This subpackage
provides support for EFI systems.

%package efi-modules
Summary:       Modules used to build custom grub.efi images
Group:         System Environment/Base
Requires:      %{name}-tools = %{epoch}:%{version}-%{release}
Obsoletes:     %{name}-efi <= 1:2.00-20%{?dist}

%description efi-modules
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.  It support rich varietyof kernel formats,
file systems, computer architectures and hardware devices.  This subpackage
provides support for rebuilding your own grub.efi on EFI systems.

%package tools
Summary:       Support tools for GRUB.
Group:         System Environment/Base
Requires:      gettext os-prober which file system-logos
%if 0%{?rhel} == 7
Requires:      grubby
%else
Requires:      grubby-deprecated
%endif
Provides:      %{name}-common = %{epoch}:%{version}-%{release}
Provides:      %{name}-tools-minimal = %{epoch}:%{version}-%{release}

%description tools
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.  It support rich varietyof kernel formats,
file systems, computer architectures and hardware devices.  This subpackage
provides tools for support of all platforms.


%prep
%autosetup -p1 -n grub-%{version}
cp %{SOURCE1} unifont.pcf.gz

%build
./autogen.sh
%configure                     \
   CFLAGS="-Os -g"             \
   TARGET_LDFLAGS=-static      \
        --with-platform=efi    \
        --with-grubdir=%{name} \
        --program-transform-name=s,grub,%{name}, \
        --disable-grub-mount   \
        --disable-werror

%{make_build}

GRUB_MODULES=" all_video boot btrfs cat chain configfile echo \
        efifwsetup efinet ext2 fat font gfxmenu gfxterm gzio halt \
        hfsplus iso9660 jpeg loadenv loopback lvm mdraid09 mdraid1x \
        minicmd normal part_apple part_msdos part_gpt \
        password_pbkdf2 png \
        reboot search search_fs_uuid search_fs_file search_label \
        serial sleep syslinuxcfg test tftp video xfs"
GRUB_MODULES+=" linux "

./grub-mkimage -O %{grubefiarch} -o %{grubefiname} -p /EFI/%{efidir} \
        -d grub-core ${GRUB_MODULES}

sed -i -e 's,(grub),(%{name}),g' \
    -e 's,grub.info,%{name}.info,g' \
    -e 's,\* GRUB:,* %{name}:,g' \
    -e 's,/boot/grub/,/boot/%{name}/,g' \
    -e 's,\([^-]\)grub-\([a-z]\),\1%{name}-\2,g' \
    docs/grub.info
sed -i -e 's,grub-dev,%{name}-dev,g' docs/grub-dev.info

/usr/bin/makeinfo --html --no-split -I docs -o grub-dev.html docs/grub-dev.texi
/usr/bin/makeinfo --html --no-split -I docs -o grub.html docs/grub.texi
sed -i -e 's,/boot/grub/,/boot/%{name}/,g' \
    -e 's,\([^-]\)grub-\([a-z]\),\1%{name}-\2,g' \
    grub.html


%install
%{make_build} DESTDIR=%{buildroot} install
find %{buildroot} -iname "*.module" -exec chmod a-x {} \;

# Ghost config file
install -m 755 -d %{buildroot}/boot/efi/EFI/%{efidir}/
touch %{buildroot}/boot/efi/EFI/%{efidir}/grub.cfg
ln -s ../boot/efi/EFI/%{efidir}/grub.cfg %{buildroot}%{_sysconfdir}/%{name}-efi.cfg

# Custom config for console colors
install -m 644 -D %{SOURCE2} %{buildroot}/boot/%{name}/custom.cfg

# Pre-installed grub-efi stub
install -m 755 %{grubefiname} %{buildroot}/boot/efi/EFI/%{efidir}/%{grubefiname}
install -m 755 -d %{buildroot}/boot/efi/EFI/BOOT/
install -m 755 %{grubefiname} %{buildroot}/boot/efi/EFI/BOOT/%{grububootname}

# Make selinux happy with exec stack binaries.
mkdir %{buildroot}%{_sysconfdir}/prelink.conf.d/
cat << EOF > %{buildroot}%{_sysconfdir}/prelink.conf.d/%{name}.conf
# these have execstack, and break under selinux
-b /usr/bin/%{name}-script-check
-b /usr/bin/%{name}-mkrelpath
-b /usr/bin/%{name}-fstest
-b /usr/sbin/%{name}-bios-setup
-b /usr/sbin/%{name}-probe
-b /usr/sbin/%{name}-sparc64-setup
EOF

mv %{buildroot}%{_infodir}/grub.info %{buildroot}%{_infodir}/%{name}.info
mv %{buildroot}%{_infodir}/grub-dev.info %{buildroot}%{_infodir}/%{name}-dev.info
rm %{buildroot}%{_infodir}/dir

mkdir -p %{buildroot}/boot/efi/EFI/%{efidir} boot/%{name}
ln -s ../efi/EFI/%{efidir}/grubenv %{buildroot}/boot/%{name}/grubenv

# Don't run debuginfo on all the grub modules and whatnot; it just
# rejects them, complains, and slows down extraction.
%global finddebugroot "%{_builddir}/%{?buildsubdir}/debug"
mkdir -p %{finddebugroot}/usr
cp -a %{buildroot}/usr/bin %{finddebugroot}/usr/bin
cp -a %{buildroot}/usr/sbin %{finddebugroot}/usr/sbin

%global dip RPM_BUILD_ROOT=%{finddebugroot} %{__debug_install_post}
%define __debug_install_post ( %{dip}                               \
    install -m 0755 -d %{buildroot}/usr/lib/ %{buildroot}/usr/src/  \
    cp -al %{finddebugroot}/usr/lib/debug/                          \\\
        %{buildroot}/usr/lib/debug/                                 \
    cp -al %{finddebugroot}/usr/src/debug/                          \\\
        %{buildroot}/usr/src/debug/ )


%clean
rm -rf %{buildroot}


%post tools
if [ "$1" = 1 ]; then
    /sbin/install-info --info-dir=%{_infodir} %{_infodir}/%{name}.info.gz || :
    /sbin/install-info --info-dir=%{_infodir} %{_infodir}/%{name}-dev.info.gz || :
fi

%preun tools
if [ "$1" = 0 ]; then
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/%{name}.info.gz || :
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/%{name}-dev.info.gz || :
fi


%files efi
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}-efi.cfg
%attr(0755,root,root)/boot/efi/EFI/%{efidir}/*.efi
%attr(0755,root,root)/boot/efi/EFI/BOOT/*
%ghost %config(noreplace) /boot/efi/EFI/%{efidir}/grub.cfg
%doc COPYING
/boot/%{name}/grubenv
# I know 0700 seems strange, but it lives on FAT so that's what it'll
# get no matter what we do.
%config(noreplace) %ghost %attr(0700,root,root)/boot/efi/EFI/%{efidir}/grubenv

%files efi-modules
%defattr(-,root,root,-)
%{_libdir}/grub/%{grubefiarch}

%files tools
%defattr(-,root,root,-)
%dir %{_libdir}/grub/
%dir %{_datarootdir}/grub/
%{_datarootdir}/grub/*
%{_sbindir}/%{name}-bios-setup
%{_sbindir}/%{name}-install
%{_sbindir}/%{name}-macbless
%{_sbindir}/%{name}-mkconfig
%{_sbindir}/%{name}-ofpathname
%{_sbindir}/%{name}-probe
%{_sbindir}/%{name}-reboot
%{_sbindir}/%{name}-set-default
%{_sbindir}/%{name}-sparc64-setup
%{_bindir}/%{name}-editenv
%{_bindir}/%{name}-file
%{_bindir}/%{name}-fstest
%{_bindir}/%{name}-glue-efi
%{_bindir}/%{name}-kbdcomp
%{_bindir}/%{name}-menulst2cfg
%{_bindir}/%{name}-mkfont
%{_bindir}/%{name}-mkimage
%{_bindir}/%{name}-mklayout
%{_bindir}/%{name}-mknetdir
%{_bindir}/%{name}-mkpasswd-pbkdf2
%{_bindir}/%{name}-mkrelpath
%ifnarch %{sparc}
%{_bindir}/%{name}-mkrescue
%endif
%{_bindir}/%{name}-mkstandalone
%{_bindir}/%{name}-render-label
%{_bindir}/%{name}-script-check
%{_bindir}/%{name}-syslinux2cfg
%{_datarootdir}/bash-completion/completions/grub
%{_sysconfdir}/prelink.conf.d/%{name}.conf
%attr(0700,root,root) %dir %{_sysconfdir}/grub.d
%config %{_sysconfdir}/grub.d/??_*
%{_sysconfdir}/grub.d/README
%attr(0644,root,root) %ghost %config(noreplace) %{_sysconfdir}/default/grub
%dir /boot/%{name}
/boot/%{name}/custom.cfg
%{_infodir}/%{name}*
%{_datadir}/man/man?/*
%doc COPYING INSTALL
%doc NEWS README
%doc THANKS TODO
%doc grub.html
%doc grub-dev.html docs/font_char_metrics.png
# locales
%dir %{_datarootdir}/locale
%{_datarootdir}/locale/*
