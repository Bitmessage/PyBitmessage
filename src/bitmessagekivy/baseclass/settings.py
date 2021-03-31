from kivy.uix.screenmanager import Screen


class Setting(Screen):
    """Setting Screen for kivy Ui"""
    exp_text = "By default, if you send a message to someone and he is offline for more than two days, Bitmessage will\
                send the message again after an additional two days. This will be continued with exponential backoff\
                forever; messages will be resent after 5, 10, 20 days ect. until the receiver acknowledges them.\
                Here you may change that behavior by having Bitmessage give up after a certain number of days \
                or months."

    # languages = {
    #     'ar': 'Arabic',
    #     'cs': 'Czech',
    #     'da': 'Danish',
    #     'de': 'German',
    #     'en': 'English',
    #     'eo': 'Esperanto',
    #     'fr': 'French',
    #     'it': 'Italian',
    #     'ja': 'Japanese',
    #     'nl': 'Dutch',
    #     'no': 'Norwegian',
    #     'pl': 'Polish',
    #     'pt': 'Portuguese',
    #     'ru': 'Russian',
    #     'sk': 'Slovak',
    #     'zh': 'Chinese',
    # }
    # newlocale = None

    # def __init__(self, *args, **kwargs):
    #     """Trash method, delete sent message and add in Trash"""
    #     super(Setting, self).__init__(*args, **kwargs)
    #     if self.newlocale is None:
    #         self.newlocale = l10n.getTranslationLanguage()
    #     lang = locale.normalize(l10n.getTranslationLanguage())
    #     langs = [
    #         lang.split(".")[0] + "." + l10n.encoding,
    #         lang.split(".")[0] + "." + 'UTF-8',
    #         lang
    #     ]
    #     if 'win32' in platform or 'win64' in platform:
    #         langs = [l10n.getWindowsLocale(lang)]
    #     for lang in langs:
    #         try:
    #             l10n.setlocale(locale.LC_ALL, lang)
    #             if 'win32' not in platform and 'win64' not in platform:
    #                 l10n.encoding = locale.nl_langinfo(locale.CODESET)
    #             else:
    #                 l10n.encoding = locale.getlocale()[1]
    #             logger.info("Successfully set locale to %s", lang)
    #             break
    #         except:
    #             logger.error("Failed to set locale to %s", lang, exc_info=True)

    #     Clock.schedule_once(self.init_ui, 0)

    # def init_ui(self, dt=0):
    #     """Initialization for Ui"""
    #     if self.newlocale is None:
    #         self.newlocale = l10n.getTranslationLanguage()
    #     # state.kivyapp.tr = Lang(self.newlocale)
    #     state.kivyapp.tr = Lang(self.newlocale)
    #     menu_items = [{"text": f"{i}"} for i in self.languages.values()]
    #     self.menu = MDDropdownMenu(
    #         caller=self.ids.dropdown_item,
    #         items=menu_items,
    #         position="auto",
    #         width_mult=3.5,
    #     )
    #     self.menu.bind(on_release=self.set_item)

    # def set_item(self, instance_menu, instance_menu_item):
    #     self.ids.dropdown_item.set_item(instance_menu_item.text)
    #     instance_menu.dismiss()

    # def change_language(self):
    #     lang = self.ids.dropdown_item.current_item
    #     for k, v in self.languages.items():
    #         if v == lang:
    #             BMConfigParser().set('bitmessagesettings', 'userlocale', k)
    #             BMConfigParser().save()
    #             state.kivyapp.tr = Lang(k)
    #             self.children[0].active = True
    #             Clock.schedule_once(partial(self.language_callback, k), 1)

    # def language_callback(self, lang, dt=0):
    #     self.children[0].active = False
    #     state.kivyapp.tr = Lang(lang)
    #     toast('Language changed')