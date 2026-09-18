# Mostly just a copy of what's in OE-core

SUMMARY = "Linux kernel"
SECTION = "kernel"
LICENSE = "GPL-2.0-with-Linux-syscall-note"
HOMEPAGE = "https://www.yoctoproject.org/"

LIC_FILES_CHKSUM ?= "file://COPYING;md5=6bc538ed5bd9a7fc9398086aedcd7e46"

UPSTREAM_CHECK_GITTAGREGEX = "(?P<pver>\d+\.\d+(\.\d+)*)"

RECIPE_NO_UPDATE_REASON = "Recipe is updated through a separate process"

KMETA ?= "amd-meta"
KERNEL_DEBUG ?= "False"
KPROTOCOL ?= "protocol=https"
KBRANCH ?= "tag=v${PV};mindepth=1;nobranch=1"
LINUX_VERSION_EXTENSION ?= "-amd-${LINUX_KERNEL_TYPE}"
AMD_KERNEL_CACHE_URI ?= "git://github.com/under-view/amd-kernel-cache.git;protocol=https;branch=master"
KSRC ?= "git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"
SRCREV_amdmeta ?= "49518b0b5d40c74a26265a779c0a5b5d05ed5d30"

PV = "${LINUX_VERSION}"
PV_MAJOR_MINOR = "${@'.'.join(d.getVar('PV').split('.')[:2])}"

SRC_URI = "\
    ${KSRC};${KPROTOCOL};${KBRANCH};name=machine \
    ${AMD_KERNEL_CACHE_URI};name=amdmeta;type=kmeta;destsuffix=${KMETA} \
    "

AMD_KERNEL_FEATURES ?= "\
    amdx64-generic.scc \
    disk.scc \
    console.scc \
    ${@bb.utils.contains('DISTRO_FEATURES', 'systemd', 'systemd.scc', '', d)} \
    ${@bb.utils.contains('INITRAMFS_IMAGE_BUNDLE', '1', 'initramfs-liveusb.scc', '', d)} \
    "

KERNEL_FEATURES = "${@' '.join(['linux-'+d.getVar('PV_MAJOR_MINOR')+'/features/'+feat for feat in d.getVar('AMD_KERNEL_FEATURES').split()])}"

# These used to be version specific, but are now common dependencies.  New
# tools / dependencies will continue to be added in version specific recipes.
DEPENDS += '${@bb.utils.contains_any("ARCH", [ "x86", "arm64", "powerpc" ], "elfutils-native", "", d)}'
DEPENDS += "openssl-native util-linux-native"
DEPENDS += "gmp-native libmpc-native"
DEPENDS += "xz-native bc-native"

inherit kernel
inherit kernel-yocto

B = "${WORKDIR}/linux-${PACKAGE_ARCH}-${LINUX_KERNEL_TYPE}-build"

do_install:append(){
	if [ -n "${KMETA}" ]; then
		rm -rf ${STAGING_KERNEL_DIR}/${KMETA}
	fi
}

# Some options depend on CONFIG_PAHOLE_VERSION, so need to make pahole-native available before do_kernel_configme
do_kernel_configme[depends] += '${@bb.utils.contains("KERNEL_DEBUG", "True", "pahole-native:do_populate_sysroot", "", d)}'

EXTRA_OEMAKE += '${@bb.utils.contains("KERNEL_DEBUG", "True", "", "PAHOLE=false", d)}'

COMPATIBLE_MACHINE = "${MACHINE}"

KERNEL_VERSION_SANITY_SKIP ?= "1"

LINUX_KERNEL_TYPE = "tiny"
KCONFIG_MODE = "--allnoconfig"
KBUILD_DEFCONFIG = "tiny.config"

do_devshell:prepend() {
    # setup native pkg-config variables (kconfig scripts call pkg-config directly, cannot generically be overriden to pkg-config-native)
    d.setVar("PKG_CONFIG_DIR", "${STAGING_DIR_NATIVE}${libdir_native}/pkgconfig")
    d.setVar("PKG_CONFIG_PATH", "${PKG_CONFIG_DIR}:${STAGING_DATADIR_NATIVE}/pkgconfig")
    d.setVar("PKG_CONFIG_LIBDIR", "${PKG_CONFIG_DIR}")
    d.setVarFlag("PKG_CONFIG_SYSROOT_DIR", "unexport", "1")
    d.appendVar("OE_TERMINAL_EXPORTS", " PKG_CONFIG_DIR PKG_CONFIG_PATH PKG_CONFIG_LIBDIR PKG_CONFIG_SYSROOT_DIR")
}
