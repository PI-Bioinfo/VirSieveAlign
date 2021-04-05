import os
import multiprocessing
try:
    import fileHandling
except ImportError:
    from . import fileHandling

cutadaptEnvironmentName = "cutadaptenv"
cpuCount = multiprocessing.cpu_count()


def runCutadapt(inputFilePath:str, outputFolder:str=None, adaptersFilePath:str=None):
    if not os.path.isfile(inputFilePath):
        raise FileNotFoundError("Unable to find input file for adapter trimming at %s" % inputFilePath)
    if not adaptersFilePath:
        return False
    if not os.path.isfile(adaptersFilePath):
        raise FileNotFoundError("Unable to find adapters file at %s" %adaptersFilePath)
    outputFolder, inputFastq = fileHandling.fastqBasicPrep(inputFilePath, outputFolder)
    outputFileName = fileHandling.stripFastqExtensions(inputFastq) + ".adapterTrim.fastq.gz"
    outputFilePath = os.path.join(outputFolder, outputFileName)
    cutadaptCommand = "conda activate %s; cutadapt -j %s -a FILE:%s -o %s %s; cutadapt conda deactivate" %(cutadaptEnvironmentName, cpuCount, adaptersFilePath, outputFilePath, inputFilePath)
    print("RUN: %s" %cutadaptCommand)
    exitStatus = os.system(cutadaptCommand)
    if exitStatus != 0:
        raise RuntimeError("Scythe command failed with non-zero exit status of %s" %exitStatus)
    return outputFilePath