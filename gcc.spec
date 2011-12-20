# functions with printf format attribute but with special parser and also
# receiving non constant format strings
%define		Werror_cflags			%{nil}

# avoid failures when testing if compiler used to build gcc can generate
# shared objects (regardless of unresolved symbols)
%define		_disable_ld_no_undefined	1

# avoid build failure due to configure built with different autoconf version
%define		_disable_libtoolize		1

#-----------------------------------------------------------------------
%define		cross			mipsel
%define		cross_target		%{cross}-linux
%define		branch			4.6
%define		gccdir			%{_libdir}/gcc/%{cross_target}/%{version}

#-----------------------------------------------------------------------
%define		gcc_major		1
%define		libgcc			%mklibname gcc %{gcc_major}

#-----------------------------------------------------------------------
Name:		cross-%{cross}-gcc
Version:	4.6.2
Release:	1
Summary:	GNU Compiler Collection
License:	GPLv3+ and GPLv3+ with exceptions and GPLv2+ with exceptions and LGPLv2+ and BSD
Group:		Development/C
URL:		http://gcc.gnu.org/
Source0:	gcc-%{version}.tar.bz2
Source1:	lsb-headers-3.1.1.tar.bz2
BuildRequires:	binutils >= 2.20.51.0.2
BuildRequires:	elfutils-devel >= 0.147
BuildRequires:	glibc-devel >= 2.4.90
BuildRequires:	dejagnu
BuildRequires:	bison
BuildRequires:	elfutils-devel
BuildRequires:	flex
BuildRequires:	gdb
BuildRequires:	gettext
BuildRequires:	sharutils
BuildRequires:	mpfr-devel
BuildRequires:	libgmp-devel
BuildRequires:	libmpc-devel

Patch0:		gcc-4.6.0-uclibc-ldso-path.patch
Patch1:		lsb-headers-3.1.1-misc.patch
Patch2:		lsb-headers-3.1.1-mips-support.patch

%description
The gcc package contains the GNU Compiler Collection version 4.6.

%files
%defattr(-,root,root)
%{_bindir}/*
%{_libdir}/gcc/%{cross_target}

########################################################################
%prep
%setup -q -n gcc-%{version}

%patch0 -p1
mkdir sysroot
pushd sysroot
    mkdir -p usr/include
    tar jxf %{SOURCE1} -C usr/include
    cd usr
%patch1 -p0
%patch2 -p0
popd

#-----------------------------------------------------------------------
%build
OPT_FLAGS=`echo %{optflags} |					\
	sed	-e 's/\(-Wp,\)\?-D_FORTIFY_SOURCE=[12]//g'	\
		-e 's/-m\(31\|32\|64\)//g'			\
		-e 's/-fstack-protector//g'			\
		-e 's/--param=ssp-buffer-size=4//'		\
		-e 's/-pipe//g'`
OPT_FLAGS=`echo "$OPT_FLAGS" | sed -e 's/[[:blank:]]\+/ /g'`

mkdir obj-%{cross_target}
pushd obj-%{cross_target}
    CONFIGURE_TOP=..						\
    CC=%{__cc}							\
    CFLAGS="$OPT_FLAGS" 					\
    CXXFLAGS="$OPT_FLAGS"					\
    %configure2_5x						\
	--disable-libgcj					\
	--disable-libffi					\
	--disable-libgomp					\
	--disable-libquadmath					\
	--disable-libquadmath-support				\
	--disable-libmudflap					\
	--disable-libssp					\
	--disable-libunwind-exceptions				\
	--disable-werror					\
	--enable-__cxa_atexit					\
	--disable-bootstrap					\
	--enable-checking=release				\
	--enable-gnu-unique-object				\
	--enable-languages="c"					\
	--enable-linker-build-id				\
	--disable-plugin					\
	--enable-threads=posix					\
	--with-system-zlib					\
	--with-bugurl=https://qa.mandriva.com/			\
	--with-build-sysroot=$PWD/../sysroot			\
	--with-headers						\
	--disable-multilib					\
	--disable-nls						\
	--disable-shared					\
	--target=%{cross_target}

# (peryvind): xgcc seems to ignore --sysroot, so let's just workaround it for
# by adding a symlink to the headers since xgcc already passes -isystem ./include
    mkdir -p %{cross_target}/libgcc
    ln -sf $PWD/../sysroot/usr/include %{cross_target}/libgcc/include
    %make
popd

#-----------------------------------------------------------------------
%install
%makeinstall_std -C obj-%{cross_target}
rm -fr %{buildroot}/%{_mandir}
rm -fr %{buildroot}/%{_infodir}
rm -f  %{buildroot}/%{_libdir}/libiberty.a
mv -f %{buildroot}%{gccdir}/include{-fixed,}/syslimits.h
mv -f %{buildroot}%{gccdir}/include{-fixed,}/limits.h
rm -fr %{buildroot}%{gccdir}/include-fixed
rm -fr %{buildroot}%{gccdir}/install-tools/include
