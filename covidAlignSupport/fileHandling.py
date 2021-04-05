import os

pe1IdentifierStringEnv = os.environ.setdefault("PE1IDENTIFIER", "_R1")
pe2IdentifierStringEnv = os.environ.setdefault("PE2IDENTIFIER", "_R2")
leaveIlluminaFileInfoEnv = "LEAVEILLUMINAFILEINFO" in os.environ

fastqEndings = [".fastq",
                ".fastq.gz",
                ".fq",
                ".fq.gz"]


class ReadSet:

    def __init__(self, pe1FilePath:str, pe2FilePath:str=None):
        if not os.path.isfile(pe1FilePath):
            raise FileNotFoundError("Unable to fine pe1 file at %s" %pe1FilePath)
        if pe2FilePath:
            self.isPaired=True
            if not os.path.isfile(pe2FilePath):
                raise FileNotFoundError("Unable to find pe2 file at %s" %pe2FilePath)
        else:
            self.isPaired = False
        self.pe1Raw = pe1FilePath
        self.pe2Raw = pe2FilePath
        self.pe1AdapterTrim = None
        self.pe2AdapterTrim = None
        self.pe1QualTrim = None
        self.pe2QualTrim = None
        self.singletonQualTrim = None
        self.rawPairedBAM = None
        self.rawSingleBAM = None
        self.sortedPairedBAM = None
        self.sortedSingleBAM = None
        self.mergedBAM = None
        self.finalBAM = None
        self.finalBAMIndex = None
        self.readGroupString = ""

    @property
    def fastqRaw(self):
        if not self.isPaired:
            return self.pe1Raw
        else:
            raise ValueError("Unable to return unspecified paired end on paired files")

    @property
    def fastqAdapterTrim(self):
        if not self.isPaired:
            return self.pe1AdapterTrim
        else:
            raise ValueError("Unable to return unspecified paired end on paired files")

    @property
    def fastqQualTrim(self):
        if not self.isPaired:
            return self.pe1QualTrim
        else:
            raise ValueError("Unable to return unspecified paired end on paired files")

    @property
    def rawBAM(self):
        if not self.rawSingleBAM:
            return self.pe1QualTrim
        else:
            raise ValueError("Unable to return unspecified paired end on paired files")

    @property
    def sortedBAM(self):
        if not self.isPaired:
            return self.sortedSingleBAM
        else:
            raise ValueError("Unable to return unspecified paired end on paired files")

    @property
    def adapterTrimmed(self):
        return self.pe1AdapterTrim and self.pe1Raw != self.pe1AdapterTrim

    @property
    def qualityTrimmed(self):
        return self.pe1AdapterTrim and self.pe1Raw != self.pe1AdapterTrim

    def __str__(self):
        return "%s|%s" %(self.pe1Raw, self.pe2Raw)



def stripFastqExtensions(fileName:str):
    if fileName.endswith(".gz"):
        fileBase = fileName[:-3]
    else:
        fileBase = fileName
    if fileBase.endswith(".fastq"):
        fileBase = fileBase[:-6]
    elif fileBase.endswith(".fq"):
        fileBase = fileBase[:-3]
    return fileBase


def fastqBasicPrep(fastqFilePath:str, outputFolder:str=None):
    inputFolder, inputFastq = os.path.split(os.path.abspath(fastqFilePath))
    if not outputFolder:
        outputFolder = inputFolder
    if not os.path.isdir(outputFolder):
        if os.path.isfile(outputFolder):
            raise NotADirectoryError("Output folder %s is already an existing file." %outputFolder)
        os.makedirs(outputFolder)
    return outputFolder, inputFastq


def groupFastqsFromFolder(inputFolder:str, leaveIlluminaFileInfo:bool=leaveIlluminaFileInfoEnv):
    if not os.path.isdir(inputFolder):
        raise NotADirectoryError("Unable to find input directory %s" %inputFolder)
    unfilteredFiles = os.listdir(inputFolder)
    filteredFiles = []
    for file in unfilteredFiles:
        if not os.path.isfile(os.path.join(inputFolder, file)):
            continue
        for fastqEnding in fastqEndings:
            if file.endswith(fastqEnding):
                filteredFiles.append(file)
                break
    pairedEndMatcher = {}
    for file in filteredFiles:
        if pe1IdentifierStringEnv in file and pe2IdentifierStringEnv in file:
            raise ValueError("File %s appears to have identifiers for both pe1 and pe2" %(os.path.join(inputFolder, file)))
        if not leaveIlluminaFileInfo:
            fileBase = file.split(".")[0].split("_")[0]
        else:
            if pe1IdentifierStringEnv in file:
                fileBase = stripFastqExtensions(file.replace(pe1IdentifierStringEnv, ""))
            elif pe2IdentifierStringEnv in file:
                fileBase = stripFastqExtensions(file.replace(pe2IdentifierStringEnv, ""))
            else:
                fileBase = file
        if not fileBase in pairedEndMatcher:
            pairedEndMatcher[fileBase] = []
        pairedEndMatcher[fileBase].append(file)
    readSets = {}
    for baseName, fileSet in pairedEndMatcher.items():
        if len(fileSet) == 1:
            readSets[baseName] = ReadSet(os.path.join(inputFolder, fileSet[0]))
        elif len(fileSet) == 2:
            firstInSet, secondInSet = fileSet
            if pe1IdentifierStringEnv in firstInSet:
                readSets[baseName] = ReadSet(os.path.join(inputFolder, firstInSet), os.path.join(inputFolder, secondInSet))
            elif pe2IdentifierStringEnv in firstInSet:
                readSets[baseName] = ReadSet(os.path.join(inputFolder, secondInSet), os.path.join(inputFolder, firstInSet))
            elif pe1IdentifierStringEnv in secondInSet:
                readSets[baseName] = ReadSet(os.path.join(inputFolder, secondInSet), os.path.join(inputFolder, firstInSet))
            elif pe2IdentifierStringEnv in secondInSet:
                readSets[baseName] = ReadSet(os.path.join(inputFolder, firstInSet), os.path.join(inputFolder, secondInSet))
            else:
                print("WARNING: Unable to positively identify PE1 and PE2 from %s and %s" %(firstInSet, secondInSet))
                readSets[baseName] = ReadSet(os.path.join(inputFolder, firstInSet), os.path.join(inputFolder, secondInSet))
    return readSets



