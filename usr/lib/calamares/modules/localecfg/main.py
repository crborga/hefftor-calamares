#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# === This file is part of Calamares - <https://github.com/calamares> ===
#
#   Copyright 2014, Anke Boersma <demm@kaosx.us>
#   Copyright 2015, Philip Müller <philm@manjaro.org>
#   Copyright 2016, Teo Mrnjavac <teo@kde.org>
#   Copyright 2018, AlmAck <gluca86@gmail.com>
#   Copyright 2018-2019, Adriaan de Groot <groot@kde.org>
#
#   Calamares is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Calamares is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Calamares. If not, see <http://www.gnu.org/licenses/>.

import os
import re
import shutil

import libcalamares

import gettext
_ = gettext.translation("calamares-python",
                        localedir=libcalamares.utils.gettext_path(),
                        languages=libcalamares.utils.gettext_languages(),
                        fallback=True).gettext


def pretty_name():
    return _("Configuring locales.")


RE_IS_COMMENT = re.compile("^ *#")
def is_comment(line):
    """
    Does the @p line look like a comment? Whitespace, followed by a #
    is a comment-only line.
    """
    return bool(RE_IS_COMMENT.match(line))

RE_TRAILING_COMMENT = re.compile("#.*$")
RE_REST_OF_LINE = re.compile("\\s.*$")
def extract_locale(line):
    """
    Extracts a locale from the @p line, and returns a pair of
    (extracted-locale, uncommented line). The locale is the
    first word of the line after uncommenting (in the human-
    readable text explanation at the top of most /etc/locale.gen
    files, the locales may be bogus -- either "" or e.g. "Configuration")
    """
    # Remove leading spaces and comment signs
    line = RE_IS_COMMENT.sub("", line)
    uncommented = line.strip()
    fields = RE_TRAILING_COMMENT.sub("", uncommented).strip().split()
    if len(fields) != 2:
        # Not exactly two fields, can't be a proper locale line
        return "", uncommented
    else:
        # Drop all but first field
        locale = RE_REST_OF_LINE.sub("", uncommented)
        return locale, uncommented


def rewrite_locale_gen(srcfilename, destfilename, locale_conf):
    """
    Copies a locale.gen file from @p srcfilename to @p destfilename
    (this may be the same name), enabling those locales that can
    be found in the map @p locale_conf. Also always enables en_US.UTF-8.
    """
    en_us_locale = 'en_US.UTF-8'

    # Get entire source-file contents
    text = []
    with open(srcfilename, "r") as gen:
        text = gen.readlines()

    # we want unique values, so locale_values should have 1 or 2 items
    locale_values = set(locale_conf.values())
    locale_values.add(en_us_locale)  # Always enable en_US as well

    enabled_locales = {}
    seen_locales = set()

    # Write source out again, enabling some
    with open(destfilename, "w") as gen:
        for line in text:
            c = is_comment(line)
            locale, uncommented = extract_locale(line)

            # Non-comment lines are preserved, and comment lines
            # may be enabled if they match a desired locale
            if not c:
                seen_locales.add(locale)
            else:
                for locale_value in locale_values:
                    if locale.startswith(locale_value):
                        enabled_locales[locale] = uncommented
            gen.write(line)

        gen.write("\n###\n#\n# Locales enabled by Calamares\n")
        for locale, line in enabled_locales.items():
            if locale not in seen_locales:
                gen.write(line + "\n")
                seen_locales.add(locale)

        for locale in locale_values:
            if locale not in seen_locales:
                gen.write("# Missing: %s\n" % locale)


def run():
    """ Create locale """
    import libcalamares

    locale_conf = libcalamares.globalstorage.value("localeConf")

    if not locale_conf:
        locale_conf = {
            'LANG': 'en_US.UTF-8',
            'LC_NUMERIC': 'en_US.UTF-8',
            'LC_TIME': 'en_US.UTF-8',
            'LC_MONETARY': 'en_US.UTF-8',
            'LC_PAPER': 'en_US.UTF-8',
            'LC_NAME': 'en_US.UTF-8',
            'LC_ADDRESS': 'en_US.UTF-8',
            'LC_TELEPHONE': 'en_US.UTF-8',
            'LC_MEASUREMENT': 'en_US.UTF-8',
            'LC_IDENTIFICATION': 'en_US.UTF-8'
        }

    install_path = libcalamares.globalstorage.value("rootMountPoint")

    if install_path is None:
        libcalamares.utils.warning("rootMountPoint is empty, {!s}".format(install_path))
        return (_("Configuration Error"),
                _("No root mount point is given for <pre>{!s}</pre> to use." ).format("localecfg"))

    target_locale_gen = "{!s}/etc/locale.gen".format(install_path)
    target_locale_gen_bak = target_locale_gen + ".bak"
    target_locale_conf_path = "{!s}/etc/locale.conf".format(install_path)
    target_etc_default_path = "{!s}/etc/default".format(install_path)

    # restore backup if available
    if os.path.exists(target_locale_gen_bak):
        shutil.copy2(target_locale_gen_bak, target_locale_gen)
        libcalamares.utils.debug("Restored backup {!s} -> {!s}"
            .format(target_locale_gen_bak, target_locale_gen))

    # run locale-gen if detected; this *will* cause an exception
    # if the live system has locale.gen, but the target does not:
    # in that case, fix your installation filesystem.
    if os.path.exists('/etc/locale.gen'):
        rewrite_locale_gen(target_locale_gen, target_locale_gen, locale_conf)
        libcalamares.utils.target_env_call(['locale-gen'])
        libcalamares.utils.debug('{!s} done'.format(target_locale_gen))

    # write /etc/locale.conf
    with open(target_locale_conf_path, "w") as lcf:
        for k, v in locale_conf.items():
            lcf.write("{!s}={!s}\n".format(k, v))
        libcalamares.utils.debug('{!s} done'.format(target_locale_conf_path))

    # write /etc/default/locale if /etc/default exists and is a dir
    if os.path.isdir(target_etc_default_path):
        with open(os.path.join(target_etc_default_path, "locale"), "w") as edl:
            for k, v in locale_conf.items():
                edl.write("{!s}={!s}\n".format(k, v))
        libcalamares.utils.debug('{!s} done'.format(target_etc_default_path))

    return None
