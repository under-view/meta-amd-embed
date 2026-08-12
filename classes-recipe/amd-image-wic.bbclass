SUMMARY = "Building WIC Images"

LICENSE = "MIT"

inherit core-image

INITRAMFS_MAXSIZE = ""
IMAGE_NAME_SUFFIX = ""
IMAGE_ROOTFS_SIZE = "0"
IMAGE_ROOTFS_EXTRA_SPACE = "0"
IMAGE_POSTPROCESS_COMMAND = ""

IMAGE_FSTYPES = "wic wic.gz wic.bmap"

do_rootfs() {
    :
}

do_image_wic[depends] += "\
    grub-native:do_populate_sysroot \
    grub:do_populate_sysroot \
    grub-efi:do_populate_sysroot \
    "
