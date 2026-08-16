AMD_ARTIFACTS_DIR ?= "${TMPDIR}/../build-artifacts"
AMD_ARTIFACTS_PN_DIR ?= "${AMD_ARTIFACTS_DIR}/${PN}"

gen_build_artifact_dir() {
    local wic_path="${DEPLOY_DIR_IMAGE}/${PN}-${MACHINE}.wic"

    mkdir -p "${AMD_ARTIFACTS_PN_DIR}"

    ln --relative -sf "${wic_path}.gz" "${AMD_ARTIFACTS_PN_DIR}"
    ln --relative -sf "${wic_path}.bmap" "${AMD_ARTIFACTS_PN_DIR}"
}

IMAGE_POSTPROCESS_COMMAND:append = " gen_build_artifact_dir;"

# Define your custom post-processing cleanup function
python clean_build_artifact_dir() {
    import os
    import shutil

    artifacts_pn_dir = d.getVar('AMD_ARTIFACTS_PN_DIR')
    if os.path.exists(artifacts_pn_dir):
        shutil.rmtree(artifacts_pn_dir)

    artifacts_dir = d.getVar('AMD_ARTIFACTS_DIR')
    if len(os.listdir(artifacts_dir)) == 0:
        os.rmdir(artifacts_dir)
}

# Add python execution to the clean sequence
clean_custom_image_dirs[deptask] = ""
do_clean[postfuncs] += "clean_build_artifact_dir"
