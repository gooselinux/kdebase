Name: kdebase
Summary: KDE Core Files
Epoch: 6
Version: 4.3.4
Release: 4%{?dist}
License: GPLv2
Group: User Interface/Desktops
URL: http://www.kde.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source0: ftp://ftp.kde.org/pub/kde/stable/%{version}/src/kdebase-%{version}.tar.bz2

# search path for plugins
Patch0: kdebase-4.1.80-nsplugins-paths.patch

# konsole session management
Patch1: kdebase-4.1.70-konsole-session.patch

# make menuitem Home visible
Patch2: kdebase-4.2.1-home-icon.patch

# 4.3 branch
Patch100: kdebase-4.3.5.patch

# 4.4 (backported from trunk) upstream patches
# Allow 'Open Folder in Tabs' in Konsole to support SSH bookmarks (kde#177637)
# http://websvn.kde.org/?revision=1033653&view=revision
Patch200: kdebase-4.3.3-konsole-kde#177637.patch

%ifnarch s390 s390x
Requires: eject
%endif
Requires: %{name}-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires: kdebase-runtime

Provides: kdebase4 = %{version}-%{release}
%{?_isa:Provides: kdebase4%{?_isa} = %{version}-%{release}}

BuildRequires: alsa-lib-devel
BuildRequires: bzip2-devel
BuildRequires: cmake >= 2.6.2
BuildRequires: cyrus-sasl-devel
BuildRequires: doxygen
BuildRequires: fontconfig-devel
BuildRequires: gettext
BuildRequires: giflib-devel
BuildRequires: hal-devel
BuildRequires: pcre-devel
BuildRequires: kdebase-workspace-devel
BuildRequires: kdelibs4-devel >= %{version}
BuildRequires: kdepimlibs-devel >= %{version}
%ifnarch s390 s390x
BuildRequires: libraw1394-devel
BuildRequires: libusb-devel
%endif
BuildRequires: OpenEXR-devel
BuildRequires: openssl-devel
BuildRequires: pciutils-devel
BuildRequires: pcre-devel
BuildRequires: pkgconfig
BuildRequires: qimageblitz-devel
BuildRequires: libsmbclient-devel
BuildRequires: soprano-devel 
BuildRequires: strigi-devel 
BuildRequires: xorg-x11-font-utils
BuildRequires: xorg-x11-proto-devel
BuildRequires: glib2-devel

%description
Core runtime requirements and applications for the KDE 4.

%package libs
Summary: Runtime libraries for %{name}
Group: System Environment/Libraries
Requires: kdelibs4%{?_isa} >= %{version}
Requires: kdepimlibs%{?_isa} >= %{version}

%description libs
%{summary}.

%package devel
Group: Development/Libraries
Summary: Development files for %{name}
Provides: kdebase4-devel = %{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires: kdelibs4-devel
Requires: kdepimlibs4-devel

%description devel
%{summary}.


%prep
%setup -q

%patch0 -p1 -b .nsplugins-paths
%patch1 -p1 -b .konsole-session
%patch2 -p1 -b .home-icon

# 4.3 branch
%patch100 -p1 -b .kde435

# 4.4 (backported from trunk) upstream patches
%patch200 -p0 -b .konsole-kde#177637

# fix incorrect assumption that we're building in a combined kdebase tree
sed -i -e 's/EXISTS "${kdebase_SOURCE_DIR}"/0/g' apps/CMakeLists.txt


%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%{cmake_kde4} ..
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
rm -rf %{buildroot}
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}

# move devel symlinks
mkdir -p %{buildroot}%{_kde4_libdir}/kde4/devel
pushd %{buildroot}%{_kde4_libdir}
for i in lib*.so
do
  case "$i" in
    libkdeinit4_*.so|libkonsoleprivate.so)
      ;;
    *)
      linktarget=`readlink "$i"`
      rm -f "$i"
      ln -sf "../../$linktarget" "kde4/devel/$i"
      ;;
  esac
done
popd

# konquerorsu only show in KDE
echo 'OnlyShowIn=KDE;' >> %{buildroot}%{_kde4_datadir}/applications/kde4/konquerorsu.desktop

# create/own some dirs 
mkdir -p %{buildroot}%{_kde4_appsdir}/konqueror/{kpartplugins,icons,opensearch}

# creat file list for lang
HTML_DIR=$(kde4-config --expandvars --install html)
if [ -d %{buildroot}${HTML_DIR} ]; then
for lang_dir in %{buildroot}${HTML_DIR}/* ; do
  if [ -d ${lang_dir} ]; then
    lang=$(basename ${lang_dir})
    echo "%lang(${lang}) ${HTML_DIR}/${lang}/*/" >> %{name}.lang
  fi
done
fi


%clean
rm -rf %{buildroot}


%post
touch --no-create %{_kde4_iconsdir}/hicolor &> /dev/null ||:
touch --no-create %{_kde4_iconsdir}/oxygen &> /dev/null ||:

%posttrans
gtk-update-icon-cache %{_kde4_iconsdir}/hicolor &> /dev/null ||:
gtk-update-icon-cache %{_kde4_iconsdir}/oxygen &> /dev/null ||:
update-desktop-database -q &> /dev/null ||:

%postun
if [ $1 -eq 0 ] ; then
  touch --no-create %{_kde4_iconsdir}/hicolor &> /dev/null ||:
  gtk-update-icon-cache %{_kde4_iconsdir}/hicolor &> /dev/null ||:
  touch --no-create %{_kde4_iconsdir}/oxygen &> /dev/null ||:
  gtk-update-icon-cache %{_kde4_iconsdir}/oxygen &> /dev/null ||:
  update-desktop-database -q &> /dev/null ||:
fi

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig


%files -f %{name}.lang
%defattr(-,root,root,-)
%{_kde4_bindir}/*
%{_kde4_datadir}/applications/kde4/*.desktop
%{_kde4_appsdir}/*
%{_kde4_datadir}/config.kcfg/*
%{_datadir}/dbus-1/interfaces/*
%{_kde4_iconsdir}/hicolor/*/*/*
%{_kde4_iconsdir}/oxygen/*/*/*
%{_kde4_datadir}/kde4/services/*.desktop
%{_kde4_datadir}/kde4/services/ServiceMenus/
%{_kde4_datadir}/kde4/services/kded/*.desktop
%{_kde4_datadir}/kde4/services/useragentstrings/
%{_kde4_datadir}/kde4/servicetypes/*.desktop
%{_kde4_libdir}/kde4/*.so
%exclude %{_kde4_libdir}/kde4/devel/
%{_mandir}/man1/*
%{_kde4_datadir}/autostart/*.desktop
%{_kde4_configdir}/*
%{_kde4_datadir}/templates/*
%{_kde4_datadir}/templates/.source/*
%{_kde4_libdir}/libkdeinit4_*.so
%{_kde4_libdir}/libkonsoleprivate.so
%{_kde4_datadir}/kde4/services/plasma-applet-folderview.desktop
%{_kde4_libdir}/kde4/plasma_applet_folderview.so

%files libs
%defattr(-,root,root,-)
%{_kde4_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%{_kde4_includedir}/*
%{_kde4_libdir}/kde4/devel/lib*.so


%changelog
* Tue Mar 30 2010 Than Ngo <than@redhat.com> - 6:4.3.4-4
- rebuilt against qt 4.6.2

* Fri Jan 22 2010 Than Ngo <than@redhat.com> - 6:4.3.4-3
- backport 4.3.5 fixes

* Sat Dec 12 2009 Than Ngo <than@redhat.com> - 6:4.3.4-2
- cleanup

* Tue Dec 01 2009 Than Ngo <than@redhat.com> - 4.3.4-1
- 4.3.4

* Wed Nov 11 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.3.3-3
- allow 'Open Folder in Tabs' in Konsole to support SSH bookmarks (kde#177637)
  (upstream patch backported from 4.4)

* Mon Nov 09 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.3-2
- BR: webkitpart-devel >= 0.0.2

* Sat Oct 31 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.3-1
- 4.3.3

* Fri Oct 09 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.3.2-3
- backport upstream patch for bookmark editor drag&drop crash (kde#160679)

* Wed Oct 07 2009 Than Ngo <than@redhat.com> - 4.3.2-2
- fix Dolphin crash (regression)

* Sun Oct 04 2009 Than Ngo <than@redhat.com> - 4.3.2-1
- 4.3.2

* Sun Sep 27 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.1-4
- BR: webkitpart-devel
- fix Provides: kdebase4%%{?_isa} (not kdelibs)

* Sun Sep 27 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.1-3
- own %%_kde4_appsdir/konqueror/{kpartplugins,icons,opensearch}
- %%lang'ify HTML docs
- Provides: kdelibs4%%{?_isa} 

* Wed Sep  2 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.3.1-2
- fix context menus in Konsole (kdebug:186745)

* Fri Aug 28 2009 Than Ngo <than@redhat.com> - 4.3.1-1
- 4.3.1
- drop/revert kde-plasma-folderview subpkg

* Tue Aug 25 2009 Rex Dieter <rdieter@fedoraproject.org> 4.3.0-2
- kde-plasma-folderview subpkg
- %%?_isa'ify -libs deps

* Thu Jul 30 2009 Than Ngo <than@redhat.com> - 4.3.0-1
- 4.3.0

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:4.2.98-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 21 2009 Than Ngo <than@redhat.com> - 4.2.98-1
- 4.3rc3

* Thu Jul 09 2009 Than Ngo <than@redhat.com> - 4.2.96-1
- 4.3rc2

* Thu Jun 25 2009 Than Ngo <than@redhat.com> - 4.2.95-1
- 4.3rc1

* Wed Jun 03 2009 Rex Dieter <rdieter@fedoraproject.org> - 6:4.2.90-1
- KDE-4.3 beta2 (4.2.90)

* Tue Jun 02 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 6:4.2.85-2
- Fedora 8 is EOL'ed, drop conditionals and cleanup the specfile

* Wed May 13 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.85-1
- KDE 4.3 beta 1

* Tue Apr 21 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.2-3
- #496447 -  fix disabling konsole's flow control

* Wed Apr 01 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.2-2
- optimize scriptlets

* Mon Mar 30 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.2-1
- KDE 4.2.2

* Mon Mar 09 2009 Than Ngo <than@redhat.com> - 4.2.1-3
- apply patch to fix regression in konsole, layout regression affecting apps
  using the KPart

* Wed Mar 04 2009 Than Ngo <than@redhat.com> - 4.2.1-2
- apply patch to fix regression in konsole, double-click selection works again

* Fri Feb 27 2009 Than Ngo <than@redhat.com> - 4.2.1-1
- 4.2.1

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6:4.2.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.0-6
- unbreak apps like vim or mc under Konsole

* Thu Feb 12 2009 Rex Dieter <rdieter@fedorparoject.org> - 4.2.0-5
- avoid_kde3_services patch
- fix home-icon patch

* Thu Feb 12 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.0-4
- add Home icon to the Applications menu by default (#457756)

* Wed Feb 11 2009 Than Ngo <than@redhat.com> - 4.2.0-3
- apply patch to make dolphin working well with 4.5

* Wed Jan 28 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.0-2
- KDEInit could not launch '/usr/bin/konsole' (kdebug#162729)

* Thu Jan 22 2009 Than Ngo <than@redhat.com> - 4.2.0-1
- 4.2.0

* Wed Jan 07 2009 Than Ngo <than@redhat.com> - 4.1.96-1
- 4.2rc1

* Thu Dec 11 2008 Than Ngo <than@redhat.com> -  4.1.85-1
- 4.2beta2

* Thu Nov 27 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 6:4.1.80-4
- BR plasma-devel instead of kdebase-workspace-devel

* Sun Nov 23 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 6:4.1.80-3
- rebase nsplugins-path patch

* Thu Nov 20 2008 Than Ngo <than@redhat.com>  4.1.80-2
- merged

* Wed Nov 19 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 6:4.1.80-1
- 4.1.80
- patch100 was backported from 4.2 (4.1.6x), removed from patch list
- ported 4.1.2 konsole patches
- drop the second konsole patch (upstreamed)
- using make install/fast
- BR cmake >= 2.6.2

* Wed Nov 12 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.3-2
- readd kde#156636 patch (Konsole keyboard actions backport)

* Tue Nov  4 2008 Lukáš Tinkl <ltinkl@redhat.com> 4.1.3-1
- KDE 4.1.3

* Thu Oct 16 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.2-5
- backport kbd actions for switching to Nth tab in Konsole from 4.2 (kde#156636)

* Mon Oct 06 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.2-4
- updated konsole session management patch from Stefan Becker

* Mon Oct 06 2008 Than Ngo <than@redhat.com> 4.1.2-3
- bz#465451, backport konsole session management, thanks to Stefan Becker

* Mon Sep 29 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.2-2
- make VERBOSE=1
- respin against new(er) kde-filesystem

* Fri Sep 26 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.2-1
- 4.1.2

* Thu Sep 18 2008 Than Ngo <than@redhat.com> 4.1.1-2
- make bookmark silent

* Fri Aug 29 2008 Than Ngo <than@redhat.com> 4.1.1-1
- 4.1.1

* Fri Jul 25 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.0-1.1
- always check for Plasma actually being present (fixes F8 kdebase4 build)

* Wed Jul 23 2008 Than Ngo <than@redhat.com> 4.1.0-1
- 4.1.0

* Tue Jul 22 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.99-2
 respin (libraw1394)

* Fri Jul 18 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.99-1
- 4.0.99

* Fri Jul 11 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.98-2
- BR: pciutils-devel

* Thu Jul 10 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.98-1
- 4.0.98

* Sun Jul 06 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.85-1
- 4.0.85

* Fri Jun 27 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.84-1
- 4.0.84

* Tue Jun 24 2008 Lukáš Tinkl <ltinkl@redhat.com> - 4.0.83-2
- #426108: Add more directories to konqueror's default
  plugin search path list

* Thu Jun 19 2008 Than Ngo <than@redhat.com> 4.0.83-1
- 4.0.83 (beta2)

* Mon Jun 16 2008 Than Ngo <than@redhat.com> 4.0.82-2
- BR kdebase-workspace-devel (F9+)

* Sun Jun 15 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.82-1
- 4.0.82

* Tue May 27 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.80-3
- respun tarball from upstream

* Tue May 27 2008 Than Ngo <than@redhat.com> 4.0.80-2
- rebuild to fix undefined symbol issue in dolphin

* Mon May 26 2008 Than Ngo <than@redhat.com> 4.0.80-1
- 4.1 beta1

* Sun May 11 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.72-2
- quote semicolon in fix for #442834
- only do the echo when konquerorsu.desktop is actually shipped (#445989)

* Tue May 06 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.72-1
- update to 4.0.72 (4.1 alpha 1)
- drop backported kde#160422 and nspluginviewer patches
- add minimum versions to soprano-devel and strigi-devel BRs

* Fri Apr 18 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.3-9
- kwrite.desktop: Categories += Utility (#438786)

* Thu Apr 17 2008 Than Ngo <than@redhat.com> 4.0.3-8
- konquerorsu only show in KDE, #442834

* Mon Apr 14 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.3-7
- nspluginviewer patch (kde#160413)

* Sun Apr 06 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-6
- backport Konsole window size fixes from 4.1 (#439638, kde#160422)

* Thu Apr 03 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-5
- rebuild (again) for the fixed %%{_kde4_buildtype}

* Mon Mar 31 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-4
- add missing BR libraw1394-devel (thanks to Karsten Hopp)
- don't BR libusb-devel on s390 or s390x

* Mon Mar 31 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-3
- rebuild for NDEBUG and _kde4_libexecdir

* Fri Mar 28 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-2
- add Requires: kdebase-runtime oxygen-icon-theme (#438632)

* Fri Mar 28 2008 Than Ngo <than@redhat.com> 4.0.3-1
- 4.0.3
- drop fix for favicons infinite loop, it's included in new version
- omit multilib upgrade hacks
- omit extraneous BR's
- (re)include oxgygen/scalable icons

* Fri Feb 29 2008 Lukáš Tinkl <ltinkl@redhat.com> 4.0.2-2
- fix favicons infinite loop

* Thu Feb 28 2008 Than Ngo <than@redhat.com> 4.0.2-1
- 4.0.2

* Mon Feb 18 2008 Than Ngo <than@redhat.com> 4.0.1-4
- fix nsplugins hangs during login

* Mon Feb 04 2008 Than Ngo <than@redhat.com> 4.0.1-3
- respin

* Fri Feb 01 2008 Than Ngo <than@redhat.com> 4.0.1-2
- add flash fix from stable svn branch

* Thu Jan 31 2008 Than Ngo <than@redhat.com> 4.0.1-1
- 4.0.1

* Wed Jan 30 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.0-3
- resurrect -libs (f9+)
- improve %%description

* Sat Jan 19 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.0-2.1
- Obsoletes: dolphin, d3lphin, Provides: dolphin everywhere

* Tue Jan 08 2008 Rex Dieter <rdieter[AT]fedoraproject.org> 4.0.0-2
- respun tarball

* Mon Jan 07 2008 Than Ngo <than@redhat.com> 4.0.0-1
- 4.0.0

* Tue Dec 25 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.97.0-5
- Obsoletes: dolphin, d3lphin, Provides: dolphin (F9+)

* Fri Dec 14 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.97.0-4
- Obsoletes: -extras (f9+)

* Wed Dec 12 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.97.0-3
- rebuild for changed _kde4_includedir

* Sun Dec 09 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.97.0-2
- rm konsoleprofile when building as kdebase4, does nothing with KDE 3 konsole

* Thu Dec 06 2007 Than Ngo <than@redhat.com> 3.97.0-1
- update to 3.97.0

* Sat Dec 01 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.96.2-1
- merge changes from Sebastian Vahl's version:
  - update to 3.96.2, remove beta warnings
  - BR: kde-filesystem >= 4
  - only remove conflicts when building as kdebase4, update file list
  - run xdg-icon-resource forceupdate for hicolor when building as kdebase
- make this the default kdebase for F9 again

* Mon Nov 19 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.96.0-4
- don't list libkdeinit4_*.so, we remove all of them as conflicts

* Mon Nov 19 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.96.0-3
- remove new directory/files %{_kde4_datadir}/templates (conflict with KDE 3)

* Mon Nov 19 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.96.0-2
- (re)add %{_kde4_iconsdir}/oxygen/*/*/* to file list

* Mon Nov 19 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.96.0-1
- update to 3.96.0
- drop dolphin-desktop patch, fixed upstream
- don't list files which are now in kdebase-runtime
- add Requires: kdebase-runtime

* Thu Oct 25 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.94.0-2
- patch dolphin.desktop to get Dolphin to start from the menu

* Fri Oct 19 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.94.0-1
- update to 3.94.0

* Thu Oct 4 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.93.0-5
- don't make this the default kdebase on F9 yet
- drop ExcludeArch: ppc64 (#300601)

* Fri Sep 21 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.93.0-4
- ExcludeArch: ppc64 (#300601)
- update description

* Thu Sep 13 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.93.0-3
- add missing BR alsa-lib-devel

* Wed Sep 12 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.93.0-2
- remove files which conflict with KDE 3
- move devel symlinks to %%{_kde4_libdir}/kde4/devel/
- Conflicts with KDE 3 versions of dolphin pre d3lphin rename

* Wed Sep 12 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.93.0-1
- update to 3.93.0
- drop kde4home patch (no longer applied)
- drop KDM ConsoleKit patch (KDM is now in kdebase-workspace)
- remove kdebase-kdm Obsoletes/Provides (for the same reason)
- remove KDM (and KDM session) setup code (for the same reason)
- remove rss-glx conflict (Plasma is now in kdebase-workspace)
- remove redhat-startkde patch (startkde is now in kdebase-workspace)
- remove kde4-opt.sh (all the code in it is commented out)
- remove kde4-xdg_menu_prefix.sh (only needed for kdebase-workspace)
- remove bogus BRs on automake and libtool
- remove workspace-only BRs
- add BR qimageblitz-devel, xine-lib-devel (all), libxcb-devel (F8+)
- remove workspace files and directories
- handle icons (moved from kdelibs4)
- add mkdir %%{buildroot} in %%install

* Tue Aug 14 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.92.0-4
- use macros.kde4
- License: GPLv2

* Mon Jul 30 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.92.0-3
- bump rss-glx Conflicts because the conflict is still there in 0.8.1.p-7.fc8
- rss-glx conflict only needed if "%%{_prefix}" == "/usr"
- consolekit_kdm patch only needs BR dbus-devel, not ConsoleKit-devel

* Mon Jul 30 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.92.0-2
- consolekit_kdm patch (#228111, kde#147790)
- update startkde patch

* Sat Jul 28 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.92.0-1
- kde-3.92 (kde-4-beta1)

* Wed Jul 25 2007 Than Ngo <than@redhat.com> - 3.91.0-6
- fix startkde
- add env/shutdown directory

* Thu Jul 19 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.91.0-5
- kde4.desktop: fix session Name

* Tue Jul 17 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.91.0-4
- cleanup/fix kde4.desktop
- kdepimlibs4->kdepimlibs

* Thu Jun 29 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.91.0-3
- fix %%_sysconfdir for %%_prefix != /usr case.

* Thu Jun 28 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.91.0-2
- updated kde4home.diff
- CMAKE_BUILD_TYPE=RelWithDebInfo (we're already using %%optflags)

* Wed Jun 27 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.91.0-1
- kde-3.91.0
- CMAKE_BUILD_TYPE=debug

* Sat Jun 23 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.90.1-2
- specfile cleanup (%%prefix issues mostly)

* Sun May 13 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.90.1-1
- update to 3.90.1
- bump cmake BR to 2.4.5 as required upstream now
- don't set execute bits by hand anymore, cmake has been fixed
- use multilibs in /opt/kde4
- add BR openssl-devel, NetworkManager-devel, bluez-libs-devel
- add explicit BRs on strigi-devel, zlib-devel, bzip2-devel, libpng-devel
  in case we want to drop the Rs on these from kdelibs4-devel
- consistently add all BRs as -devel Rs, not just almost all, until we can
  figure out which, if any, are really needed
- BR libsmbclient-devel instead of samba on F>=7, EL>=6

* Fri Mar 23 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.80.3-4
- restore minimum version requirement for cmake
- build against libxklavier on EL5
- don't set QT4DIR and PATH anymore, qdbuscpp2xml has been fixed

* Mon Mar 05 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 3.80.3-3
- +eXecute perms for %%{_prefix}/lib/*

* Fri Feb 23 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.80.3-2
- rebuild for patched FindKDE4Internal.cmake

* Wed Feb 21 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.80.3-1
- update to 3.80.3
- update and improve parallel-installability patch
- drop obsolete joydevice.h patch
- remove translations of "KDE" without the "4" from kde4.desktop
- resync BR and -devel Requires
- don't set LD_LIBRARY_PATH
- set QT4DIR and PATH so CMake's direct $QT4DIR/qdbuscpp2xml calls work
- fix missing underscore in _datadir
- install kde4.desktop in install, not prep
- fix invalid syntax in kde4.desktop

* Wed Nov 29 2006 Chitlesh Goorah <chitlesh [AT] fedoraproject DOT org> 3.80.2-0.3.20061003svn
- dropped -DCMAKE_SKIP_RPATH=TRUE from cmake
- compiling with QA_RPATHS=0x0003; export QA_RPATHS

* Sun Nov 26 2006 Chitlesh Goorah <chitlesh [AT] fedoraproject DOT org> 3.80.2-0.2.20061003svn
- parallel build support
- added -DCMAKE_SKIP_RPATH=TRUE to cmake to skip rpath
- dropped qt4-devel >= 4.2.0, kdelibs4-devel as BR
- spec file cleanups and added clean up in %%install
- fixed PATH for libkdecore.so.5; cannot open shared object file;
- added Logitech mouse support
- added dbus-devel, hal-devel and more as BR
- fixed broken joydevice.h - Kevin Kofler
- added file kde4.desktop

* Sun Oct 08 2006 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.80.2-0.1.20061003svn
- first Fedora RPM (parts borrowed from the OpenSUSE kdebase 4 RPM and the Fedora kdebase 3 RPM)
- apply parallel-installability patch
