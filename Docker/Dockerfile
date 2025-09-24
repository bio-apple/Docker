FROM alpine AS nextclade
# glibc+conda+nextclade v3.8.2
RUN apk update && \
    apk add --no-cache bash openjdk21 git && mkdir -p /lib64/ && \
    wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub && \
    wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.35-r1/glibc-2.35-r1.apk && \
    apk add --no-cache --force-overwrite glibc-2.35-r1.apk && \
    rm glibc-2.35-r1.apk && ln -s /usr/glibc-compat/lib/* /lib64/ && \
    wget -q -O /opt/Miniforge3-Linux-x86_64.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh && \
    bash /opt/Miniforge3-Linux-x86_64.sh -f -b -p /opt/conda/ && rm -rf /opt/Miniforge3-Linux-x86_64.sh /var/cache/apk/* && \
    cd /bin/ && wget -O nextclade https://github.com/nextstrain/nextclade/releases/download/3.8.2/nextclade-x86_64-unknown-linux-musl && chmod u+x ./nextclade

FROM nextclade AS pangolin
RUN git clone https://github.com/cov-lineages/pangolin.git && cd pangolin/ &&  \
    /opt/conda/bin/mamba env create -f environment.yml --name pangolin &&  \
    /opt/conda/envs/pangolin/bin/pip install . &&  rm -rf /opt/pangolin/ && \
    /opt/conda/bin/conda clean -a -y \

#version SnpEff 5.1d
FROM pangolin AS snpeff
COPY snpEff_latest_core.zip /opt/
RUN mkdir -p /software/ && cd /software/ && mv /opt/snpEff_latest_core.zip /software/  && \
    unzip snpEff_latest_core.zip && rm /software/snpEff_latest_core.zip && mkdir -p /software/snpEff/data/ && \
    rm -rf /software/snpEff/snpEff.config
COPY snpEff.config /software/snpEff/
COPY virus.gbk.tar.gz /software/snpEff/data
COPY build.sh /opt/
RUN cd /software/snpEff/data && tar xzvf virus.gbk.tar.gz && rm -rf virus.gbk.tar.gz && sh /opt/build.sh
ENV PATH=/opt/conda/envs/pangolin/bin:$PATH