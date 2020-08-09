from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from typing import NamedTuple,Dict,List,Any,Tuple
from concurrent.futures import ThreadPoolExecutor
import argparse

import vcfparser
from vcfparser import ParseVcf


#driver.find_element_by_class_name("_3FRCZ") CONTACT
#msg_box = driver.find_element_by_xpath("//*[@id='main']/footer/div[1]/div[2]/div/div[2]")

WHATSAPP_WEB_APP = "https://web.whatsapp.com/"
ENTER = Keys.ENTER

class PageElements(NamedTuple):
    ContactSearchBOX:webdriver.remote.webelement.WebElement
    MsgBox:webdriver.remote.webelement.WebElement
    #TODO: add more elements such as images icon and document

    @classmethod
    def set_elem(cls,m:Dict[Any,Any]) :
        contact,msgbox = [m[x] for x in list(cls.__dict__["_fields"])]
        return cls.__new__(cls,contact,msgbox)


class WhatsappB:
    def __init__(self,vcffile:str,text:str,image:str,document:str):
        self.vcffile = vcffile
        self.text = text
        self.image = image
        self.document = document
        #self.contacts = List[Any]
        self.failedContact = List[Any]
        try:
            self.driver = webdriver.Chrome()
        except Exception as e:
            raise Exception("Cannot load chrome Driver",type(e).__name__(),e)

    def ExtractContacts(self):
        #TODO: extract contacts from vcf file
        pvcf = ParseVcf(self.vcffile)
        pvcf.Parse()
        self.contacts = pvcf.GetContacts
    
    def GetPageElements(self) -> PageElements:
        contactF = self.driver.find_element_by_class_name("_3FRCZ")
        msgF = self.driver.find_element_by_xpath("//*[@id='main']/footer/div[1]/div[2]/div/div[2]")
        pageCnt = dict(ContactSearchBOX=contactF,MsgBox=msgF)
        pageElmnt = PageElements.set_elem(pageCnt)
        return pageElmnt


    @staticmethod
    def MapNums(contacts:List[Any]) -> vcfparser.Contact :
        p = GetPageElements()
        currentContact = None
        for cnt in contacts:
            p.ContactSearchBOX.send_keys(cnt.N)
            p.ContactSearchBOX.send_keys(ENTER)
            p.MsgBox.send_keys(self.text)
            p.MsgBox.send_keys(ENTER)
            currentContact = cnt
        return currentContact

    def run(self) :
        start = input("Scan the QR Code then Enter y if you're done: ")
        if start.lower() == "y" or start.upper() == "Y":
            if self.text != "" and len(self.contacts) != 0 :
                with ThreadPoolExecutor(max_workers=1) as executor:
                    cnts = executor.map(MapNums,self.contacts)
                    for c in cnts:
                        print("sent To",c)
                self.Driver.close()

def FlagHandler() -> Tuple[str]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vcffile",type=str, help="Put the vcf file that contains contact you want ot ")
    parser.add_argument("--image",type=str,help="Put the image path if you need to send image to your contacts")
    parser.add_argument("--document",type=str,help="Document length")
    parser.add_argument("--text",type=str,help="text message to send")
    args = parser.parse_args() 
    return args.vcffile, args.image, args.document,args.text

if __name__ == "__main__":
    vcffile, image , document, text = FlagHandler()
    WhatsappB(vcffile,text,image,document).run()
