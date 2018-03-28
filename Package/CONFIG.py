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
install_tmp_dir = ""
dst_bin_dir = ""
cc_host = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global dst_bin_dir
    global cc_host
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    dst_bin_dir = ops.path_join(install_dir, "bin")
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]


def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))

    cc_sysroot = ops.getEnv("CC_SYSROOT")

    cflags = ""
    cflags += " -I" + ops.path_join(cc_sysroot, 'usr/include')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libz')

    ldflags = ""
    ldflags += " -L" + ops.path_join(cc_sysroot, 'lib')
    ldflags += " -L" + ops.path_join(cc_sysroot, 'usr/lib')
    ldflags += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')
    ldflags += " -L" + ops.path_join(iopc.getSdkPath(), 'usr/lib')

    ops.exportEnv(ops.setEnv("LDFLAGS", ldflags))
    ops.exportEnv(ops.setEnv("CFLAGS", cflags))

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
    #extra_conf.append("--host=x86_64")
    extra_conf.append("--host=" + cc_host)
    extra_conf.append("--build=armel")
    #extra_conf.append("--with-zlib=" + ops.path_join(iopc.getSdkPath, "libz"))
    #extra_conf.append("--prefix=" + install_dir)
    extra_conf.append("--disable-loginfunc")
    extra_conf.append("--disable-shadow")
    extra_conf.append("--disable-lastlog")
    iopc.configure(tarball_dir, extra_conf, env_conf, False)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)

    extra_conf = []
    extra_conf.append("MULTI=1")

    iopc.make(tarball_dir, extra_conf)
    iopc.make_install(tarball_dir, extra_conf)

    return False

def MAIN_INSTALL(args):
    set_global(args)

    ops.mkdir(install_dir)

    ops.mkdir(ops.path_join(install_dir, "bin"))

    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/bin/dropbearmulti"), ops.path_join(install_dir, "bin"))
    ops.ln(ops.path_join(install_dir, "bin"), "dropbearmulti", "dbclient")
    ops.ln(ops.path_join(install_dir, "bin"), "dropbearmulti", "dropbearconvert")
    ops.ln(ops.path_join(install_dir, "bin"), "dropbearmulti", "dropbearkey")
    ops.ln(ops.path_join(install_dir, "bin"), "dropbearmulti", "dropbear")

    iopc.installBin(args["pkg_name"], ops.path_join(install_dir, "bin/."), "bin")

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

