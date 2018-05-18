#!/usr/bin/env python
import re
import argparse
import sqlite3

#usage: python keggHtext2db.py --kegg  ko00001.keg --database kegg.db

__author__ = "Zhikun Wu"
__email__ = "598466208@qq.com"
__date__ = "2018.05.18"

def parse_kegg_htext(kegg_htext, out_db):
    ### Create database
    con = sqlite3.connect(out_db)
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE PathwayLevel
        (levelA text,
        levelB text,
        pathway text)
    """)

    cursor.execute("""
        CREATE TABLE Pathway
        (pathway text,
        pathway_id text,
        pathway_desc text)
    """)

    cursor.execute("""
        CREATE TABLE PathKO
        (pathway text,
        KO_id text)
    """)

    cursor.execute("""
        CREATE TABLE KODesc
        (KO_id text,
        KO_symbol text,
        KO_desc text)
    """)

    cursor.execute("""
        CREATE TABLE KOEC
        (KO_id text,
        EC_id text)
    """)

    Pathway = []
    PathKO = []
    KODesc = []
    KOEC = []
    ### parse the kegg information
    in_h = open(kegg_htext, "r")
    for line in in_h:
        line = line.strip()
        if line.startswith("A"):
            matchesA = re.findall("\<b\>(.*)\<\/b\>", line)
            if matchesA != []:
                level_A = matchesA[0]
            else:
                print("Please check whether the record '%s' has the pathway class." % line)
        elif line.startswith("B"):
            if line[1:].strip() != '':
                matchesB = re.findall("\<b\>(.*)\<\/b\>", line)
                if matchesB != []:
                    level_B = matchesB[0]
                else:
                    print("Please check whether the record '%s' has the pathway class." % line)
        elif line.startswith("C"):
            path_ids = re.findall("\s+(\d+)\s+", line)
            ### pathway maybe "[ko:ko01007]" or "[BR:ko01007]"
            pathways = re.findall("\[\w+\:(ko\d+)\]", line) 
            descriptions = re.findall("\s+\d+\s+(.*)\s+\[\w+\:", line)
            if path_ids != [] and  pathways != [] and descriptions != []:
                path_id = path_ids[0]
                pathway = pathways[0]
                description = descriptions[0]
                cursor.execute("""
                    INSERT INTO PathwayLevel
                    (levelA, levelB, pathway)
                    VALUES
                    (?, ?, ?);
                """, (level_A, level_B, pathway))
                Pathway.append((pathway, path_id, description))
            else:
                print("Please check whether the record '%s' have the items of path id, pathway and pathway description." % line)
        elif line.startswith("D"):
            KOs = re.findall("\s+(K\d+)\s", line)
            ECs = re.findall("\[EC\:(.*)\]", line)
            Descs = re.findall("D\s+K\d+\s+(.*)\s+\[EC", line)
            if KOs != []  and Descs != []:
                KO = KOs[0]
                Desc = Descs[0]
                symbol_num = Desc.split(";")[0].split(",")
                KO_desc = Desc.split(";")[1].strip()
                PathKO.append((pathway, KO))
                ### insert KO, symbol and description, one KO may have mutiple symbol
                if len(symbol_num) ==1:
                    symbol = symbol_num[0]
                    symbol = symbol.strip()
                    KODesc.append((KO, symbol, KO_desc))
                else:
                    for symbol in symbol_num:
                        symbol = symbol.strip()
                        KODesc.append((KO, symbol, KO_desc))
                ### insert the EC if it exists, one KO may have zero, one or mutiple EC
                if  ECs != []:               
                    EC_num = ECs[0].split()
                    if len(EC_num) == 1:
                        EC = EC_num[0]
                        KOEC.append((KO, EC))
                    else:
                        for EC in EC_num:
                            KOEC.append((KO, EC))
            else:
                if KOs == []:
                    print("Please check whether the record %s have the items of KO." % line)
                elif Descs != []:
                    print("Please check whether the record %s have the items of  description." % line)
    ### Insert uniq record
    for p in list(set(Pathway)):
        cursor.execute("""
        INSERT INTO Pathway
        (pathway, pathway_id, pathway_desc)
        VALUES
        (?, ?, ?);
        """, p) 

    for p in list(set(PathKO)):
        cursor.execute("""
            INSERT INTO PathKO
            (pathway, KO_id)
            VALUES
            (?, ?);
        """, p)

    for k in list(set(KODesc)):
        cursor.execute("""
            INSERT INTO KODesc
            (KO_id, KO_symbol, KO_desc)
            VALUES
            (?, ?, ?);
        """, k)

    for k in list(set(KOEC)):        
        cursor.execute("""
            INSERT INTO KOEC
            (KO_id, EC_id)
            VALUES
            (?, ?);
        """, k)             
    cursor.close()
    con.commit()
    con.close()


def main():
    parser = argparse.ArgumentParser(description="Get the information of KEGG pathway.")
    parser.add_argument("-kegg", "--kegg", help="Input kegg file from web site 'http://www.genome.jp/kegg-bin/get_htext#C298'.")
    parser.add_argument("-d", "--database", help="The output database.")
    args = parser.parse_args()
    parse_kegg_htext(args.kegg, args.database)

if __name__ == "__main__":
    main()