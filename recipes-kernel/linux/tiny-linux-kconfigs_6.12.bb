SUMMARY = "Clones and copies repo that stores all kernel Kconfig symbols"
HOMEPAGE = "https://github.com/under-view/tiny-linux-kconfigs"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=e3bf24f6d9404087a466a27410dc3b66"

SRC_URI = "git://git@github.com/under-view/tiny-linux-kconfigs.git;protocol=https;branch=master"
SRCREV ?= "71bfcc0ba65c20e941fc64ec1f93c24a71c7e25e"

S = "${UNPACKDIR}/${BPN}-${PV}"

do_install() {
    install -d ${D}${datadir}/linux-cfgs
    cp -r ${S}/linux-${PV}/* ${D}${datadir}/linux-cfgs
}

BBCLASSEXTEND += "native"
