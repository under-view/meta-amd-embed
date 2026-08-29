#
# Copyright Underview Contributors
#
# SPDX-License-Identifier: GPL-2.0-only
#
# DESCRIPTION
# This implements the 'liveusb_isohybrid' source plugin class for 'wic'
# Searches for most files in deploy directory of a given MACHINE.
#
# AUTHORS
# Vincent Davis Jr <vince (at] underview.tech>
#
# Based on oe-core isoimage-isohybrid

import glob
import logging
import sys
import os
import re
import shutil

from wic import WicError
from wic.engine import get_custom_config
from wic.pluginbase import SourcePlugin
from wic.misc import exec_cmd, exec_native_cmd, get_bitbake_var

logger = logging.getLogger('wic')
#handler = logging.StreamHandler(stream=sys.stdout)
#logger.addHandler(handler)
#logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)

class LiveusbIsohybrid(SourcePlugin):
    """
    Create a bootable ISO image

    This plugin creates a hybrid, legacy and EFI bootable ISO image. The
    generated image can be used on optical media as well as USB media.

    Legacy boot uses syslinux and EFI boot uses grub or gummiboot (not
    implemented yet) as bootloader. The plugin creates the directories required
    by bootloaders and populates them by creating and configuring the
    bootloader files.

    Example kickstart file:
    part /boot --label LIVEUSB --source liveusb_isohybrid --sourceparams="loaders=grub-efi|syslinux"

    NOT FULLY SUPPORTED YET
    part /boot --label LIVEUSB --source liveusb_isohybrid --sourceparams="loaders=grub|grub-efi"

    ###### Variables ######

    # Set variable to 1 if initramfs
    LIVEUSB_INITRAMFS = '1'
    LIVEUSB_SPLASH = "amd.jpg"
    LIVEUSB_GRUB_KERNEL_ARGS = "${KERNEL_ARGS}"
    LIVEUSB_SYSLINUX_KERNEL_ARGS = "${KERNEL_ARGS}"
    # Can be kernel + initramfs or kernel + initrd
    LIVEUSB_CONSOLE = 'bzImage-initramfs-console-${MACHINE}.bin'
    LIVEUSB_INSTALL = 'bzImage-initramfs-install-${MACHINE}.bin'
    """

    name = 'liveusb_isohybrid'

    @staticmethod
    def _install_isolinux_cfg(isolinux_dir, liveusb_splash,
                              kernel_dir, bootloader):
        kernel = ''
        kernel_args = ''

        liveusb_console = get_bitbake_var("LIVEUSB_CONSOLE")
        liveusb_install = get_bitbake_var("LIVEUSB_INSTALL")
        liveusb_initramfs = get_bitbake_var("LIVEUSB_INITRAMFS")
        amd_artifacts_dir = get_bitbake_var('AMD_ARTIFACTS_DIR')

        if get_bitbake_var('LIVEUSB_SYSLINUX_KERNEL_ARGS'):
            kernel_args = get_bitbake_var('LIVEUSB_SYSLINUX_KERNEL_ARGS')

        kernel = "console" if liveusb_initramfs == '1' else get_bitbake_var("KERNEL_IMAGETYPE")

        isolinux_cfg = open("%s/isolinux.cfg" % isolinux_dir, "w", encoding="utf-8")

        isolinux_cfg.write("serial 0 115200\n")
        isolinux_cfg.write("timeout %s\n\n" % (bootloader.timeout or 50))
        isolinux_cfg.write("menu title Liveusb\n\n")
        isolinux_cfg.write("promt 0\n\n")
        isolinux_cfg.write("default console\n\n")

        if liveusb_splash:
            isolinux_cfg.write("ui vesamenu.c32\n")
            isolinux_cfg.write("menu background amd.jpg\n\n")
        else:
            isolinux_cfg.write("ui menu.c32\n")

        if liveusb_console:
            isolinux_cfg.write("label console\n")
            isolinux_cfg.write("\tmenu label console\n")
            isolinux_cfg.write("\tmenu default\n")
            isolinux_cfg.write("\tkernel /%s\n" % kernel)
            if liveusb_initramfs == '0':
                isolinux_cfg.write("\tappend initrd=/console %s\n" % kernel_args)
            else:
                isolinux_cfg.write("\tappend %s\n\n" % kernel_args)

        kernel = "install" if liveusb_initramfs == '1' else get_bitbake_var("KERNEL_IMAGETYPE")

        if liveusb_install and amd_artifacts_dir:
            with os.scandir(amd_artifacts_dir) as artifacts:
                for artifact in artifacts:
                    isolinux_cfg.write("label %s\n" % artifact.name)
                    isolinux_cfg.write("\tmenu label install (%s)\n" % artifact.name)
                    isolinux_cfg.write("\tkernel /%s\n" % kernel)
                    if liveusb_initramfs == '0':
                        isolinux_cfg.write("\tappend initrd=/install INSTALL=%s %s\n" % (artifact.name, kernel_args))
                    else:
                        isolinux_cfg.write("\tappend INSTALL=%s %s\n" % (artifact.name, kernel_args))

        isolinux_cfg.close()

    @staticmethod
    def _install_syslinux(isodir, creator, kernel_dir, bootimg_dir):
        # Prepare files for legacy boot
        # Prefer to utilize wic-tools recipe-sysroot
        isolinux_dir = "%s/isolinux" % isodir
        syslinux_dir = "%s/syslinux" % bootimg_dir

        liveusb_splash = get_bitbake_var("LIVEUSB_SPLASH")

        if not syslinux_dir:
            raise WicError("Couldn't find STAGING_DATADIR, exiting.")

        if os.path.exists(isolinux_dir):
            shutil.rmtree(isolinux_dir)

        install_cmd = "install -d %s" % isolinux_dir
        exec_cmd(install_cmd)

        bootloader = creator.ks.bootloader
        LiveusbIsohybrid._install_isolinux_cfg(isolinux_dir, liveusb_splash,
                                               kernel_dir, bootloader)

        install_cmd = "install -m 444 %s/ldlinux.sys " % syslinux_dir
        install_cmd += "%s/ldlinux.sys" % isolinux_dir
        exec_cmd(install_cmd)

        install_cmd = "install -m 444 %s/isohdpfx.bin " % syslinux_dir
        install_cmd += "%s/isohdpfx.bin" % isolinux_dir
        exec_cmd(install_cmd)

        install_cmd = "install -m 644 %s/isolinux.bin " % syslinux_dir
        install_cmd += "%s/isolinux.bin" % isolinux_dir
        exec_cmd(install_cmd)

        install_cmd = "install -m 644 %s/ldlinux.c32 " % syslinux_dir
        install_cmd += "%s/ldlinux.c32" % isolinux_dir
        exec_cmd(install_cmd)

        # Required for menu screen
        install_cmd = "install -m 444 %s/libutil.c32 " % syslinux_dir
        install_cmd += "%s/libutil.c32" % isolinux_dir
        exec_cmd(install_cmd)

        install_cmd = "install -m 444 %s/libcom32.c32 " % syslinux_dir
        install_cmd += "%s/libcom32.c32" % isolinux_dir
        exec_cmd(install_cmd)

        if liveusb_splash:
            # Required for splash screen
            install_cmd = "install -m 644 %s/%s " % (kernel_dir, liveusb_splash)
            install_cmd += "%s/amd.jpg" % isolinux_dir
            exec_cmd(install_cmd)

            install_cmd = "install -m 444 %s/vesamenu.c32 " % syslinux_dir
            install_cmd += "%s/vesamenu.c32" % isolinux_dir
            exec_cmd(install_cmd)
        else:
            # Required for text screen
            install_cmd = "install -m 444 %s/menu.c32 " % syslinux_dir
            install_cmd += "%s/menu.c32" % isolinux_dir
            exec_cmd(install_cmd)

    @staticmethod
    def _install_grub_cfg(target_dir, kernel_dir, bootloader):
        kernel = ''
        kernel_args = ''

        liveusb_console = get_bitbake_var("LIVEUSB_CONSOLE")
        liveusb_install = get_bitbake_var("LIVEUSB_INSTALL")
        liveusb_initramfs = get_bitbake_var("LIVEUSB_INITRAMFS")
        amd_artifacts_dir = get_bitbake_var('AMD_ARTIFACTS_DIR')

        if get_bitbake_var('LIVEUSB_GRUB_KERNEL_ARGS'):
            kernel_args = get_bitbake_var('LIVEUSB_GRUB_KERNEL_ARGS')

        kernel = "console" if liveusb_initramfs == '1' else get_bitbake_var("KERNEL_IMAGETYPE")

        grub_cfg = open("%s/grub.cfg" % target_dir, "w", encoding="utf-8")

        grub_cfg.write("serial --unit=0 --speed=115200 --word=8 --parity=no --stop=1\n\n")
        grub_cfg.write("terminal_input serial console\n")
        grub_cfg.write("terminal_output serial console\n\n")
        grub_cfg.write("set default=0\n\n")
        grub_cfg.write("set timeout=%s\n\n" % (bootloader.timeout or 50))

        if liveusb_console:
            grub_cfg.write("menuentry 'console' {\n")
            grub_cfg.write("\tlinux /%s %s\n" % (kernel, kernel_args))
            if liveusb_initramfs == '0':
                grub_cfg.write("\tinitrd /console\n" % kernel)
            grub_cfg.write("}\n\n")

        kernel = "install" if liveusb_initramfs == '1' else get_bitbake_var("KERNEL_IMAGETYPE")

        if liveusb_install and amd_artifacts_dir:
            with os.scandir(amd_artifacts_dir) as artifacts:
                for artifact in artifacts:
                    grub_cfg.write("menuentry 'install (%s)' {\n" % artifact.name)
                    grub_cfg.write("\tlinux /%s INSTALL=%s %s\n" % (kernel, artifact.name, kernel_args))
                    if liveusb_initramfs == '0':
                        grub_cfg.write("\tinitrd /install\n")
                    grub_cfg.write("}\n\n")

        grub_cfg.close()

    @staticmethod
    def _install_grub_efi(isodir, creator, kernel_dir, native_sysroot):
        target_dir = "%s/EFI/BOOT" % isodir
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        os.makedirs(target_dir)

        # Builds bootx64.efi/bootia32.efi if ISODIR didn't exist or
        # didn't contains it
        target_arch = get_bitbake_var("TARGET_SYS")
        if not target_arch:
            raise WicError("Coludn't find target architecture")

        if re.match("x86_64", target_arch):
            grub_src_image = "grub-efi-bootx64.efi"
            grub_dest_image = "bootx64.efi"
        elif re.match('i.86', target_arch):
            grub_src_image = "grub-efi-bootia32.efi"
            grub_dest_image = "bootia32.efi"
        else:
            raise WicError("grub-efi is incompatible with target %s" % target_arch)

        bootloader = creator.ks.bootloader
        LiveusbIsohybrid._install_grub_cfg(target_dir, kernel_dir, bootloader)

        # Create startup script
        uefi_script = "printf 'fs0:/EFI/BOOT/%s' > %s/startup.nsh" % (grub_dest_image,isodir)
        exec_native_cmd(uefi_script, native_sysroot)

    @staticmethod
    def _install_efi_image(isodir, kernel_dir, native_sysroot, source_params, part):
        # Default to 100 blocks of extra space for file system overhead
        esp_extra_blocks = int(source_params.get('esp_extra_blocks', '100'))

        du_cmd = "du -bks %s/EFI" % isodir
        out = exec_cmd(du_cmd)
        blocks = int(out.split()[0])
        blocks += esp_extra_blocks
        logger.debug("Added %d extra blocks to %s to get to %d total blocks",
                     esp_extra_blocks, part.mountpoint, blocks)

        # dosfs image for EFI boot
        bootimg = "%s/efi.img" % isodir

        esp_label = source_params.get('esp_label', 'EFIimg')

        dosfs_cmd = 'mkfs.vfat -n \'%s\' -S 512 -C %s %d' \
                    % (esp_label, bootimg, blocks)
        exec_native_cmd(dosfs_cmd, native_sysroot)

        mmd_cmd = "mmd -i %s ::/EFI" % bootimg
        exec_native_cmd(mmd_cmd, native_sysroot)

        mcopy_cmd = "mcopy -i %s -s %s/EFI/* ::/EFI/" \
                    % (bootimg, isodir)
        exec_native_cmd(mcopy_cmd, native_sysroot)

        chmod_cmd = "chmod 644 %s" % bootimg
        exec_cmd(chmod_cmd)

    @staticmethod
    def _install_kernel(isodir, kernel_dir):
        if get_bitbake_var('LIVEUSB_INITRAMFS') != '1':
            kernel = "%s/%s" % (kernel_dir, get_bitbake_var("KERNEL_IMAGETYPE"))
            shutil.copy(kernel, isodir, follow_symlinks=True)

    @staticmethod
    def _install_initrd(isodir, kernel_dir):
        console = ''
        install = ''

        liveusb_console = get_bitbake_var("LIVEUSB_CONSOLE")
        liveusb_install = get_bitbake_var("LIVEUSB_INSTALL")

        if liveusb_console:
            console = "%s/%s" % (kernel_dir,liveusb_console)
        if liveusb_install:
            install = "%s/%s" % (kernel_dir,liveusb_install)

        if console:
            shutil.copy(console, isodir + "/console", follow_symlinks=True)
        if install:
            shutil.copy(install, isodir + "/install", follow_symlinks=True)

    @staticmethod
    def _create_iso_image(isodir, iso_img, native_sysroot, part):
        iso_bootimg = "isolinux/isolinux.bin"
        iso_bootcat = "isolinux/boot.cat"
        efi_img = "efi.img"

        mkisofs_cmd = "mkisofs -V %s " % part.label
        mkisofs_cmd += "-o %s -U " % iso_img
        mkisofs_cmd += "-J -joliet-long -r -iso-level 2 -b %s " % iso_bootimg
        mkisofs_cmd += "-c %s -no-emul-boot -boot-load-size 4 " % iso_bootcat
        mkisofs_cmd += "-boot-info-table -eltorito-alt-boot "
        mkisofs_cmd += "-eltorito-platform 0xEF -eltorito-boot %s " % efi_img
        mkisofs_cmd += "-no-emul-boot %s " % isodir

        logger.debug("running command: %s", mkisofs_cmd)
        exec_native_cmd(mkisofs_cmd, native_sysroot)

        shutil.rmtree(isodir)

    @classmethod
    def do_prepare_partition(cls, part, source_params, creator, cr_workdir,
                             oe_builddir, bootimg_dir, kernel_dir,
                             rootfs_dir, native_sysroot):
        """
        Called to do the actual content population for a partition i.e. it
        'prepares' the partition to be incorporated into the image.
        In this case, prepare content for a bootable ISO image.
        """

        isodir = "%s/ISO" % cr_workdir
        if os.path.exists(isodir):
            shutil.rmtree(isodir)

        cls._install_grub_efi(isodir, creator, kernel_dir, native_sysroot)
        cls._install_efi_image(isodir, kernel_dir, native_sysroot, source_params, part)
        cls._install_syslinux(isodir, creator, kernel_dir, bootimg_dir)
        cls._install_kernel(isodir, kernel_dir)
        cls._install_initrd(isodir, kernel_dir)

        iso_img = "%s/tempiso_img.iso" % cr_workdir
        cls._create_iso_image(isodir, iso_img, native_sysroot, part)

        isohybrid_cmd = "isohybrid -u %s" % iso_img
        logger.debug("running command: %s", isohybrid_cmd)
        exec_native_cmd(isohybrid_cmd, native_sysroot)

        du_cmd = "du -Lbks %s" % iso_img
        out = exec_cmd(du_cmd)
        isoimg_size = int(out.split()[0])

        part.size = isoimg_size
        part.source_file = iso_img

    @classmethod
    def do_install_disk(cls, disk, disk_name, creator, workdir, oe_builddir,
                        bootimg_dir, kernel_dir, native_sysroot):
        """
        Called after all partitions have been prepared and assembled into a
        disk image.  In this case, we insert/modify the MBR using isohybrid
        utility for booting via BIOS from disk storage devices.
        """

        iso_img = "%s.p1" % disk.path
        wic_image = creator._full_path(workdir, disk_name, "direct")

        dd_cmd = "dd if=%s of=%s conv=notrunc" % (iso_img, wic_image)
        exec_cmd(dd_cmd, native_sysroot)

        # Doesn't account for logical partitions at the moment.
        fdisk_str = ''
        for part in creator.parts:
            if part.num > 1:
                fdisk_str += 'n\np\n%d\n%d\n+%d\n' % \
                    (part.num + 1, part.start, part.size_sec-1)

        if fdisk_str:
            fdisk_str += 'w\n'
            fdisk_cmd = 'echo -e "%s" | fdisk %s' % (fdisk_str, wic_image)
            logger.debug("running command: %s", fdisk_cmd)
            exec_native_cmd(fdisk_cmd, native_sysroot)
