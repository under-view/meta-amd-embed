AMD_ARTIFACTS_DIR ?= "${TMPDIR}/../build-artifacts"
AMD_ARTIFACTS_PN_DIR ?= "${AMD_ARTIFACTS_DIR}/${PN}"

gen_build_artifact_dir() {
    local wic_path="${DEPLOY_DIR_IMAGE}/${PN}-${MACHINE}.wic"

    mkdir -p "${AMD_ARTIFACTS_PN_DIR}"

    ln --relative -sf "${wic_path}.gz" "${AMD_ARTIFACTS_PN_DIR}"
    ln --relative -sf "${wic_path}.bmap" "${AMD_ARTIFACTS_PN_DIR}"
}

IMAGE_POSTPROCESS_COMMAND:append = " gen_build_artifact_dir;"
