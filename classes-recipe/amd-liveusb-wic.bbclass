inherit amd-image-wic

LIVEUSB_SPLASH ??= ""
LIVEUSB_CONSOLE ??= ""
LIVEUSB_INSTALL ??= ""
LIVEUSB_INITRAMFS ??= "0"
LIVEUSB_KERNEL_ARGS ??= "rootwait"

WICVARS:append = "\
    LIVEUSB_SPLASH \
    LIVEUSB_CONSOLE \
    LIVEUSB_INSTALL \
    LIVEUSB_INITRAMFS \
    LIVEUSB_KERNEL_ARGS \
    AMD_ARTIFACTS_DIR \
    "

do_image_wic[depends] += "dosfstools-native:do_populate_sysroot \
                          mtools-native:do_populate_sysroot \
                          cdrtools-native:do_populate_sysroot \
                          syslinux-native:do_populate_sysroot \
                          ${MLPREFIX}syslinux:do_populate_sysroot \
                          "
