#!/usr/bin/env python

import uuid
import storage as StorageOperations

if __name__ == "__main__":

    filename = "testfile.txt"
    fileCont = "TestString..."
    storage.upload_file(fileCont, filename, 'kribesContainer')

    fileExist = storage.file_exists(filename, 'kribesContainer')

    print(fileExist)
