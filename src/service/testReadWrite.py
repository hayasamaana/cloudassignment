#!/usr/bin/env python

import uuid
import StorageOperations

if __name__ == "__main__":

    filename = "testfile.txt"
    fileCont = "testFile.txt"
    StorageOperations.upload_file(fileCont, filename, 'kribesContainer')

    fileExist = StorageOperations.file_exists(filename, 'kribesContainer')

    print(fileExist)
