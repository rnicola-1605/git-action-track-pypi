# -*- coding: utf-8 -*-
import re
import requests as req
from pkg_resources import parse_version

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


pkgs_to_bump = []
pkgs_ok = []

with open('requirements.txt', 'r') as requirements:
    for pkg in requirements.readlines():
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
                pkgs_to_bump.append({pkg: str(latest_release)})
            else:
                pkgs_ok.append(pkg)

# print(json.dumps(pkgs_to_bump))
json.dumps(pkgs_to_bump)
