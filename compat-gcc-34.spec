#
#		nothing to debug. 3_4-branch is closed.
%define		_enable_debug_packages	0
#
Summary:	GNU Compiler Collection: the C compiler and shared files
Summary(pl.UTF-8):	Kolekcja kompilatorów GNU: kompilator C i pliki współdzielone
Name:		compat-gcc-34
Version:	3.4.6
Release:	1
License:	GPL
Group:		Development/Languages
Source0:	ftp://gcc.gnu.org/pub/gcc/releases/gcc-%{version}/gcc-%{version}.tar.bz2
# Source0-md5:	4a21ac777d4b5617283ce488b808da7b
Patch0:		%{name}-info.patch
Patch1:		%{name}-nolocalefiles.patch
Patch2:		%{name}-nodebug.patch
Patch3:		%{name}-pr16276.patch
Patch4:		%{name}-cxxabi.patch
Patch5:		%{name}-pr-rh.patch
URL:		http://gcc.gnu.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	binutils >= 2:2.15.91.0.2
BuildRequires:	bison
BuildRequires:	fileutils >= 4.0.41
BuildRequires:	flex
BuildRequires:	gettext-tools
BuildRequires:	glibc-devel >= 2.2.5-20
BuildRequires:	perl-devel
BuildRequires:	texinfo >= 4.1
BuildRequires:	zlib-devel
Requires:	binutils >= 2:2.15.91.0.2
Requires:	gcc-dirs >= 1.0-3
Provides:	cpp = %{epoch}:%{version}-%{release}
Obsoletes:	compat-gcc-34-libgcc
Conflicts:	glibc-devel < 2.2.5-20
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%ifarch sparc64
%define		rpmcflags	-O2 -mtune=ultrasparc
%endif

%description
A compiler aimed at integrating all the optimizations and features
necessary for a high-performance and stable development environment.

This package contains the C compiler and some files shared by various
parts of the GNU Compiler Collection. In order to use another GCC
compiler you will need to install the appropriate subpackage.

%description -l pl.UTF-8
Kompilator, posiadający duże możliwości optymalizacyjne niezbędne do
wyprodukowania szybkiego i stabilnego kodu wynikowego.

Ten pakiet zawiera kompilator C i pliki współdzielone przez różne
części kolekcji kompilatorów GNU (GCC). Żeby używać innego kompilatora
z GCC, trzeba zainstalować odpowiedni podpakiet.

%package c++
Summary:	C++ support for gcc
Summary(pl.UTF-8):	Obsługa C++ dla gcc
Group:		Development/Languages
Obsoletes:	compat-gcc-34-libstdc++
Obsoletes:	compat-gcc-34-libstdc++-devel
Obsoletes:	compat-gcc-34-libstdc++-static
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description c++
This package adds C++ support to the GNU Compiler Collection. It
includes support for most of the current C++ specification, including
templates and exception handling.

%description c++ -l pl.UTF-8
Ten pakiet dodaje obsługę C++ do kompilatora gcc. Ma wsparcie dla
dużej ilości obecnych specyfikacji C++.

%prep
%setup -q -n gcc-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p0
%patch4 -p0
%patch5 -p0

# because we distribute modified version of gcc...
perl -pi -e 's/(version.*)";/$1 (PLD Linux)";/' gcc/version.c
perl -pi -e 's@(bug_report_url.*<URL:).*";@$1http://bugs.pld-linux.org/>";@' gcc/version.c

mv ChangeLog ChangeLog.general

%build
# because pr16276 patch modifies configure.ac
cd gcc
%{__autoconf}
cd ..
cp -f /usr/share/automake/config.sub .

rm -rf obj-%{_target_platform} && install -d obj-%{_target_platform} && cd obj-%{_target_platform}

CC="%{__cc}" \
CFLAGS="%{rpmcflags}" \
CXXFLAGS="%{rpmcflags}" \
TEXCONFIG=false \
../configure \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libdir} \
	--infodir=%{_infodir} \
	--mandir=%{_mandir} \
	--program-suffix="-3.4" \
	--enable-version-specific-runtime-libs \
	--enable-shared \
	--enable-threads=posix \
	--enable-__cxa_atexit \
	--enable-languages="c,c++" \
	--enable-c99 \
	--enable-long-long \
	--disable-multilib \
	--disable-libstdcxx-pch \
	--enable-nls \
	--with-gnu-as \
	--with-gnu-ld \
	--with-slibdir=/%{_lib} \
	%{_target_platform}

PATH=$PATH:/sbin:%{_sbindir}

cd ..
%{__make} -C obj-%{_target_platform} \
	BOOT_CFLAGS="%{rpmcflags}" \
	LDFLAGS_FOR_TARGET="%{rpmldflags}" \
	mandir=%{_mandir} \
	infodir=%{_infodir}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_aclocaldir},%{_datadir},%{_infodir}}

cd obj-%{_target_platform}
PATH=$PATH:/sbin:%{_sbindir}

%{__make} -j1 install \
	mandir=%{_mandir} \
	infodir=%{_infodir} \
	DESTDIR=$RPM_BUILD_ROOT

%ifarch sparc64
ln -f $RPM_BUILD_ROOT%{_bindir}/sparc64-pld-linux-gcc \
	$RPM_BUILD_ROOT%{_bindir}/sparc-pld-linux-gcc
%endif

ln -sf gcc-3.4 $RPM_BUILD_ROOT%{_bindir}/cc-3.4
echo ".so gcc-3.4.1" > $RPM_BUILD_ROOT%{_mandir}/man1/cc-3.4.1

cd ..

# include/ contains install-tools/include/* and headers that were fixed up
# by fixincludes, we don't want former
gccdir=$(echo $RPM_BUILD_ROOT%{_libdir}/gcc/*/*/)
mkdir $gccdir/tmp
# we have to save these however
mv $gccdir/include/syslimits.h $gccdir/tmp
mv $gccdir/include/c++ $gccdir/tmp
rm -r $gccdir/include
mv $gccdir/tmp $gccdir/include
cp $gccdir/install-tools/include/*.h $gccdir/include
# but we don't want anything more from install-tools
rm -r $gccdir/install-tools

%clean
rm -rf $RPM_BUILD_ROOT

%post
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

%postun
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

%files
%defattr(644,root,root,755)
%doc ChangeLog.general MAINTAINERS NEWS bugs.html faq.html
%doc gcc/{ChangeLog,ONEWS,README.Portability}
%dir %{_libdir}/gcc/*/*
%dir %{_libdir}/gcc/*/*/include
%attr(755,root,root) %{_bindir}/*-gcc*
%attr(755,root,root) %{_bindir}/gcc-*
%attr(755,root,root) %{_bindir}/gcov-*
%attr(755,root,root) %{_bindir}/cc-*
%attr(755,root,root) %{_bindir}/cpp-*
%{_mandir}/man1/cc-*.1*
%{_mandir}/man1/cpp-*.1*
%{_mandir}/man1/gcc-*.1*
%{_mandir}/man1/gcov-*.1*
%{_libdir}/gcc/*/*/libgcov.a
%{_libdir}/gcc/*/*/libgcc.a
%{_libdir}/gcc/*/*/libgcc_eh.a
%{_libdir}/gcc/*/*/specs
%{_libdir}/gcc/*/*/crt*.o
%attr(755,root,root) %{_libdir}/gcc/*/*/cc1
%attr(755,root,root) %{_libdir}/gcc/*/*/collect2
%{_libdir}/gcc/*/*/include/*.h

%files c++
%defattr(644,root,root,755)
%doc gcc/cp/{ChangeLog,NEWS}
%attr(755,root,root) %{_bindir}/g++-*
%attr(755,root,root) %{_bindir}/*-g++-*
%attr(755,root,root) %{_bindir}/c++-*
%attr(755,root,root) %{_bindir}/*-c++-*
%attr(755,root,root) %{_libdir}/gcc/*/*/cc1plus
%{_libdir}/gcc/*/*/include/c++
%{_libdir}/gcc/*/*/libstdc++.a
%{_libdir}/gcc/*/*/libstdc++.la
%attr(755,root,root) %{_libdir}/gcc/*/*/libstdc++.so*
%{_libdir}/gcc/*/*/libsupc++.la
%{_libdir}/gcc/*/*/libsupc++.a
%{_mandir}/man1/g++-*.1*
