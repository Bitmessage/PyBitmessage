from os import environ
from os.path import exists, join

import sh
from pythonforandroid.logger import shprint, info_main, info
from pythonforandroid.recipe import PythonRecipe
# from pythonforandroid.util import ensure_dir


class KivyMDRecipe(PythonRecipe):
    # This recipe installs KivyMD into the android dist from source
    version = 'master'
    # url = 'https://gitlab.com/kivymd/KivyMD/repository/{version}/archive.zip'
    url = 'https://github.com/HeaTTheatR/KivyMD/archive/master.zip'
    depends = ['kivy']
    site_packages_name = 'kivymd'
    call_hostpython_via_targetpython = False
    # patches = ['kivymd-fix-dev-compatibility.patch']
    # Made commented as use different repo for updates

    def should_build(self, arch):
        return True

    # def unpack(self, arch):
    #     info_main('Unpacking {} for {}'.format(self.name, arch))
    #
    #     build_dir = self.get_build_container_dir(arch)
    #
    #     user_dir = environ.get('P4A_{}_DIR'.format(self.name.lower()))
    #
    #     if user_dir is not None:
    #         info("Installing KivyMD development version (from modded source)")
    #         self.clean_build()
    #         shprint(sh.rm, '-rf', build_dir)
    #         shprint(sh.mkdir, '-p', build_dir)
    #         shprint(sh.rmdir, build_dir)
    #         ensure_dir(build_dir)
    #         ensure_dir(build_dir + "/kivymd")
    #         shprint(sh.cp, user_dir + '/setup.py', self.get_build_dir(arch) + "/setup.py")
    #         shprint(sh.cp, '-a', user_dir + "/kivymd", self.get_build_dir(arch) + "/kivymd")
    #         return

    def get_recipe_env(self, arch):
        env = super(KivyMDRecipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -lpython2.7'
        if 'sdl2' in self.ctx.recipe_build_order:
            env['USE_SDL2'] = '1'
            env['KIVY_SDL2_PATH'] = ':'.join([
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_image'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
                ])
        return env


recipe = KivyMDRecipe()
