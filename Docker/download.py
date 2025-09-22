import json
import os,re
import subprocess

java="java"
snpEff="/software/snpEff/snpEff.jar"
infile=open("/Users/yfan/Desktop/RPIP_report/knowledge/dragen_4.3/DME+_1.1.0_AMR_Lookup/DME+_RPIPvAMRvariants.RPIP-6.5.1.txt","r")
all_ref=[]
all_ref.append('NC_045512')
for line in infile:
    text = json.loads(line.strip())
    ###################################################get all reference id
    if not text['accession'] in all_ref:
        all_ref.append(text['accession'])
    variant=""
    for key in text['variants']:
        if key['secondary_references']:
            for key1 in key['secondary_references']:
                if not key1['accession'] in all_ref:
                    all_ref.append(key1['accession'])
infile.close()
infile=open("/Users/yfan/Desktop/RPIP_report/knowledge/dragen_4.3/DME+_1.1.0_AMR_Lookup/DME+_VSPv2vAMRvariants.VSPv2-2.7.0.txt","r")
for line in infile:
    text = json.loads(line.strip())
    ###################################################get all reference id
    if not text['accession'] in all_ref:
        print(text['accession'])
        all_ref.append(text['accession'])
    variant = ""
    for key in text['variants']:
        if key['secondary_references']:
            for key1 in key['secondary_references']:
                if not key1['accession'] in all_ref:
                    print(key1['accession'])
                    all_ref.append(key1['accession'])
infile.close()
subprocess.call("echo \'data.dir =/software/snpEff/data/' >snpEff.config && rm -rf build.sh && mkdir -p virus", shell=True)
for key in all_ref:
    subprocess.call('echo %s.genome:%s >>snpEff.config'%(key,key), shell=True)
    subprocess.call('echo \'%s -jar %s build -genbank -v %s\'>> build.sh'%(java,snpEff,key),shell=True)
    subprocess.call("mkdir -p virus/%s"%key, shell=True)
    gb="wget -O virus/%s/genes.gbk 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=%s&rettype=gb&retmode=text\'"%(key,key)
    subprocess.check_call(gb,shell=True)

subprocess.call('cd virus/ && tar czvf virus.gbk.tar.gz ./ && mv virus.gbk.tar.gz ../ && rm -rf virus/', shell=True)