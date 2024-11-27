FROM biocontainers/bwa:v0.7.17_cv1

USER root

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get install -y python3-pip && \
    apt-get install -y samtools && \
    apt-get install -y zlib1g-dev && \
    pip3 install pysam==0.16.0.1

WORKDIR /opt
RUN wget https://github.com/najoshi/sickle/archive/v1.33.tar.gz && \
    tar -xvf v1.33.tar.gz && \
    mv sickle-1.33 sickle && \
    cd sickle && \
    make && \
    ln -s /opt/sickle/sickle /usr/bin/sickle

WORKDIR /opt
RUN wget -O scythe.zip https://github.com/vsbuffalo/scythe/archive/master.zip && \
    unzip scythe.zip && \
    mv scythe-master scythe && \
    cd scythe && \
    make && \
    ln -s /opt/scythe/scythe /usr/bin/scythe

WORKDIR /home/biodocker

COPY ./references /home/biodocker/references

RUN cd references . && \
    bwa index ./Sars_cov_2.ASM985889v3.dna_sm.toplevel.fa.gz && \
    cd ..

COPY  ./covidAlignSupport /home/biodocker/covidAlignSupport

COPY ./*.py /home/biodocker

RUN chown -R biodocker /home/biodocker


USER biodocker

WORKDIR /home/biodocker

ENV PYTHONUNBUFFERED=1

CMD python3 /home/biodocker/main.py