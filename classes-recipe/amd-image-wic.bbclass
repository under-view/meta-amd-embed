SUMMARY = "Building WIC Images"

LICENSE = "MIT"

inherit image

AMD_IMAGE_DEPENDS ?= ""

INITRAMFS_MAXSIZE = ""
IMAGE_NAME_SUFFIX = ""
IMAGE_ROOTFS_SIZE = "0"
IMAGE_ROOTFS_EXTRA_SPACE = "0"
IMAGE_POSTPROCESS_COMMAND = ""

IMAGE_FSTYPES = "wic wic.gz wic.bmap"

do_rootfs() {
    :
}

do_image_wic[vardeps] += "\
    AMD_IMAGE_DEPENDS \
    ${WICVARS} \
    "

do_image_wic[depends] += "\
    grub-native:do_populate_sysroot \
    grub:do_populate_sysroot \
    grub-efi:do_populate_sysroot \
    ${@' '.join([image + ':do_image_complete' for image in d.getVar('AMD_IMAGE_DEPENDS').split()])} \
    "
