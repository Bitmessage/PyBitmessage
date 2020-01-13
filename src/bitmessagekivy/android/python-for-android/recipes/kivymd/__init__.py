"""
src/bitmessagekivy/android/python-for-android/recipes/kivymd/__init__.py
=================================
"""
# pylint: disable=import-error
from os.path import join

from pythonforandroid.recipe import PythonRecipe
# from pythonforandroid.util import ensure_dir


class KivyMDRecipe(PythonRecipe):
    """This recipe installs KivyMD into the android dist from source"""
    version = 'master'
    url = 'https://github.com/surbhicis/kivymd/archive/master.zip'
    depends = ['kivy']
    site_packages_name = 'kivymd'
    call_hostpython_via_targetpython = False

    def should_build(self, arch):    # pylint: disable=no-self-use, unused-argument
        """Method helps to build the application"""
        return True

    def get_recipe_env(self, arch):
        """Method is used for getting all the env paths"""
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
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'), ])
        return env


recipe = KivyMDRecipe()
