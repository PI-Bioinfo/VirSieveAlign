import os
try:
    import fileHandling
except ImportError:
    from . import fileHandling

scytheExecutable = "/usr/bin/scythe"


def runScythe(inputFilePath:str, outputFolder:str=None, adaptersFilePath:str=None):
    if not os.path.isfile(inputFilePath):
        raise FileNotFoundError("Unable to find input file for adapter trimming at %s" % inputFilePath)
    if not adaptersFilePath:
        return False
    if not os.path.isfile(adaptersFilePath):
        raise FileNotFoundError("Unable to find adapters file at %s" %adaptersFilePath)
    outputFolder, inputFastq = fileHandling.fastqBasicPrep(inputFilePath, outputFolder)
    outputFileName = fileHandling.stripFastqExtensions(inputFastq) + ".adapterTrim.fastq"
    outputFilePath = os.path.join(outputFolder, outputFileName)
    scytheCommand = "%s -a %s -o %s %s" %(scytheExecutable, adaptersFilePath, outputFilePath, inputFilePath)
    print("RUN: %s" %scytheCommand)
    exitStatus = os.system(scytheCommand)
    if exitStatus != 0:
        raise RuntimeError("Scythe command failed with non-zero exit status of %s" %exitStatus)
    return outputFilePath
