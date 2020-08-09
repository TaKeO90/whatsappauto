#!/usr/bin/env python3.8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from typing import NamedTuple,Dict,List,Any,Tuple
from concurrent.futures import ThreadPoolExecutor
import argparse
import sys
import time

from vcfparser import parse


WHATSAPP_WEB_APP = "https://web.whatsapp.com/"
ENTER = Keys.ENTER



class WhatsappB:
    def __init__(self,vcffile:str,text:str,image:str,document:str):
        self.vcffile = vcffile
        self.text = text
        self.image = image
        self.document = document
        try:
            self.driver = webdriver.Chrome()
            self.driver.get(WHATSAPP_WEB_APP)
        except Exception as e:
            raise Exception("Cannot load chrome Driver",type(e).__name__(),e)


    def ExtractContacts(self) -> List[Any]:
        pvcf = parse.ParseVcf(self.vcffile)
        pvcf.Parse()
        contacts = pvcf.GetContacts()
        return contacts
    


    def MapNums(self,contacts:List[Any]):
        self.failed = []
        for cnt in contacts:
            try : 
                contactSearch = self.driver.find_element_by_class_name("_3FRCZ")
                contactSearch.send_keys(cnt)
                contactSearch.send_keys(ENTER)
                selectedCnt = self.driver.find_element_by_xpath("//span[@title='" + cnt  + "']").click()
                msgF = self.driver.find_element_by_xpath("//*[@id='main']/footer/div[1]/div[2]/div/div[2]")
                msgF.send_keys(self.text)
                msgF.send_keys(ENTER)
                currentContact = cnt
                print(f"sent to => {cnt}")
                time.sleep(0.2)
            except Exception as e :
                self.failed.append(cnt)
                pass

    def run(self) :
        start = input("Scan the QR Code then Enter y if you're done: ")
        if start.lower() == "y" or start.upper() == "Y":
            if self.text != "":
                contacts = self.ExtractContacts()
                self.MapNums(contacts)
                print(f"Failed {len(self.failed)} times ==> {(',').join(self.failed)}")
                time.sleep(1.2)
                self.driver.close()


def FlagHandler(argc:list) -> Tuple[str]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vcffile",type=str, help="Put the vcf file that contains contact you want ot ")
    parser.add_argument("--image",type=str,help="Put the image path if you need to send image to your contacts")
    parser.add_argument("--document",type=str,help="Document length")
    parser.add_argument("--text",type=str,help="text message to send")
    args = parser.parse_args() 
    if len(argc) > 2 :
        return (args.vcffile, args.image, args.document,args.text)
    else :
        parser.print_help()
        sys.exit(1)
        

if __name__ == "__main__":
    vcffile, image , document, text = FlagHandler(sys.argv)
    WhatsappB(vcffile,text,image,document).run()
