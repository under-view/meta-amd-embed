PREFERRED_VERSION_linux-yocto ?= "6.12%"
PREFERRED_VERSION_linux-yocto-rt ?= "6.12%"
PREFERRED_PROVIDER_virtual/kernel ?= "amd-linux-tiny"

PREFERRED_PROVIDER_jpeg ?= "jpeg"
PREFERRED_PROVIDER_jpeg-native ?= "jpeg-native"

ACPI_DEBUG ?= "0"
ACPI_DEBUG_KERNEL_ARGS ?= "log_buf_len=16M acpi.debug_layer=0x00000002 acpi.debug_level=0x00000004"

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
