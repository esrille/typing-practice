# Copyright (c) 2020-2024 Esrille Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

m4_define([typing_practice_version], [0.3.3~rc1])
AC_INIT([esrille-typing-practice], [typing_practice_version], [https://github.com/esrille/typing-practice/issues])
AC_CONFIG_AUX_DIR([.])
AM_INIT_AUTOMAKE([foreign tar-ustar])

AM_GNU_GETTEXT([external])
AM_GNU_GETTEXT_REQUIRE_VERSION([0.19.8])
AM_GNU_GETTEXT_VERSION([0.19.8])

# Check Python
AM_PATH_PYTHON([3.8])

# define GETTEXT_* variables
GETTEXT_PACKAGE=AC_PACKAGE_NAME
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(
  GETTEXT_PACKAGE, "$GETTEXT_PACKAGE",
    [Define to the read-only architecture-independent data directory.]
)

# For GitHub
m4_define(typing_practice_source_version,
  [m4_esyscmd(echo -n typing_practice_version | tr '~' '-')])
SOURCE_VERSION="typing_practice_source_version"
AC_SUBST(SOURCE_VERSION)

# OUTPUT files
AC_CONFIG_FILES(
docs/Makefile
icons/Makefile
lessons/Makefile
po/Makefile.in
src/Makefile
src/package.py.in
src/esrille-typing-practice.in
Makefile
)

AC_OUTPUT
