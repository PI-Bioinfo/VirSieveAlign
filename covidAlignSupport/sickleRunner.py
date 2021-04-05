import os
try:
    import fileHandling
except ImportError:
    from . import fileHandling

sickleExecutable = "/usr/bin/sickle"
qualityThreshold = 20
lengthThreshold = 40
qualityEncoding = "sanger"


def runSicklePaired(pe1InputFilePath:str, pe2InputFilePath:str, outputFolder:str=None):
    if not os.path.isfile(pe1InputFilePath):
        raise FileNotFoundError("Unable to find pe1 input file for adapter trimming at %s" % pe1InputFilePath)
    if not os.path.isfile(pe2InputFilePath):
        raise FileNotFoundError("Unable to find pe2 input file for adapter trimming at %s" % pe1InputFilePath)
    outputFolder, inputFastq = fileHandling.fastqBasicPrep(pe1InputFilePath, outputFolder)
    pe1OutputFileName = fileHandling.stripFastqExtensions(os.path.split(pe1InputFilePath)[1]) + ".qualTrim.fastq.gz"
    pe2OutputFileName = fileHandling.stripFastqExtensions(os.path.split(pe2InputFilePath)[1]) + ".qualTrim.fastq.gz"
    singletonFileName = fileHandling.stripFastqExtensions(os.path.split(pe1InputFilePath)[1]) + ".singleton.qualTrim.fastq.gz"
    pe1OutputFilePath = os.path.join(outputFolder, pe1OutputFileName)
    pe2OutputFilePath = os.path.join(outputFolder, pe2OutputFileName)
    singletonOutputFilePath = os.path.join(outputFolder, singletonFileName)
    sickleCommand = "%s pe -f %s -r %s -o %s -p %s -s %s -t %s -l %s -q %s -g" %(sickleExecutable,
                                                                                 pe1InputFilePath,
                                                                                 pe2InputFilePath,
                                                                                 pe1OutputFilePath,
                                                                                 pe2OutputFilePath,
                                                                                 singletonOutputFilePath,
                                                                                 qualityEncoding,
                                                                                 lengthThreshold,
                                                                                 qualityThreshold)
    print("RUN: %s" %sickleCommand)
    exitStatus = os.system(sickleCommand)
    if exitStatus != 0:
        raise RuntimeError("Sickle command failed with non-zero exit status of %s" %exitStatus)
    return pe1OutputFilePath, pe2OutputFilePath, singletonOutputFilePath


def runSickleSingle(inputFilePath:str, outputFolder:str=None):
    if not os.path.isfile(inputFilePath):
        raise FileNotFoundError("Unable to find pe1 input file for adapter trimming at %s" % inputFilePath)
    outputFolder, inputFastq = fileHandling.fastqBasicPrep(inputFilePath, outputFolder)
    outputFileName = fileHandling.stripFastqExtensions(inputFastq) + ".qualTrim.fastq.gz"
    outputFilePath = os.path.join(outputFolder, outputFileName)
    sickleCommand = "%s pe -f %s -o %s -t %s -l %s -q %s -g" %(sickleExecutable,
                                                               inputFilePath,
                                                               outputFilePath,
                                                               qualityEncoding,
                                                               lengthThreshold,
                                                               qualityThreshold)
    print("RUN: %s" %sickleCommand)
    exitStatus = os.system(sickleCommand)
    if exitStatus != 0:
        raise RuntimeError("Sickle command failed with non-zero exit status of %s" %exitStatus)
    return outputFilePath