All images should use **Alpine** as the base image. For building bioinformatics-related images, use **Mamba** instead of Conda. 
Do not set a mirror source, and the image can be built in stages to aim for the smallest Dockerfile.

### 1.Based on the above requirements, we have provided the minimal bioinformatics environment **biobase**.

    FROM alpine:latest
    RUN apk update && \
        apk add --no-cache bash openjdk21 git && mkdir -p /lib64/ /ref/ /script/ /raw_data/ /outdir/ && \
        wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub && \
        wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.35-r1/glibc-2.35-r1.apk && \
        apk add --no-cache --force-overwrite glibc-2.35-r1.apk && \
        rm glibc-2.35-r1.apk && ln -s /usr/glibc-compat/lib/* /lib64/ && \
        wget -q -O /opt/Miniforge3-Linux-x86_64.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh && \
        bash /opt/Miniforge3-Linux-x86_64.sh -f -b -p /opt/conda/ && rm -rf /opt/Miniforge3-Linux-x86_64.sh /var/cache/apk/*

### 2.The Docker image file for metagenomic data analysis is as follows.

    FROM alpine:latest
    RUN apk add --no-cache bash && mkdir -p /lib64/ /ref/ /script/ /raw_data/ /outdir/ && \
        wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub && \
        wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.35-r1/glibc-2.35-r1.apk &&  \
        apk add --no-cache --force-overwrite glibc-2.35-r1.apk && rm glibc-2.35-r1.apk && ln -s /usr/glibc-compat/lib/* /lib64/ && \
        wget -q -O /opt/Miniforge3-Linux-x86_64.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh && \
        bash /opt/Miniforge3-Linux-x86_64.sh -f -b -p /opt/conda/ && rm -rf /opt/Miniforge3-Linux-x86_64.sh /var/cache/apk/* && \
        /opt/conda/bin/mamba create --name rgi --channel conda-forge --channel bioconda --channel defaults rgi &&  \
        /opt/conda/bin/conda config --add channels ursky && \
        /opt/conda/bin/mamba create -y --name metawrap --channel ursky  \
        --channel conda-forge --channel bioconda --channel defaults blas=2.5=mkl biopython metawrap-mg=1.3.2 checkm-genome && \
        /opt/conda/bin/mamba create --name gtdbtk --channel conda-forge --channel bioconda --channel defaults gtdbtk && \
        /opt/conda/bin/mamba create --name metaphlan --channel conda-forge --channel bioconda --channel defaults metaphlan && \
        /opt/conda/bin/mamba run -n rgi mamba install --channel conda-forge --channel bioconda --channel defaults staramr  \
        quast minimap2 megahit cd-hit spades freebayes fastqtk seqtk bbmap fastp fastqc prinseq cutadapt multiqc trimmomatic  \
        bcftools prokka covtobed fastani megan kraken2 krakentools krona bracken drep coverm &&  \
        /opt/conda/bin/conda clean -a -y && /opt/conda/bin/mamba clean -a -y
    ENV LD_LIBRARY_PATH=/lib/:/lib64/:$LD_LIBRARY_PATH

### 3.The Docker image for COVID-19 and other microbiome detection based on amplicon methods is as follows.This is a good example of building the image in stages, but an additional step is required to copy a jvarkit.jar file into the image.   

    FROM alpine AS nextclade
    # glibc+conda+nextclade
    RUN apk update && \
        apk add --no-cache bash openjdk21 git && mkdir -p /lib64/ /ref/ /script/ /raw_data/ /outdir/ && \
        wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub && \
        wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.35-r1/glibc-2.35-r1.apk && \
        apk add --no-cache --force-overwrite glibc-2.35-r1.apk && \
        rm glibc-2.35-r1.apk && ln -s /usr/glibc-compat/lib/* /lib64/ && \
        wget -q -O /opt/Miniforge3-Linux-x86_64.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh && \
        bash /opt/Miniforge3-Linux-x86_64.sh -f -b -p /opt/conda/ && rm -rf /opt/Miniforge3-Linux-x86_64.sh /var/cache/apk/* && \
        cd /bin/ && wget -O nextclade https://github.com/nextstrain/nextclade/releases/latest/download/nextclade-x86_64-unknown-linux-musl && chmod u+x ./nextclade
    
    FROM nextclade AS pangolin
    RUN git clone https://github.com/cov-lineages/pangolin.git && cd pangolin/ &&  \
        /opt/conda/bin/mamba env create -f environment.yml --name pangolin &&  \
        /opt/conda/envs/pangolin/bin/pip install . &&  rm -rf /opt/pangolin/ && \
        /opt/conda/bin/conda clean -a -y
    
    FROM pangolin AS micro2amplicon
    COPY jvarkit.jar /software/
    RUN /opt/conda/bin/mamba install --channel conda-forge --channel bioconda --channel defaults ivar=1.3 trimmomatic  \
        bowtie2 bbmap fastp seqtk samtools bedtools bcftools bwa prinseq cutadapt drep
    RUN /opt/conda/bin/pip3 install seaborn matplotlib numpy pysam pandas

**The commonly used Docker analysis commands are as follows.**

*停止所有容器*

    docker ps -a | grep "Exited" | awk '{print $1 }'|xargs docker stop
    
*删除所有容器*

    docker ps -a | grep "Exited" | awk '{print $1 }'|xargs docker rm

*镜像保存与加载*

    docker save -o my_ubuntu_v3.tar runoob/ubuntu:v3
    docker load --input my_ubuntu_v3.tar
    
*镜像上传docker hub*

    docker tag biobase fanyucai1/