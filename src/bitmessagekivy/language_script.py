import os
import subprocess

KVFILES = [
    "settings",
    "popup",
    "allmails",
    "draft",
    "maildetail",
    "common_widgets",
    "addressbook",
    "myaddress",
    "composer",
    "payment",
    "sent",
    "network",
    "login",
    "credits",
    "trash",
    "inbox",
    "chat_room",
    "chat_list"
]

windowsLanguageMap = {
    'ar': 'Arabic',
    'cs': 'Czech',
    'da': 'Danish',
    'de': 'German',
    'en': 'English',
    'eo': 'Esperanto',
    'fr': 'French',
    'it': 'Italian',
    'ja': 'Japanese',
    'nl': 'Dutch',
    'no': 'Norwegian',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'sk': 'Slovak',
    'zh': 'Chinese',
}

current_dir_path = os.path.abspath(os.path.join(__file__, '../'))
main_file = os.path.join(current_dir_path, 'mpybit.py')
kv_file = os.path.join(current_dir_path, 'main.kv')

print("Create .po files for Project")

translation_command = [
    'xgettext',
    '-Lpython',
    '--output=messages.pot',
    '--from-code=UTF-8',
    main_file,
    kv_file
]

for kv_file in KVFILES:
    translation_command.append(f'{current_dir_path}/kv/{kv_file}.kv')

# print('translation_command..............', translation_command)
subprocess.run(translation_command, stdout=subprocess.DEVNULL)
# print("The exit code1 was: %d" % list_files.returncode)

# this command is used to create seperate dir for mo and po file
subprocess.run(
    ['mkdir', '-p', 'translations/po'], stdout=subprocess.DEVNULL)


for key in windowsLanguageMap.keys():
    subprocess.run(
        ['touch', f'{current_dir_path}/translations/po/bitmessage_{key}.po'], stdout=subprocess.DEVNULL)
    subprocess.run(
        ['msgmerge', '--update', '--no-fuzzy-matching', '--backup=off',
            f'{current_dir_path}/translations/po/bitmessage_{key}.po', f'{current_dir_path}/messages.pot'],
        stdout=subprocess.DEVNULL
    )

print("Create .mo file from .po file")

for key in windowsLanguageMap.keys():
    subprocess.run(
        ['mkdir', '-p', f'{current_dir_path}/translations/mo/locales/{key}/LC_MESSAGES'],
        stdout=subprocess.DEVNULL
    )
    subprocess.run(
        ['touch', f'{current_dir_path}/translations/mo/locales/{key}/LC_MESSAGES/langapp.mo'],
        stdout=subprocess.DEVNULL
    )
    subprocess.run(
        ['msgfmt', '-c', '-o', f'{current_dir_path}/translations/mo/locales/{key}/LC_MESSAGES/langapp.mo',
            f'{current_dir_path}/translations/po/bitmessage_{key}.po'], stdout=subprocess.DEVNULL
    )
