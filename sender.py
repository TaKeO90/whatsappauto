#!/usr/bin/env python3.8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from typing import NamedTuple,Dict,List,Any,Tuple
from zipfile import ZipFile
from concurrent.futures import ThreadPoolExecutor
import argparse
import sys
import time
import stat
import os
import requests

from vcfparser import parse


WHATSAPP_WEB_APP = "https://web.whatsapp.com/"
ENTER = Keys.ENTER

#CONFIGURATION PROCESS
class Config:
    WINDOWS_LINK = "https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_win32.zip"
    LINUX_LINK = "https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip"
    CHROME_DOWNLOAD_LINK = "https://sites.google.com/a/chromium.org/chromedriver/downloads"
    driver_Path = "./browserdriver"
    driver_name = "chromedriver.zip"
    #NOTE: inform the user that the chrome version we are using is 83 than give him the link where he can download the right version ` CHROME_DOWNLOAD_LINK `

    @classmethod
    def checkFordrivers(cls) -> bool:
        if len((driver:=[x for x in os.listdir(cls.driver_Path) if x == "chromedriver"])) != 0:
            return True
        return False

    @classmethod
    def getDriver(cls, url="") :
        Os = sys.platform
        link = ""
        if Os == "linux":
            link = cls.LINUX_LINK
        elif Os == "windows":
            link = cls.WINDOWS_LINK
        elif url != "":
            link = url
        with requests.get(link,stream=True) as r:
            print("DOWNLOADING driver....")
            with open(cls.driver_name,"wb") as f:
                for chunk in r.iter_content():
                    f.write(chunk)
        with ZipFile(cls.driver_name,"r") as zipf :
            print("UNZIPPING driver....")
            zipf.extractall(cls.driver_Path)
            os.chmod(os.path.join(cls.driver_Path,cls.driver_name.strip(".zip")),stat.S_IREAD|stat.S_IEXEC|stat.S_IWRITE)
            if cls.checkFordrivers():
                print("Finished")
            else :
                print("Failed")
####


class WhatsappB:
    def __init__(self,vcffile:str,text:str,image:str,document:str):
        self.vcffile = vcffile
        self.text = text
        self.image = image
        self.document = document
        driverP = os.path.join(Config.driver_Path,Config.driver_name.strip(".zip"))
        try:
            self.driver = webdriver.Chrome(driverP)
            self.driver.get(WHATSAPP_WEB_APP)
        except Exception as e:
            raise Exception("Cannot load chrome Driver",type(e).__name__,e)


    def ExtractContacts(self) -> List[Any]:
        pvcf = parse.ParseVcf(self.vcffile)
        pvcf.Parse()
        contacts = pvcf.GetContacts()
        return contacts
    

    def _sendTextmsg(self):
        msgF = self.driver.find_element_by_xpath("//*[@id='main']/footer/div[1]/div[2]/div/div[2]")
        msgF.send_keys(self.text)
        msgF.send_keys(ENTER)


    def _sendImage(self):
        try :
            #click on share icon to share an image or document
            icon = self.driver.find_element_by_css_selector("span[data-icon='clip']").click()
            time.sleep(2)
            putPath = self.driver.find_element_by_css_selector("input[type='file']").send_keys(self.image)
            time.sleep(2)
            clickBtn = self.driver.find_element_by_css_selector("span[data-icon='send']").click()
            time.sleep(2)
        except Exception as e:
            print("Failed To Locate and Element",e)
            self.driver.quit()


    #this function is for sending text msgs only
    def MapNums(self,contact:str) -> str :
        self.failed = []
        try: 
            contactSearch = self.driver.find_element_by_class_name("_3FRCZ")
            contactSearch.send_keys(contact)
            contactSearch.send_keys(ENTER)
            selectedCnt = self.driver.find_element_by_xpath("//span[@title='" + contact  + "']").click()
            if self.text is not None :
                self._sendTextmsg()
            return contact
        except Exception as e:
            self.failed.append(contact)
            pass


    def image_sender(self, contacts:list):
        for contact in contacts :
            contactSearch = self.driver.find_element_by_class_name("_3FRCZ")
            contactSearch.send_keys(contact)
            contactSearch.send_keys(ENTER)
            selectedCnt = self.driver.find_element_by_xpath("//span[@title='" + contact  + "']").click()
            self._sendImage()
            time.sleep(3)
            print("sent to ",contact)
        self.driver.quit()


    def run(self) :
        start = input("Scan the QR Code then Enter y if you're done: ")
        rightAnsw = "y"
        if start == rightAnsw.upper() or start ==  rightAnsw:
            contacts = self.ExtractContacts()
            if self.text != None :
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.map(self.MapNums,contacts)
                    for cSent in future:
                        if cSent != None:
                            print(f"sent to {cSent}")
                print(f"Failed {len(self.failed)} times ==> {(',').join(self.failed)}")
                self.driver.close()
            elif self.image != None:
                self.image_sender(contacts)
        else:
            self.driver.quit()



def FlagHandler(argc:list) -> Tuple[Tuple[str],bool,str]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vcffile",type=str, help="Put the vcf file that contains contact you want ot ")
    parser.add_argument("--image",type=str,help="Put the image path if you need to send image to your contacts")
    parser.add_argument("--document",type=str,help="Document length")
    parser.add_argument("--text",type=str,help="text message to send")
    parser.add_argument("--url",type=str,help="url of the driver where to download it e.g `https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip`")
    parser.add_argument("--config",help="use this flag to configure the application",action="store_true")
    args = parser.parse_args() 
    if len(argc) >= 2 and not args.config :
        return (args.vcffile, args.image, args.document,args.text),False,""
    elif len(argc) >= 2 and args.config :
        return (args.vcffile, args.image, args.document,args.text),args.config,args.url
    else:
        parser.print_help()
        sys.exit(1)
        

if __name__ == "__main__":
    (vcffile, image , document, text),config, url = FlagHandler(sys.argv)
    if not config and url == "":
        WhatsappB(vcffile,text,image,document).run()
    elif config :
        if not Config.checkFordrivers():
            Config.getDriver(url)
        else :
            print("Seems like there is a driver on `browserdriver` directory")
