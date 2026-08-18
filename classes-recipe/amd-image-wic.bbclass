SUMMARY = "Building WIC Images"

LICENSE = "MIT"

inherit image nospdx amd-artifacts-dir

AMD_IMAGE_DEPENDS ?= ""

IMAGE_INSTALL = ""
IMAGE_LINGUAS = ""
IMAGE_FEATURES = ""
DISTRO_FEATURES = ""
SDKIMAGE_FEATURES = ""
INITRAMFS_MAXSIZE = ""
IMAGE_NAME_SUFFIX = ""
IMAGE_ROOTFS_SIZE = "0"
IMAGE_ROOTFS_EXTRA_SPACE = "0"
IMAGE_POSTPROCESS_COMMAND = ""
IMAGE_PREPROCESS_COMMAND:remove = "reproducible_final_image_task"

IMAGE_FSTYPES = "wic wic.gz wic.bmap"

do_rootfs() {
    :
}

do_create_image_spdx[noexec] = "1"
do_create_rootfs_spdx[noexec] = "1"
do_create_image_sbom_spdx[noexec] = "1"

do_image_wic[vardeps] += "\
    ${WICVARS} \
    AMD_IMAGE_DEPENDS \
    "

do_image_wic[depends] += "\
    grub-native:do_populate_sysroot \
    grub:do_populate_sysroot \
    grub-efi:do_populate_sysroot \
    util-linux-native:do_populate_sysroot \
    ${@' '.join([image + ':do_image_complete' for image in d.getVar('AMD_IMAGE_DEPENDS').split()])} \
    "

WKS_FILE_DEPENDS_BOOTLOADERS:remove = "systemd-boot"
