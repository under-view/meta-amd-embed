inherit amd-image-wic

LIVEUSB_SPLASH ??= ""
LIVEUSB_CONSOLE ??= ""
LIVEUSB_INSTALL ??= ""
LIVEUSB_INITRAMFS ??= "0"
LIVEUSB_GRUB_KERNEL_ARGS ??= "console=tty1 console=ttyS0,115200n8"
LIVEUSB_SYSLINUX_KERNEL_ARGS ??= "console=tty1 console=ttyS0,115200n8"

WICVARS:append = "\
    LIVEUSB_SPLASH \
    LIVEUSB_CONSOLE \
    LIVEUSB_INSTALL \
    LIVEUSB_INITRAMFS \
    LIVEUSB_GRUB_KERNEL_ARGS \
    LIVEUSB_SYSLINUX_KERNEL_ARGS \
    AMD_ARTIFACTS_DIR \
    "

do_image_wic[depends] += "dosfstools-native:do_populate_sysroot \
                          mtools-native:do_populate_sysroot \
                          cdrtools-native:do_populate_sysroot \
                          syslinux-native:do_populate_sysroot \
                          ${MLPREFIX}syslinux:do_populate_sysroot \
                          "
