inherit amd-image-wic

LIVEUSB_CONSOLE ??= ""
LIVEUSB_INSTALL ??= ""
LIVEUSB_INITRAMFS ??= "0"

WICVARS:append = "\
    LIVEUSB_INITRAMFS \
    LIVEUSB_CONSOLE \
    LIVEUSB_INSTALL \
    AMD_ARTIFACTS_DIR \
    "

do_image_wic[depends] += "dosfstools-native:do_populate_sysroot \
                          mtools-native:do_populate_sysroot \
                          cdrtools-native:do_populate_sysroot \
                          syslinux-native:do_populate_sysroot \
                          ${MLPREFIX}syslinux:do_populate_sysroot \
                          "
