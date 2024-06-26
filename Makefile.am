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

SUBDIRS = \
	docs \
	icons \
	lessons \
	po \
	src\
	$(NULL)

EXTRA_DIST = \
	debian/changelog \
	debian/changelog.in \
	debian/compat \
	debian/control \
	debian/copyright \
	debian/rules \
	debian/source/format \
	autogen.sh \
	@PACKAGE_NAME@.spec \
	@PACKAGE_NAME@.spec.in \
	CONTRIBUTING.md \
	LICENSE \
	NOTICE \
	README.md \
	README.txt \
	$(NULL)

DISTCLEANFILES = \
	po/stamp-it \
	$(NULL)

debian/changelog:
	$(AM_V_GEN) \
	( \
		date=`date -R`; \
		version=@VERSION@; \
		source_version=@SOURCE_VERSION@; \
		s=`cat debian/changelog.in`; \
		eval "echo \"$${s}\""; \
	) > $@

@PACKAGE_NAME@.spec:
	$(AM_V_GEN) \
	( \
		date=`date '+%a %b %d %Y'`; \
		version=@VERSION@; \
		source_version=@SOURCE_VERSION@; \
		s=`cat @PACKAGE_NAME@.spec.in`; \
		eval "echo \"$${s}\""; \
	) > $@

uninstall-hook:
	-rmdir $(pkgdatadir)
