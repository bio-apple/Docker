All images should use **Alpine** as the base image. 

For building bioinformatics-related images, use **Mamba** instead of Conda. 

Do not set a mirror source, and the image can be built in stages to aim for the smallest Dockerfile.

#   1.The commonly used Docker analysis commands are as follows.

Stop all Docker containers

    docker ps -a | grep "Exited" | awk '{print $1 }'|xargs docker stop
    
delete all containers

    docker ps -a | grep "Exited" | awk '{print $1 }'|xargs docker rm

disable Cache with **--no-cache**

    docker build --no-cache -t my_image .

clean Up Build Cache
    
    docker builder prune -f

save and load images

    docker save -o my_ubuntu_v3.tar runoob/ubuntu:v3
    docker load --input my_ubuntu_v3.tar

#   2.Several important practical use cases of the images are as follows.

**minimal bioinformatics environment**

    FROM alpine:latest
    RUN apk update && \
        apk add --no-cache bash openjdk21 git && mkdir -p /lib64/ /ref/ /script/ /raw_data/ /outdir/ && \
        wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub && \
        wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.35-r1/glibc-2.35-r1.apk && \
        apk add --no-cache --force-overwrite glibc-2.35-r1.apk && \
        rm glibc-2.35-r1.apk && ln -s /usr/glibc-compat/lib/* /lib64/ && \
        wget -q -O /opt/Miniforge3-Linux-x86_64.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh && \
        bash /opt/Miniforge3-Linux-x86_64.sh -f -b -p /opt/conda/ && rm -rf /opt/Miniforge3-Linux-x86_64.sh /var/cache/apk/*

**metagenomic data analysis:https://github.com/bio-apple/metagenomics**


**COVID-19:** and other microbiome detection based on amplicon methods is as follows. This is a good example of building the image in stages.

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


# 3.Error resolution

## 3-1:ERROR: failed to solve: DeadlineExceeded: DeadlineExceeded: DeadlineExceeded:
*add the following to /etc/docker/daemon.json* https://blog.csdn.net/weixin_41463944/article/details/135348288

    {
        "features": {
            "buildkit": false
        }
    }

Docker Mirror Configuration Reference for Chinese Users：https://github.com/dongyubin/DockerHub

*add the mirror link to /etc/docker/daemon.json* https://www.coderjia.cn/archives/dba3f94c-a021-468a-8ac6-e840f85867ea

     {
        "registry-mirrors": [
            "https://docker-0.unsee.tech"
        ]
    }
For Mac users, the **daemon.json** link is：

    ~/.docker/daemon.json