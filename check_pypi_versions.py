# -*- coding: utf-8 -*-
import re
import requests as req
from pkg_resources import parse_version

import os
import json


def get_versions(package_name, last_release=None):
    """Get versions of package from pypi resource."""
    url = "https://pypi.org/pypi/%s/json" % (package_name,)
    data = req.get(url).json()
    versions = list(data["releases"].keys())
    versions.sort(key=parse_version)

    if last_release:
        return parse_version(versions[-1])

    return versions


path_to_requirements = 'requirements.txt'

pkgs_to_bump = []
pkgs_ok = []

if os.path.isfile(path_to_requirements):

    with open('requirements.txt', 'r') as requirements:
        file_lines = (
            requirements.readlines() if requirements else [])

        for pkg in file_lines:
            pkg.replace('\n', '')

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
                latest_release = get_versions(pkg, True)
                if parse_version(version) < latest_release:
                    pkgs_to_bump.append({
                        "package": pkg,
                        "bump_to": str(latest_release)
                    })
                else:
                    pkgs_ok.append(pkg)

print(json.dumps(pkgs_to_bump))
