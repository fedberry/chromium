%global debug_package %{nil}
%global chromiumdir %{_libdir}/chromium
%global crd_path %{_libdir}/chrome-remote-desktop

# We don't want any libs in these directories to generate Provides
%global __provides_exclude_from %{chromiumdir}/.*\\.so|%{chromiumdir}/lib/.*\\.so
%global private_libs libEGL|libGLESv2|libVkLayer_core_validation|libVkLayer_swapchain|libVkLayer_object_tracker|libVkLayer_threading|libVkLayer_parameter_validation|libVkLayer_unique_objects
%global __requires_exclude ^(%{private_libs})\\.so

# Generally chromium is a monster if you compile the source code, enabling all; and takes hours compiling; common users doesn't need all tools.
%bcond_without devel_tools

# Chromium users don't need chrome-remote-desktop
%bcond_without remote_desktop

# Use gcc instead of clang (default compiler is clang)
%bcond_without clang

%bcond_with system_libvpx

%bcond_with system_jinja2

# markupsafe
%bcond_with system_markupsafe

# https://github.com/dabeaz/ply/issues/66
%bcond_without system_ply

# Chromium used to break on wayland, hidpi, and colors with gtk3 enabled.
# Hopefully it does not anymore.
%bcond_with _gkt3

# Require libxml2 > 2.9.4 for XML_PARSE_NOXXE
%bcond_without system_libxml2

%if 0%{?fedora} >= 28
%bcond_without system_harfbuzz
%else
%bcond_with system_harfbuzz
%endif

# Jumbo / Unity builds
# https://chromium.googlesource.com/chromium/src/+/lkcr/docs/jumbo.md
%bcond_without jumbo_unity

%global majorversion 69

Name:       chromium
Version:    %{majorversion}.0.3497.100
Release:    1%{?dist}
Summary:    A WebKit (Blink) powered web browser
Group:      Applications/Internet
License:    BSD and LGPLv2+
URL:        https://www.chromium.org
Vendor:     Fedberry
Source0:    https://commondatastorage.googleapis.com/chromium-browser-official/chromium-%{version}.tar.xz
Source1:    chromium-latest.py
%if %{with remote_desktop}
Source2:    chrome-remote-desktop.service
%endif

# The following two source files are copied and modified from
# https://repos.fedorapeople.org/repos/spot/chromium/
Source10:   chromium-wrapper
Source11:   chromium-browser.desktop

# The following two source files are copied verbatim from
# http://pkgs.fedoraproject.org/cgit/rpms/chromium.git/tree/
Source12:   chromium-browser.xml
Source13:   chromium-browser.appdata.xml

# Support build flags passed in the --args to gn (Debian)
Patch1:     chromium-buildflags.patch

# Respect specified number of parallel jobs while bootstrapping gn (Debian)
Patch2:     chromium-parallel.patch

# Change master_preferences path
Patch3:     chromium-master-prefs-path.patch

# Don't use unversioned python commands. This patch is based on
# https://src.fedoraproject.org/rpms/chromium/c/7048e95ab61cd143
# https://src.fedoraproject.org/rpms/chromium/c/cb0be2c990fc724e
Patch4:    chromium-bootstrap-python2.patch

# Disable build commands for embedded fontconfig (Debian)
Patch13:    chromium-fontconfig.patch

### Misc. Gentoo fixes
# Re-enable widevine support for linux! :-/
# https://gitweb.gentoo.org/repo/gentoo.git/commit/www-client/chromium/files?id=09b804516320eee06930303870cd68008aac8a8a
Patch24:    chromium-widevine-r2.patch


### Enable mmal hardware acceleration for RPi's
%ifarch armv7hl
#Patch100:     v65.0.3325.212_mmal_2.15.patch

# Fedberry mmal build fixes
#Patch101:     mmal-build-fixes.patch
#Patch102:     mmal-build-fix-gles2.patch
%endif

ExclusiveArch: armv7hl x86_64 i686

BuildRequires: clang, llvm, lld
BuildRequires: ninja-build, bison, gperf, hwdata
BuildRequires: libgcc, glibc
BuildRequires: libatomic
BuildRequires: libcap-devel, cups-devel, minizip-devel, alsa-lib-devel
BuildRequires: pkgconfig(libexif), pkgconfig(nss)
%if %{with _gtk3}
BuildRequires: pkgconfig(gtk+-3.0)
%else
BuildRequires: pkgconfig(gtk+-2.0)
%endif
BuildRequires: pkgconfig(xtst), pkgconfig(xscrnsaver)
BuildRequires: pkgconfig(dbus-1), pkgconfig(libudev)
BuildRequires: pkgconfig(gnome-keyring-1)
BuildRequires: pkgconfig(libffi)
BuildRequires: python2-rpm-macros
BuildRequires: python-beautifulsoup4
BuildRequires: python-html5lib
%if %{with system_jinja2}
BuildRequires: python2-jinja2
%endif
%if %{with system_markupsafe}
BuildRequires: python2-markupsafe
%endif
%if %{with system_ply}
BuildRequires: python2-ply
%endif
BuildRequires: flac-devel
BuildRequires: freetype-devel
%if %{with system_harfbuzz}
BuildRequires: harfbuzz-devel
%endif
BuildRequires: libjpeg-turbo-devel
BuildRequires: libpng-devel
%if %{with system_libvpx}
BuildRequires: libvpx-devel
%endif
BuildRequires: libwebp-devel
BuildRequires: pkgconfig(libxslt)
BuildRequires: opus-devel
%if %{with system_libxml2}
BuildRequires: pkgconfig(libxml-2.0)
%endif
BuildRequires: re2-devel
BuildRequires: snappy-devel
BuildRequires: yasm
BuildRequires: zlib-devel
BuildRequires: pciutils-devel
BuildRequires: speech-dispatcher-devel
BuildRequires: desktop-file-utils
BuildRequires: libappstream-glib
BuildRequires: pam-devel
BuildRequires: systemd
BuildRequires: git
BuildRequires: nodejs
BuildRequires: libdrm-devel
BuildRequires: mesa-libGL-devel
BuildRequires: pkgconfig(xcb-image)
%ifarch armv7hl
BuildRequires: raspberrypi-vc-libs-devel
BuildRequires: raspberrypi-vc-static
%endif

Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
Requires: hicolor-icon-theme
Requires: re2
Requires: %{name}-libs = %{version}-%{release}
%ifarch armv7hl
Requires: raspberrypi-vc-libs
%endif
Provides: chromium >= %{majorversion}


%description
Chromium is an open-source web browser, powered by WebKit (Blink).


%package libs
Summary: Shared libraries used by chromium (and chrome-remote-desktop)
Provides: %{name}-libs%{_isa} = %{version}-%{release}
Provides: chromium-libs >= %{majorversion}
Provides: bundled(mesa)
Provides: bundled(libVkLayer_core_validation)
Provides: bundled(libVkLayer_swapchain)
Provides: bundled(libVkLayer_object_tracker)
Provides: bundled(libVkLayer_threading)
Provides: bundled(libVkLayer_parameter_validation)
Provides: bundled(libVkLayer_unique_objects)
Obsoletes: %{name}-libs-media < %{majorversion}

%description libs
Shared libraries used by chromium (and chrome-remote-desktop).


%if %{with devel_tools}
%package chromedriver
Summary: WebDriver for Google Chrome/Chromium
Group: Development/Libraries
Provides: chromedriver >= %{majorversion}

%description chromedriver
WebDriver is an open source tool for automated testing of webapps across many
browsers. It provides capabilities for navigating to web pages, user input,
JavaScript execution, and more. ChromeDriver is a standalone server which
implements WebDriver's wire protocol for Chromium. It is being developed by
members of the Chromium and WebDriver teams.
%endif


%if %{with remote_desktop}
%package -n chrome-remote-desktop
Summary: Remote desktop support for google-chrome & chromium
Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires: xorg-x11-server-Xvfb

Requires: %{name}-libs%{_isa} = %{version}-%{release}

%description -n chrome-remote-desktop
Remote desktop support for google-chrome & chromium.
%endif



%prep
%autosetup -n chromium-%{version} -p1

%if 0%{?fedora} > 27
# Change shebang in all relevant files in this directory and all subdirectories
find -type f -exec sed -iE '1s=^#! */usr/bin/\(python\|env python\)[23]\?=#!%{__python2}=' {} +
%endif

%if %{with system_markupsafe}
pushd third_party/
rm -rf markupsafe/
ln -sf %{python2_sitearch}/markupsafe/ markupsafe
popd
%else
pushd third_party
rm -rf markupsafe/
git clone --depth 1 https://github.com/pallets/markupsafe.git
cp -f $PWD/markupsafe/markupsafe/*.py $PWD/markupsafe/
cp -f $PWD/markupsafe/markupsafe/*.c $PWD/markupsafe/
popd
%endif

# node fix
mkdir -p third_party/node/linux/node-linux-x64/bin
ln -s /usr/bin/node third_party/node/linux/node-linux-x64/bin/node

%if %{with remote_desktop}
# Fix hardcoded path in remoting code
sed -i 's|/opt/google/chrome-remote-desktop|%{crd_path}|g' remoting/host/setup/daemon_controller_delegate_linux.cc
%endif

# xlocale.h is gone in >= F26
sed -r -i 's/xlocale.h/locale.h/' buildtools/third_party/libc++/trunk/include/__locale

%if %{with clang}
%if 0%{?fedora} < 28
# Remove compiler flags not supported by Fedora's system clang
sed -i \
-e '/"-Wno-unused-lambda-capture"/d' \
-e '/"-Wno-enum-compare-switch"/d' \
-e '/"-Wno-null-pointer-arithmetic"/d' \
-e '/"-Wno-tautological-unsigned-zero-compare"/d' \
-e '/"-Wno-tautological-unsigned-enum-zero-compare"/d' \
-e '/"-Wno-tautological-constant-compare"/d' \
build/config/compiler/BUILD.gn

# Remove ldflags not supported by Fedora's system lld
sed -i 's/ || use_lld//' tools/v8_context_snapshot/BUILD.gn
%endif

%if 0%{?fedora} > 27
sed -i \
-e '/"-Wno-ignored-pragma-optimize"/d' \
build/config/compiler/BUILD.gn
%endif
%endif

### build with widevine support

# Patch from crbug (chromium bugtracker)
# fix the missing define (if not, fail build) (need upstream fix) (https://crbug.com/473866)
sed '14i#define WIDEVINE_CDM_VERSION_STRING "Something fresh"' -i "third_party/widevine/cdm/stub/widevine_cdm_version.h"


# Allow building against system libraries in official builds
  sed -i 's/OFFICIAL_BUILD/GOOGLE_CHROME_BUILD/' \
    tools/generate_shim_headers/generate_shim_headers.py

python2 build/linux/unbundle/remove_bundled_libraries.py --do-remove \
    buildtools/third_party/libc++ \
    third_party/icu \
    base/third_party/icu/ \
    base/third_party/dmg_fp \
    base/third_party/dynamic_annotations \
    base/third_party/libevent \
    base/third_party/nspr \
    base/third_party/superfasthash \
    base/third_party/symbolize \
    base/third_party/valgrind \
    v8/src/third_party/utf8-decoder \
    base/third_party/xdg_mime \
    base/third_party/xdg_user_dirs \
    buildtools/third_party/libc++ \
    buildtools/third_party/libc++abi \
    chrome/third_party/mozilla_security_manager \
    courgette/third_party \
    native_client/src/third_party/dlmalloc \
    native_client/src/third_party/valgrind \
    net/third_party/http2 \
    net/third_party/mozilla_security_manager \
    net/third_party/nss \
    net/third_party/quic \
    net/third_party/spdy \
    third_party/node \
    third_party/adobe \
    third_party/analytics \
    third_party/angle \
    third_party/angle/src/common/third_party/base \
    third_party/angle/src/common/third_party/smhasher \
    third_party/angle/src/third_party/compiler \
    third_party/angle/src/third_party/libXNVCtrl \
    third_party/angle/src/third_party/trace_event \
    third_party/angle/third_party/glslang \
    third_party/angle/third_party/spirv-headers \
    third_party/angle/third_party/spirv-tools \
    third_party/angle/third_party/vulkan-validation-layers \
    third_party/apple_apsl \
    third_party/blanketjs \
    third_party/blink \
    third_party/boringssl \
    third_party/boringssl/src/third_party/fiat \
    third_party/breakpad \
    third_party/breakpad/breakpad/src/third_party/curl \
    third_party/brotli \
    third_party/cacheinvalidation \
    third_party/catapult \
    third_party/catapult/common/py_vulcanize/third_party/rcssmin  \
    third_party/catapult/common/py_vulcanize/third_party/rjsmin  \
    third_party/catapult/third_party/polymer \
    third_party/catapult/tracing/third_party/d3 \
    third_party/catapult/tracing/third_party/gl-matrix \
    third_party/catapult/tracing/third_party/jszip \
    third_party/catapult/tracing/third_party/mannwhitneyu \
    third_party/catapult/tracing/third_party/oboe \
    third_party/catapult/tracing/third_party/pako \
    third_party/ced \
    third_party/cld_3 \
    third_party/crashpad \
    third_party/crashpad/crashpad/third_party/zlib \
    third_party/crc32c \
    third_party/cros_system_api \
    third_party/devscripts \
    third_party/dom_distiller_js \
    third_party/expat \
    third_party/ffmpeg \
    third_party/fips181 \
    third_party/flatbuffers \
    third_party/flot \
    third_party/fontconfig \
    third_party/freetype \
    third_party/glslang-angle \
    third_party/googletest \
    third_party/google_input_tools \
    third_party/google_input_tools/third_party/closure_library \
    third_party/google_input_tools/third_party/closure_library/third_party/closure \
%if !%{with system_harfbuzz}
    third_party/harfbuzz-ng \
%endif
    third_party/hunspell \
    third_party/iccjpeg \
    third_party/inspector_protocol \
%if !%{with system_jinja2}
    third_party/jinja2 \
%endif
    third_party/jstemplate \
    third_party/khronos \
    third_party/leveldatabase \
    third_party/libaddressinput \
    third_party/libaom \
    third_party/libjingle \
    third_party/libphonenumber \
    third_party/libsecret \
    third_party/libsrtp \
    third_party/libsync \
    third_party/libudev \
    third_party/libusb \
%if !%{with system_libvpx}
    third_party/libvpx \
    third_party/libvpx/source/libvpx/third_party/googletest \
    third_party/libvpx/source/libvpx/third_party/libwebm \
    third_party/libvpx/source/libvpx/third_party/libyuv \
    third_party/libvpx/source/libvpx/third_party/x86inc \
%endif
    third_party/libwebm \
%if %{with system_libxml2}
    third_party/libxml/chromium \
%else
    third_party/libxml \
%endif
    third_party/libXNVCtrl \
    third_party/libyuv \
    third_party/lss \
    third_party/lzma_sdk \
%if !%{with system_markupsafe}
    third_party/markupsafe \
%endif
    third_party/mesa \
    third_party/metrics_proto \
    third_party/modp_b64 \
    third_party/node/node_modules/polymer-bundler/lib/third_party/UglifyJS2 \
    third_party/openh264 \
    third_party/openmax_dl \
    third_party/opus \
    third_party/ots \
    third_party/pdfium \
    third_party/pdfium/third_party/agg23 \
    third_party/pdfium/third_party/base \
    third_party/pdfium/third_party/bigint \
    third_party/pdfium/third_party/freetype \
    third_party/pdfium/third_party/lcms \
    third_party/pdfium/third_party/libopenjpeg20 \
    third_party/pdfium/third_party/libpng16 \
    third_party/pdfium/third_party/libtiff \
    third_party/pdfium/third_party/skia_shared \
    third_party/perfetto \
%if !%{with system_ply}
    third_party/ply \
%endif
    third_party/polymer \
    third_party/protobuf \
    third_party/protobuf/third_party/six \
    third_party/pyjson5 \
    third_party/qcms \
    third_party/qunit \
    third_party/rnnoise \
    third_party/s2cellid \
    third_party/sfntly \
    third_party/sinonjs \
    third_party/skia \
    third_party/skia/third_party/gif \
    third_party/skia/third_party/skcms \
    third_party/skia/third_party/vulkan \
    third_party/smhasher \
    third_party/speech-dispatcher \
    third_party/spirv-tools-angle \
    third_party/spirv-headers \
    third_party/sqlite \
    third_party/tcmalloc \
    third_party/unrar \
    third_party/usb_ids \
    third_party/usrsctp \
    third_party/vulkan \
    third_party/vulkan-validation-layers \
    third_party/web-animations-js \
    third_party/webdriver \
    third_party/WebKit \
    third_party/webrtc \
    third_party/widevine \
    third_party/woff2 \
    third_party/xdg-utils \
    third_party/yasm/run_yasm.py \
    third_party/zlib/google \
    url/third_party/mozilla \
    v8/src/third_party/valgrind \
    v8/third_party/antlr4 \
    v8/third_party/inspector_protocol



python2 build/linux/unbundle/replace_gn_files.py --system-libraries \
    flac \
    freetype \
    fontconfig \
    libdrm \
%if %{with system_harfbuzz}
    harfbuzz-ng \
%endif
    libjpeg \
    libpng \
    libwebp \
%if %{with system_libxml2}
    libxml \
%endif
    libxslt \
    re2 \
    snappy \
    yasm \
    zlib


# Fix usb.ids location
sed -i 's|//third_party/usb_ids|/usr/share/hwdata|g' device/usb/BUILD.gn

# Fix references to ninja
sed -i "s|'ninja'|'ninja-build'|" tools/gn/bootstrap/bootstrap.py
sed -i 's|//third_party/usb_ids|/usr/share/hwdata|g' device/usb/BUILD.gn

# Don't use static libstdc++
sed -i '/-static-libstdc++/d' tools/gn/build/gen.py

%if %{with system_jinja2}
rmdir third_party/jinja2
ln -s %{python2_sitelib}/jinja2 third_party/jinja2
%endif

%if %{with system_ply}
rmdir third_party/ply
ln -s %{python2_sitelib}/ply third_party/ply
%endif

# Hard code extra version
FILE=chrome/common/channel_info_posix.cc
sed -i.orig -e 's/getenv("CHROME_VERSION_EXTRA")/"FedBerry"/' $FILE


%build
cd %{_builddir}/chromium-%{version}/

%if %{with clang}
export CC=clang CXX=clang++
%endif
export AR=ar NM=nm
export PNACLPYTHON=%{__python2}


_flags+=(
    'enable_google_now=false'
    'enable_hangout_services_extension=true'
    'enable_iterator_debugging=false'
    'enable_nacl=false'
    'enable_nacl_nonsfi=false'
    'enable_swiftshader=false'
    'enable_vulkan=false'
    'enable_wayland_server=false'
    'enable_widevine=true'
    'fatal_linker_warnings=false'
    'ffmpeg_branding="Chrome"'
    'fieldtrial_testing_like_official_build=true'
    'google_api_key="AIzaSyCkfPOPZXDKNn8hhgu3JrA62wIgC93d44k"'
    'google_default_client_id="811574891467.apps.googleusercontent.com"'
    'google_default_client_secret="kdloedMFGdGla2P1zacGjAQh"'
    'is_debug=false'
    'is_desktop_linux=true'
    'is_component_build=false'
    'is_official_build=true'
    'linux_use_bundled_binutils=false'
    'proprietary_codecs=true'
    'remove_webcore_debug_symbols=true'
    'symbol_level=0'
    'treat_warnings_as_errors=false'
    'use_allocator="none"'
    'use_alsa=true'
    'use_cups=true'
    'use_custom_libcxx=false'
    'use_dbus=true'
    'use_gnome_keyring=false'
    'use_gold=false'
    'use_ozone=false'
    'use_pulseaudio=false'
    'use_sysroot=false'
    'use_system_freetype=true'
%if %{with system_harfbuzz}
    'use_system_harfbuzz=true'
%endif
%ifarch x86_64
    'system_libdir="lib64"'
%endif
%ifnarch x86_64
    'target_extra_ldflags="-Wl,--no-keep-memory -Wl,--reduce-memory-overheads"'
%endif
%ifarch armv7hl
    'target_cpu="arm"'
    'arm_arch="armv7-a"'
    'arm_float_abi="hard"'
    'arm_optionally_use_neon=false'
    'arm_use_neon=true'
    'arm_use_thumb=true'
    'arm_version=7'
    'use_libpci=false'
%endif
%if %{with clang}
    'is_clang=true'
    'clang_base_path="/usr"'
    'clang_use_chrome_plugins=false'
%else
    'is_clang=false'
    'target_extra_cxxflags="-fno-delete-null-pointer-checks"'
    'target_extra_cflags="-fno-delete-null-pointer-checks"'
%endif
%if %{with _gtk3}
    'use_gtk3=true'
%else
    'use_glib=true'
    'use_gio=true'
    'use_gtk3=false'
%endif
%if %{with jumbo_unity}
    'use_jumbo_build=true'
    'jumbo_file_merge_limit=10'
%endif
)

# fix arm gcc
%ifarch armv7hl
sed -i 's|arm-linux-gnueabihf-||g' build/toolchain/linux/BUILD.gn
%endif

python2 tools/gn/bootstrap/bootstrap.py -vv --gn-gen-args "${_flags[*]}"

./out/Release/gn gen --script-executable=/usr/bin/python2 --args="${_flags[*]}" out/Release

# Set jobs to number of cores less 1
jobs=$(expr $(grep -c ^processor /proc/cpuinfo))

%if %{with devel_tools}
%__ninja -C out/Release -vv chrome chrome_sandbox chromedriver -j$jobs
%else
%__ninja -C out/Release -vv chrome -j$jobs
%endif

%if %{with remote_desktop}
%__ninja -C out/Release -vv remoting_all -j$jobs
%endif


%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{chromiumdir}/locales
mkdir -p %{buildroot}%{_mandir}/man1
mkdir -p %{buildroot}%{_datadir}/appdata
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/gnome-control-center/default-apps
sed -e "s|@LIBDIR@|%{_libdir}|" -e "s|@@BUILDTARGET@@|`cat /etc/redhat-release`|" \
%{SOURCE10} > chromium-wrapper
install -m 755 chromium-wrapper %{buildroot}%{_bindir}/%{name}-browser
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE11}
install -m 644 %{SOURCE12} %{buildroot}%{_datadir}/gnome-control-center/default-apps/
appstream-util validate-relax --nonet %{SOURCE13}
install -m 644 %{SOURCE13} %{buildroot}%{_datadir}/appdata/
sed -e "s|@@MENUNAME@@|Chromium|g" -e "s|@@PACKAGE@@|chromium|g" \
chrome/app/resources/manpage.1.in > chrome.1
install -m 644 chrome.1 %{buildroot}%{_mandir}/man1/%{name}-browser.1
install -m 755 out/Release/chrome %{buildroot}%{chromiumdir}/chromium

%if %{with devel_tools}
install -m 4755 out/Release/chrome_sandbox %{buildroot}%{chromiumdir}/chrome-sandbox
install -m 755 out/Release/chromedriver %{buildroot}%{chromiumdir}/
ln -s %{chromiumdir}/chromedriver %{buildroot}%{_bindir}/%{name}-chromedriver
%endif

install -m 644 out/Release/icudtl.dat %{buildroot}%{chromiumdir}/
install -m 644 out/Release/*.bin %{buildroot}%{chromiumdir}/
install -m 644 out/Release/*.pak %{buildroot}%{chromiumdir}/
install -m 644 out/Release/*.so %{buildroot}%{chromiumdir}/
install -m 644 out/Release/locales/*.pak %{buildroot}%{chromiumdir}/locales/
for i in 16 32; do
    mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps
    install -m 644 chrome/app/theme/default_100_percent/chromium/product_logo_$i.png \
    %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/chromium.png
done
for i in 22 24 32 48 64 128 256; do
    if [ ${i} = 32 ]; then ext=xpm; else ext=png; fi
    if [ ${i} = 32 ]; then dir=linux/; else dir=; fi
    mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps
    install -m 644 chrome/app/theme/chromium/${dir}product_logo_$i.${ext} \
    %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/chromium.${ext}
done

mkdir -p %{buildroot}/%{chromiumdir}/PepperFlash

%if %{with remote_desktop}
# Remote desktop bits
mkdir -p %{buildroot}%{crd_path}

pushd %{buildroot}%{crd_path}
ln -s %{_libdir}/%{name} lib
popd

# See remoting/host/installer/linux/Makefile for logic
cp -a out/Release/remoting_native_messaging_host %{buildroot}%{crd_path}/remoting_native_messaging_host
cp -a out/Release/remote_assistance_host %{buildroot}%{crd_path}/remote-assistance-host
cp -a out/Release/remoting_locales %{buildroot}%{crd_path}/
cp -a out/Release/remoting_me2me_host %{buildroot}%{crd_path}/chrome-remote-desktop-host
cp -a out/Release/remoting_start_host %{buildroot}%{crd_path}/start-host
cp -a out/Release/remoting_user_session %{buildroot}%{crd_path}/user-session

# chromium
mkdir -p %{buildroot}%{_sysconfdir}/chromium/remoting_native_messaging_host

# google-chrome
mkdir -p %{buildroot}%{_sysconfdir}/opt/chrome/
cp -a out/Release/remoting/* %{buildroot}%{_sysconfdir}/chromium/remoting_native_messaging_host/

for i in %{buildroot}%{_sysconfdir}/chromium/remoting_native_messaging_host/*.json; do
    sed -i 's|/opt/google/chrome-remote-desktop|%{crd_path}|g' $i
done

pushd %{buildroot}%{_sysconfdir}/opt/chrome/
ln -s ../../chromium/remoting_native_messaging_host remoting_native_messaging_host
popd

mkdir -p %{buildroot}/var/lib/chrome-remote-desktop
touch %{buildroot}/var/lib/chrome-remote-desktop/hashes

mkdir -p %{buildroot}%{_sysconfdir}/pam.d/
pushd %{buildroot}%{_sysconfdir}/pam.d/
ln -s system-auth chrome-remote-desktop
popd

cp -a remoting/host/linux/linux_me2me_host.py %{buildroot}%{crd_path}/chrome-remote-desktop
cp -a remoting/host/installer/linux/is-remoting-session %{buildroot}%{crd_path}/

mkdir -p %{buildroot}%{_unitdir}
cp -a %{SOURCE2} %{buildroot}%{_unitdir}/
sed -i 's|@@CRD_PATH@@|%{crd_path}|g' %{buildroot}%{_unitdir}/chrome-remote-desktop.service
%endif


%post
update-desktop-database &> /dev/null || :

%postun
update-desktop-database &> /dev/null || :


%if %{with remote_desktop}
%pre -n chrome-remote-desktop
getent group chrome-remote-desktop >/dev/null || groupadd -r chrome-remote-desktop

%post -n chrome-remote-desktop
%systemd_post chrome-remote-desktop.service

%preun -n chrome-remote-desktop
%systemd_preun chrome-remote-desktop.service

%postun -n chrome-remote-desktop
%systemd_postun_with_restart chrome-remote-desktop.service
%endif


%files
%license LICENSE
%doc AUTHORS
%{_bindir}/%{name}-browser
%{_datadir}/appdata/%{name}-browser.appdata.xml
%{_datadir}/applications/%{name}-browser.desktop
%{_datadir}/gnome-control-center/default-apps/%{name}-browser.xml
%{_datadir}/icons/hicolor/16x16/apps/chromium.png
%{_datadir}/icons/hicolor/22x22/apps/chromium.png
%{_datadir}/icons/hicolor/24x24/apps/chromium.png
%{_datadir}/icons/hicolor/32x32/apps/chromium.png
%{_datadir}/icons/hicolor/32x32/apps/chromium.xpm
%{_datadir}/icons/hicolor/48x48/apps/chromium.png
%{_datadir}/icons/hicolor/64x64/apps/chromium.png
%{_datadir}/icons/hicolor/128x128/apps/chromium.png
%{_datadir}/icons/hicolor/256x256/apps/chromium.png
%{_mandir}/man1/%{name}-browser.1.gz
%dir %{chromiumdir}
%dir %{chromiumdir}/PepperFlash/
%{chromiumdir}/chromium
%if %{with devel_tools}
%{chromiumdir}/chromedriver
%{chromiumdir}/chrome-sandbox
%endif
%if !%{with system_libicu}
%{chromiumdir}/icudtl.dat
%endif
%{chromiumdir}/*.bin
%{chromiumdir}/*.pak
%dir %{chromiumdir}/locales
%{chromiumdir}/locales/*.pak


%files libs
%{chromiumdir}/lib*.so*
%exclude %{chromiumdir}/libwidevinecdm.so
%exclude %{chromiumdir}/libwidevinecdmadapter.so


%if %{with devel_tools}
%files chromedriver
%{_bindir}/%{name}-chromedriver
%{chromiumdir}/chromedriver
%endif


%if %{with remote_desktop}
%files -n chrome-remote-desktop
%{crd_path}/chrome-remote-desktop
%{crd_path}/chrome-remote-desktop-host
%{crd_path}/is-remoting-session
%{crd_path}/lib
%{crd_path}/remoting_native_messaging_host
%{crd_path}/remote-assistance-host
%{_sysconfdir}/pam.d/chrome-remote-desktop
%{_sysconfdir}/chromium/remoting_native_messaging_host/
%{_sysconfdir}/opt/chrome/
%{crd_path}/remoting_locales/
%{crd_path}/start-host
%{crd_path}/user-session
%{_unitdir}/chrome-remote-desktop.service
/var/lib/chrome-remote-desktop/
%endif


%changelog
* Sun Jun 24 2018 Vaughan Agrez <devel at agrez dot net> 65.0.3325.181-3
- Update chromium-wrapper
- Enable mmal hardware acceleration for RPi's (Patch5)
- Update GN args: 'arm_use_neon=true' & 'jumbo_file_merge_limit=10'
- Add GN args: 'is_desktop_linux=true' & 'is_official_build=true'
- Change master_preferences path (Patch3)
- Update %%post scripts

* Fri Apr 13 2018 Vaughan Agrez <devel at agrez dot net> 65.0.3325.181-2
- Use system freetype / fontconfig
- Misc python fixes

* Thu Apr 05 2018 Vaughan Agrez <devel at agrez dot net> 65.0.3325.181-1
- Update to 65.0.3325.181 release
- Update/refactor patches
- Udate GN args
- Disable pulseaudio support (for the moment)

* Wed Mar 14 2018 Vaughan Agrez <devel at agrez dot net> 64.0.3282.140-1
- Update to 64.0.3282.140 release
- Update patches
- Ensure python2 is used
- Enable Jumbo / Unity builds
- Add/use %%global majorversion
- Re-enable i686 build support
- Fix install of man page

* Wed Dec 27 2017 Vaughan Agrez <devel at agrez dot net> 63.0.3239.108-1
- Update to 63.0.3239.108
- Drop Sources 1, 3 & 4 (we don't use / need them)
- Add, drop, refactor patches
- Update provides/requires
- Remove unsupported system clang/lld flags
- Disable debug package
- Don't split out ffmpeg lib
- Update build conditionals
- Update bundle/unbundled libs
- Export system AR NM & LDFLAGS
- Try to disable wayland support
- Update chromium build flags/switches

* Sat Aug 05 2017 Vaughan Agrez <devel at agrez dot net> 60.0.3112.90-1
- Update to 60.0.3112.90
- Drop patch21 (fixed upstream)

* Thu Aug 03 2017 Vaughan Agrez <devel at agrez dot net> 60.0.3112.78-1
- Update to 60.0.3112.78
- Resurrect x86_64 build support for testing (RPi is too slow)
- Update Requires & Provides excludes for private libs
- Update gcc7 fixes (patches 11-13)
- Rename/refactor parallel/bootstrap/buildflags patches
- Add fix for freetype rendering (patch21)
- Fix gtk2 build (patch22)
- Increase build verbosity

* Sat Jun 03 2017 Vaughan Agrez <devel at agrez dot net> 58.0.3029.140-2
- Fix icon name in desktop file

* Tue May 30 2017 Vaughan Agrez <devel at agrez dot net> 58.0.3029.140-1
- Import (from UnitedRpms) and rename package
- Update to 58.0.3029.140
- Add arm build support
- Remove x86 specific support (spec is armv7l only)
- Default to building with clang
- Drop -fno-delete-null-pointer-checks patch (we use clang)
- Add patches 20-22
- Refactor GN build flags
- As per SUSE's request, don't use their chromium api keys
- Drop gn_binaries source
- Strip .git dir from depot_tools source
- Add/fix requires & provides excludes for private libs
- Misc spec refactoring and cleanups

* Sat Apr 08 2017 - David Vasquez <davidjeremias82 AT gmail DOT com>  57.0.2987.133-2
- Updated to 57.0.2987.133

* Tue Mar 28 2017 - David Vasquez <davidjeremias82 AT gmail DOT com>  57.0.2987.98-2
- Updated to 57.0.2987.110

* Fri Mar 10 2017 - David Vasquez <davidjeremias82 AT gmail DOT com>  57.0.2987.98-2
- Updated to 57.0.2987.98-2

* Thu Mar 02 2017 - David Vasquez <davidjeremias82 AT gmail DOT com>  56.0.2924.87-4
- Fix issue with compilation on gcc7, Thanks to Ben Noordhuis

* Mon Feb 06 2017 - David Vasquez <davidjeremias82 AT gmail DOT com>  56.0.2924.87-2
- Updated to 56.0.2924.87

* Thu Jan 26 2017 - David Vasquez <davidjeremias82 AT gmail DOT com>  56.0.2924.76-2
- Updated to 56.0.2924.76
- Renamed to chromium-freeworld

* Sun Dec 18 2016 - David Vasquez <davidjeremias82 AT gmail DOT com>  55.0.2883.87-2
- Updated to 55.0.2883.87

* Fri Dec 02 2016 - David Vasquez <davidjeremias82 AT gmail DOT com>  55.0.2883.75-2
- Updated to 55.0.2883.75

* Thu Dec 01 2016 - David Vasquez <davidjeremias82 AT gmail DOT com>  54.0.2840.100-3
- Conditional task

* Sat Nov 12 2016 - David Vasquez <davidjeremias82 AT gmail DOT com>  54.0.2840.100-2
- Updated to 54.0.2840.100

* Mon Nov 07 2016 - David Vasquez <davidjeremias82 AT gmail DOT com>  54.0.2840.90-2
- Updated to 54.0.2840.90

* Mon Oct 31 2016 - David Vasquez <davidjeremias82 AT gmail DOT com>  54.0.2840.71-3
- Initial build
