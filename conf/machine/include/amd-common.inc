PREFERRED_VERSION_linux-yocto ??= "6.12%"
PREFERRED_VERSION_linux-yocto-rt ??= "6.12%"
PREFERRED_PROVIDER_virtual/kernel ??= "amd-linux-tiny"

PREFERRED_PROVIDER_jpeg ?= "jpeg"
PREFERRED_PROVIDER_jpeg-native ?= "jpeg-native"

AMD_ESSENTIAL_EXTRA_RDEPENDS ?= ""

# QEMU does not support some of the enhanced instructions available
# on the AMD chips which causes some build time failures.
MACHINE_FEATURES:remove = "qemu-usermode"
MACHINE_FEATURES += "efi"
MACHINE_EXTRA_RRECOMMENDS += "${KERNEL_PACKAGE_NAME}-modules alsa-utils grub"
MACHINE_ESSENTIAL_EXTRA_RDEPENDS = "linux-firmware-amdgpu ${AMD_ESSENTIAL_EXTRA_RDEPENDS}"

XSERVER ?= "\
    xserver-xorg \
    xf86-input-evdev \
    xf86-video-amdgpu \
    ${@bb.utils.contains('DISTRO_FEATURES', 'opengl', 'xserver-xorg-extension-glx', '', d)} \
    "

INITRAMFS_FSTYPE ?= "cpio.xz"

KERNEL_IMAGETYPE = "bzImage"
