# Minecraft Mappings Reverser
# Copyright (c) 2019
# by xt449/BinaryBanana
#
# This file is part of Minecraft Mappings Reverser.
#
# Minecraft Mappings Reverser is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# Minecraft Mappings Reverser is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Minecraft Mappings Reverser.
# If not, see <https://www.gnu.org/licenses/>.
#

import requests

print("Fetching versions manifest from Mojang...")
request = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
versionID = input("Version: ")
possible_result = list(
    map(lambda data: data.get("url"),
        filter(lambda data: data.get("id") == versionID,
               list(request.json().get("versions"))
               )
        )
)

if (len(possible_result) > 0):
    print("Fetching version data from Mojang...")
    request = requests.get(possible_result[0])
    possible_result = request.json().get("downloads").get("server_mappings").get("url")
    print("Fetching mappings from Mojang...")
    request = requests.get(possible_result)

    classMap = dict()
    for line in list(filter(lambda l: l[0] != ' ', request.text.splitlines())):
        if (line[0] != '#'):
            parts = line.split(" -> ")
            if (len(parts) < 2):
                print("Error?: " + line)
            classMap[parts[0]] = parts[1][:-1]

    import re

    # Regex:
    #   ^((?:\s+(?:\d+:\d+:)?[\w$.\[\]]+ )?)([\w$.]+)((?:\([^)]*\))?) -> ([\w$.]+)
    #   $1$4$3 -> $2
    content = re.sub("^((?:\\s+(?:\\d+:\\d+:)?[\\w$.\\[\\]]+ )?)([\\w$.]+)((?:\\([^)]*\\))?) -> ([\\w$.]+)", "\\1\\4\\3 -> \\2", request.text, flags=re.MULTILINE).splitlines()

    deobfuscated = list()

    for i in range(len(content)):
        if (content[i][0] == ' ' and '(' in content[i]):
            start = content[i].index('(') + 1
            end = content[i].index(')')
            deobfuscated.append(
                content[i][:start] + ','.join(
                    map(lambda par: par if par not in classMap else classMap[par],
                        filter(lambda par: len(par) > 0,
                               content[i][start:end].split(',')
                               )
                        )
                ) + content[i][end:] + '\n'
            )
        else:
            deobfuscated.append(content[i] + '\n')

    file = open("output\\reversed_" + versionID + ".txt", "w+")
    file.writelines(deobfuscated)

    print("Finished writing to file!")
else:
    print("Unable to get version data for " + versionID)
