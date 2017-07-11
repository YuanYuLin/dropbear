import ops
import iopc

TARBALL_FILE="dropbear-2017.75.tar.bz2"
TARBALL_DIR="dropbear-2017.75"
INSTALL_DIR="dropbear-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
dst_bin_dir = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global tarball_dir
    global dst_bin_dir
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    dst_bin_dir = ops.path_join(install_dir, "bin")

def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    #ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    #ops.exportEnv(ops.setEnv("DESTDIR", install_dir))

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarBz2(tarball_pkg, output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    env_conf = None

    extra_conf = []
    extra_conf.append("--host=x86_64")
    extra_conf.append("--build=armel")
    extra_conf.append("--with-zlib=" + iopc.getDevPkgPath("libz"))
    extra_conf.append("--prefix=" + install_dir)
    extra_conf.append("--disable-loginfunc")
    extra_conf.append("--disable-shadow")
    extra_conf.append("--disable-lastlog")
    iopc.configure(tarball_dir, extra_conf, env_conf, False)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)

    extra_conf = []
    extra_conf.append("MULTI=1")
    iopc.make_install(tarball_dir, extra_conf)

    ops.mkdir(dst_bin_dir)
    ops.copyto(ops.path_join(tarball_dir, "dropbearmulti"), dst_bin_dir)
    ops.ln(dst_bin_dir, "dropbearmulti", "dbclient")
    ops.ln(dst_bin_dir, "dropbearmulti", "dropbearconvert")
    ops.ln(dst_bin_dir, "dropbearmulti", "dropbearkey")
    ops.ln(dst_bin_dir, "dropbearmulti", "dropbear")

    return False

def MAIN_INSTALL(args):
    set_global(args)

    iopc.installBin(args["pkg_name"], ops.path_join(dst_bin_dir, "."), "bin")

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

