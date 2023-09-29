from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join
import os
import sys
from multiprocessing import cpu_count
import sh


class BitmsghashRecipe(Recipe):
    # This could also inherit from PythonRecipe etc. if you want to
    # use their pre-written build processes

    url = 'https://github.com/surbhicis/bitmsghash/archive/master.zip'
    # {version} will be replaced with self.version when downloading

    depends = ['openssl']

    conflicts = []

    def get_recipe_env(self, arch=None):
        env = super(BitmsghashRecipe, self).get_recipe_env(arch)
        r = Recipe.get_recipe('openssl', self.ctx)
        b = r.get_build_dir(arch.arch)
        env['CCFLAGS'] = env['CFLAGS'] = \
            env['CFLAGS'] + ' -I{openssl_build_path}/include ' \
                            '-I{openssl_build_path}/include/openssl'.format(
                            openssl_build_path=b)
        env['LDFLAGS'] = \
            env['LDFLAGS'] + ' -L{openssl_build_path} ' \
            '-lcrypto{openssl_version} ' \
            '-lssl{openssl_version}'.format(
            openssl_build_path=b,
            openssl_version=r.version)
        return env

    def should_build(self, arch=None):
        super(BitmsghashRecipe, self).should_build(arch)
        return not exists(
            join(self.ctx.get_libs_dir(arch.arch), 'libbitmsghash.so'))

    def build_arch(self, arch=None):
        super(BitmsghashRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(join(self.get_build_dir(arch.arch))):
            dst_dir = join(self.get_build_dir(arch.arch))
            shprint(sh.make, '-j', str(cpu_count()), _env=env)
            self.install_libs(arch, '{}/libbitmsghash.so'.format(dst_dir),
                                    'libbitmsghash.so')

recipe = BitmsghashRecipe()