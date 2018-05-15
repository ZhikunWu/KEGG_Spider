#!/usr/bin/env python
import requests
import lxml
from lxml import etree
import collections
import argparse

#usage: python getKOinformation.py --KO KO_file.txt --out KO_infor.txt

__author__ = "Zhikun Wu"
__email__ = "598466208@qq.com"
__date__ = "2018.05.15"

def get_KO_record(KO):
    """
    input:
    K00699

    output:
    KOInformation (two level dict) 
    name    UGT
    defination      glucuronosyltransferase ec:2.4.1.17
    pathway ['ko00040', 'ko00053', 'ko00140', 'ko00830', 'ko00860', 'ko00980', 'ko00982', 'ko00983', 'ko01100', 'ko01110', 'ko05204']
    pathway_desc    ['Pentose and glucuronate interconversions', 'Ascorbate and aldarate metabolism', 'Steroid hormone biosynthesis', 'Retinol metabolism', 
    module  ['M00014', 'M00129']
    module_desc     ['Glucuronate pathway (uronate pathway)', 'Ascorbate biosynthesis, animals, glucose-1P => ascorbate']
    disease ['H00208', 'H01593', 'H02054', 'H02055']
    disease_desc    ['Hyperbilirubinemia', 'Osteoporosis', 'Crigler-Najjar syndrome', 'Gilbert syndrome']
    GO      ['GO:0003981']
    Cazy    ['GT1']
    RN      ['R01383', 'R02358', 'R02389', 'R02478', 'R02502', 'R02902', 'R03091', 'R04352', 'R04353', 'R04354', 'R04683', 'R07106', 'R08259', 'R08261', 'R0
    other_dbs       ['R01383', 'R02358', 'R02389', 'R02478', 'R02502', 'R02902', 'R03091', 'R04352', 'R04353', 'R04354', 'R04683', 'R07106', 'R08259', 'R082
    other_dbs_href  ['/dbget-bin/www_bget?rn:R01383', '/dbget-bin/www_bget?rn:R02358', '/dbget-bin/www_bget?rn:R02389', '/dbget-bin/www_bget?rn:R02478', '/d
    genes   ['10720', '10941', '54490', '54575', '54576', '54577', '54578', '54579', '54600', '54657', '54658', '54659', '574537', '7363', '7364', '7365', '
    reference       3931633
    author  Green MD, Falany CN, Kirkpatrick RB, Tephly TR
    title   Strain differences in purified rat hepatic 3 alpha-hydroxysteroid UDP-glucuronosyltransferase.
    journal Biochem J 230:403-9 (1985)
    doi     10.1042/bj2300403
    linkDB  http://www.genome.jp/dbget-bin/get_linkdb?orthology+K00699
    """
    # KO = "K00699"
    KOInformation = collections.defaultdict(dict)
    ### The main url
    url = "http://www.kegg.jp/dbget-bin/www_bget?ko:{}".format(KO)
    r = requests.get(url)
    status_code = r.status_code
    if status_code == 200:
        ### get the html file
        text = r.text
        html = etree.HTML(text)
        ### get the information
        #name and defination
        names = html.xpath("//td[@class='td41' and @style]/div[@style]/div[@style]/text()")
        if len(names) != []:
            name = names[0]
            KOInformation[KO]['name'] = name
        defination_part1 = html.xpath("//td[@class='td40']/div[@style]/div[@style]/text()")
        defination_part2 = html.xpath("//td[@class='td40']/div[@style]/div[@style]/a/@href")
        defination = defination_part1[0].split("[")[0] + defination_part2[0].split("?")[-1]
        KOInformation[KO]['defination'] = defination

        ### pathway and descriotion
        pathway = html.xpath("//td[@class='td41']/table/tr/td/nobr/a[@href]/text()")
        pathway_desc = html.xpath("//td[@class='td41']/table/tr/td/text()")
        pathway_desc = [k for k in pathway_desc if len(k.strip()) != 0]
        KOInformation[KO]['pathway'] = pathway
        KOInformation[KO]['pathway_desc'] = pathway_desc

        ### module and disease
        module = html.xpath("//td[@class='td40' and @style]/table[@style]/tr/td/nobr/a[@href]/text()")
        module_desc = html.xpath("//td[@class='td40' and @style]/table[@style]/tr/td/nobr/a[@href]/../../../td[position()=2]/text()")
        if len(module) == len(module_desc):
            KOInformation[KO]['module'] = module
            KOInformation[KO]['module_desc'] = module_desc

        disease = html.xpath("//td[@class]/div/table/tr/td/nobr/a/text()")
        disease_desc = html.xpath("//td[@class='td41']/div/table/tr/td/text()")
        if len(disease) == len(disease_desc):
            KOInformation[KO]['disease'] = disease
            KOInformation[KO]['disease_desc'] = disease_desc

        ### brite and other dbs
        brite = html.xpath("//td[@class='td40']/div/nobr/a/text()")
        # pathway_desc = html.xpath("//td[@class='td40']/div/nobr/text()")

        other_dbs = html.xpath("//td[@class='td41']/table/tr/td/a[@href]/text()")
        other_dbs_href = html.xpath("//td[@class='td41']/table/tr/td/a/@href")
        GO_list = []
        Cazy_list = []
        RN_list = []
        COG_list = []
        for r, v in zip(other_dbs_href, other_dbs):
            if "geneontology" in r:
                GO_list.append("GO:" + v)
            elif "cazy" in r:
                Cazy_list.append(v)
            elif "dbget-bin" in r:
                RN_list.append(v)
            elif "cddsrv" in r:
                COG_list.append(v)
        if GO_list != []:
            KOInformation[KO]["GO"] = GO_list
        if Cazy_list != []:
            KOInformation[KO]["Cazy"] = Cazy_list
        if RN_list != []:
            KOInformation[KO]["RN"] = RN_list
        if COG_list != []:
            KOInformation[KO]["COG"] = COG_list

        if len(other_dbs) == len(other_dbs_href):
            KOInformation[KO]['other_dbs'] = other_dbs
            KOInformation[KO]['other_dbs_href'] = other_dbs_href

        ### genes
        gene1 = html.xpath("//td[@class='td40' and @style]/table[@style]/tr/td/a[@href]/text()")
        gene2 = html.xpath("//td[@class='td40' and @style]/div[@class]/table[@style]/tr/td/a[@href]/text()")
        KOInformation[KO]['genes'] = gene1 + gene2

        ### reference, authors, title and journal 
        PMIDs = html.xpath("//td[@class='td41' and @style]/div[@style]/a[@href]/text()")
        PMID = PMIDs[0]
        KOInformation[KO]['reference'] = PMID

        authors = html.xpath("//td[@class='td40' and @ style]/div[@style]/text()")
        author = authors[0]
        KOInformation[KO]['author'] = author

        titles = html.xpath("//td[@class='td41' and @style]/div[@style]/text()")
        print(titles)
        if len(titles) >= 2:
            title = titles[1]
            KOInformation[KO]['title'] = title

        journals = html.xpath("//td[@class='td40' and @style]/div[@style]/text()")
        if len(journals) >= 2:
            journal = journals[1]
            KOInformation[KO]['journal'] = journal

        dois = html.xpath("//td[@class='td40' and @style]/div[@style]//a[@href]/text()")
        print(dois)
        if len(dois) != []:
            doi = dois[-1]
            KOInformation[KO]['doi'] = doi

        ### linkDB
        linkDBs = html.xpath("//td[@class='td41' and 'style']/a/@href")
        print(linkDBs)
        if linkDBs != []:
            linkDB = linkDBs[0]
            KOInformation[KO]['linkDB'] = linkDB
        else:
            KOInformation[KO]['linkDB'] = None

        return KOInformation

def get_infor_from_KO_file(KO_file, out_file):
    """
    The values of these keys are list:
    pathway, pathway_desc, module, module_desc, 
    disease, disease_desc, GO, RN, COG, 
    other_dbs, other_dbs_href, genes
    """
    in_h = open(KO_file, 'r')
    out_h = open(out_file, 'w')
    for line in in_h:
        line = line.strip()
        if line.startswith("K"):
            KOInformation = get_KO_record(line)
            for ko in KOInformation:
                Infor = KOInformation[ko]
                for k in  Infor:
                    value = Infor[k]
                    out_h.write("%s\t%s\n" % (k, value))

def main():
    parser = argparse.ArgumentParser(description="Get the information for the given KEGG orthology.")
    parser.add_argument("-k", "--KO", help="The input file containing KO number with one per line.")
    parser.add_argument("-o", "--out", help="The output file.")
    args = parser.parse_args()
    get_infor_from_KO_file(args.KO, args.out)

if __name__ == "__main__":
    main()
