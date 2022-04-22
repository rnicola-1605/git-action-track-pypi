# -*- coding: utf-8 -*-
import re
import os
import json
import requests as req

from datetime import datetime
from pkg_resources import parse_version


def get_versions(
        package_name, package_version_now, last_release=None,
        check_for_days_stability=None):
    """Get versions of package from Pypi.

    var check_for_days_stability: Checks if release date from latest version
    is at least $check_for_days_stability days old. Since we need some sort
    of stability to upgrade to new versions.
    """
    url = "https://pypi.org/pypi/%s/json" % (package_name,)
    data = req.get(url).json()
    versions = list(data["releases"].keys())
    versions.sort(key=parse_version)

    #
    # Get last release available.
    #
    if last_release:

        # If actual version is not found in releases, simply return the
        # latest one.
        #
        latest_version = versions[-1]

        if not check_for_days_stability:
            parse_version(latest_version)

        try:
            dt_release = datetime.fromisoformat(
                data["releases"][package_version_now][-1]["upload_time"])
        except IndexError:
            return parse_version(versions[-1])

        dt_release_new = datetime.fromisoformat(
            data["releases"][versions[-1]][-1]["upload_time"])

        _diff_dates = (dt_release_new - dt_release)
        _diff_days = int(divmod(_diff_dates.total_seconds(), 86400)[0])

        if (_diff_days >= 90):
            return parse_version(latest_version)

        return None

    return versions


path_to_requirements = 'requirements.txt'

pkgs_to_bump = []
pkgs_ok = []

if os.path.isfile(path_to_requirements):

    with open('requirements.txt', 'r') as requirements:
        file_lines = (
            requirements.readlines() if requirements else [])

        for pkg in file_lines:
            pkg = pkg.replace('\n', '')

            if pkg.find('==') != -1:
                pkg, version = pkg.split('==')
            else:
                pattern_1 = re.findall(r"(\d+(?:\.\d+){0,2})", pkg)
                if (pattern_1):
                    version = pattern_1
                    pkg = re.findall(r'^(.*?)>=', pkg)[0]
                else:
                    continue

            if isinstance(version, (str, bytes)):
                latest_release = get_versions(
                    package_name=pkg,
                    package_version_now=version,
                    last_release=True,
                    check_for_days_stability=60)

                if latest_release and parse_version(version) < latest_release:
                    pkgs_to_bump.append({
                        "package": pkg,
                        "bump_to": str(latest_release)
                    })
                else:
                    pkgs_ok.append(pkg)

print(json.dumps(pkgs_to_bump))
