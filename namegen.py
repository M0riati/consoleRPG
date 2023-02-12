import hashlib
import json
import os
import random
from enum import Enum
from pathlib import Path

minSeqRange = 2
maxSeqRange = 3

originality = 3000
TERMINATOR = '\\'
compiled = []


class Cultures(Enum):
    ENGLISH = 'assets/nameDatasets/english.json'
    FRENCH = 'assets/nameDatasets/french.json'
    GERMAN = 'assets/nameDatasets/german.json'
    # GREEK    = 'assets/nameDatasets/greek.json'
    IRISH = 'assets/nameDatasets/irish.json'
    # ITALIAN  = 'assets/nameDatasets/italian.json'
    JAPANESE = 'assets/nameDatasets/japanese.json'
    # RUSSIAN  = 'assets/nameDatasets/russian.json'
    # TURKISH  = 'assets/nameDatasets/turkish.json'


def weightedChoice(weightMap: dict, terminatorMultiplier=5):
    laplaceList = []
    lcd = round(1 / min(weightMap.values()))
    for char in weightMap:
        weight = round(weightMap[char] * lcd)
        laplaceList += weight * [char] if char != TERMINATOR else round(weight * terminatorMultiplier) * [char]
    return random.choice(laplaceList)


def generateMapFromData(path):
    file = open(path, encoding='utf-8')
    data = [line.lower().strip() + TERMINATOR for line in file.readlines()]
    checksum = hashlib.md5(file.read().encode())
    checksumFile = open(f'{path[:-4]}-checksum.txt', 'w', encoding='utf-8')
    checksumFile.write(checksum.hexdigest())
    checksumFile.close()
    file.close()
    sequenceMap = {}
    for r in range(minSeqRange, maxSeqRange + 1):
        sequenceMap[r] = {}
        for word in data:
            for i in range(0, len(word)):
                sequence = word[i - r:i] if i - r >= 0 else (r - i) * '\0' + word[0:i]
                nextChar = word[i]
                if sequence in sequenceMap[r]:
                    if nextChar in sequenceMap[r][sequence]:
                        sequenceMap[r][sequence][nextChar] += 1
                    else:
                        sequenceMap[r][sequence][nextChar] = 1
                else:
                    sequenceMap[r][sequence] = {nextChar: 1}
    for seqRange in sequenceMap:
        for sequence in sequenceMap[seqRange]:
            total = sum(sequenceMap[seqRange][sequence].values())
            for char in sequenceMap[seqRange][sequence]:
                sequenceMap[seqRange][sequence][char] /= total
    sequenceMap['original'] = []
    for word in data:
        sequenceMap['original'].append(word)
    return sequenceMap


def sampleChanged(jsonpath):
    fileNameWithoutExtension = jsonpath[:-5]
    checksumPath = f'{fileNameWithoutExtension}-checksum.txt'
    if os.path.exists(checksumPath):
        checksumFile = open(checksumPath, 'r', encoding='utf-8')
        sampleFile = open(f'{jsonpath[:-5]}.txt', 'r', encoding='utf-8')
        hashMatches = hashlib.md5(sampleFile.read().encode()) == checksumFile.read()
        checksumFile.close()
        sampleFile.close()
        return not hashMatches
    else:
        Path(checksumPath).touch()
        return True


def getMarkowMap(jsonpath):
    if jsonpath not in compiled:
        if sampleChanged(jsonpath):
            jsonfile = open(jsonpath, 'w', encoding='utf-8')
            samplePath = f'{jsonpath[:-5]}.txt'
            sequenceMap = generateMapFromData(samplePath)
            json.dump(sequenceMap, jsonfile)
            jsonfile.close()
        compiled.append(jsonpath)
    jsonfile = open(jsonpath, 'r', encoding='utf-8')
    stringContent = jsonfile.read()
    markowMap = json.loads(stringContent)
    jsonfile.close()
    return markowMap


def randomName(jsonpath, amount=1):
    markowMap = getMarkowMap(jsonpath)
    return list(generateName(markowMap) for _ in range(0, amount)) if amount > 1 else generateName(markowMap)


def generateName(markowMap, recursion=0):
    result = weightedChoice(markowMap[str(minSeqRange)][minSeqRange * '\0'])
    i = 0
    while result[-1] != TERMINATOR:
        for seqRange in range(maxSeqRange, minSeqRange - 1, -1):
            sequence = result[i + 1 - seqRange:i + 1] if i - seqRange >= 0 else (seqRange - i - 1) * '\0' + result[
                                                                                                            0:i + 1]
            if sequence in markowMap[str(seqRange)].keys():
                key = weightedChoice(markowMap[str(seqRange)][sequence], terminatorMultiplier=i * 2)
                result += key
                i += 1
                break
            if seqRange == minSeqRange:
                return generateName(markowMap, recursion + 1)
    if result in markowMap['original'] and random.randint(0, originality - recursion) != 0:
        return generateName(markowMap, recursion + 1)
    return result.title()[:-1]


def generateFirstNames(culture, numberOfNames=1):
    return randomName(culture.value, numberOfNames)


def generateLastNames(culture, numberOfNames=1):
    jsonpath = culture.value
    fileNameWithoutExtension = jsonpath[:-5]
    lastNamePath = f'{fileNameWithoutExtension}-surnames.json'
    return randomName(lastNamePath, numberOfNames)


def generateCharacterName(culture=None, generateLastName=True, generateMiddleName=True):
    culture = random.choice(list(Cultures)) if culture is None else culture
    firstName = generateFirstNames(culture)
    middleName = generateFirstNames(culture) if random.randint(0,
                                                               10) == 0 and generateMiddleName and generateLastName else ''
    lastName = generateLastNames(culture) if generateLastName else ''

    return f'{firstName} {middleName[0] + ". " if len(middleName) > 0 else ""}{lastName}'
