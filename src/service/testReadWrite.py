#!/usr/bin/env python

import uuid
import StorageOperations

if __name__ == "__main__":

    filename = "testjosef.txt"
    fileCont = "testFile.txt"
    StorageOperations.upload_file(fileCont, filename, 'kribesContainer')

    fileExist = StorageOperations.file_exists(filename, 'kribesContainer')

    print(fileExist)
    fileExist2 = StorageOperations.file_exists("testfolder/acado_manual.pdf",'kribesContainer')
    print(fileExist2)
    
    StorageOperations.download_file(filename, 'kribesContainer')
