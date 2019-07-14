#!/usr/local/bin/python3.7


import sys
import gzip
import subprocess


gzip_file_name=''

def lambda_handler():
  try:
    print ('in lambda handler')
    print (gzip_file_name)
    subprocess.call(["/bin/cp", "./"+gzip_file_name,"/tmp"])
    unzipped_file=gzip.open('/tmp/'+gzip_file_name,'rb')
    lines=unzipped_file.read().decode('UTF-8')
    print (lines)

  except Exception as e:
    print(e)
  



if __name__ == "__main__":
  print (sys.argv)
  gzip_file_name=sys.argv[1]
  lambda_handler()


