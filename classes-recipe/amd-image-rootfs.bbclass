IMAGE_FSTYPE = "ext4"

DESCRIPTION = "Minimal rootfs image"
LICENSE = "MIT"

AMD_INSTALL ??= ""

PACKAGE_INSTALL = "\
    ${VIRTUAL-RUNTIME_base-utils} \
    ${VIRTUAL-RUNTIME_dev_manager} \
    ${ROOTFS_BOOTSTRAP_INSTALL} \
    ${AMD_INSTALL} \
    "

AUTO_LOGIN_ROOT ?= "0"

AUTO_LOGIN_FEATS = "\
    serial-autologin-root \
    empty-root-password \
    allow-empty-password \
    allow-root-login \
    "

IMAGE_FEATURES = "${@bb.utils.contains('AUTO_LOGIN_ROOT', '1', '${AUTO_LOGIN_FEATS}', '', d)}"
IMAGE_LINGUAS = ""

COPY_LIC_MANIFEST = "0"
COPY_LIC_DIRS = "0"

KERNELDEPMODDEPEND = ""

INITRAMFS_MAXSIZE = "0"

IMAGE_NAME_SUFFIX = ""

# rootfs size in kilobytes
# max 524288KB -> 512MB
IMAGE_ROOTFS_SIZE ?= "524288"
IMAGE_ROOTFS_EXTRA_SPACE ?= "0"

FORCE_RO_REMOVE ?= "1"

inherit image

IMAGE_FSTYPES = "${IMAGE_FSTYPE}"

IMAGE_POSTPROCESS_COMMAND = ""
