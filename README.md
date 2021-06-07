# PyZIP
A Python command line implementation of ZIP using only std libraries. 

## Supports
Currently PyZIP supports compression and uncompression using DEFLATE and BZip2. 

PyZip currently is verified to run on windows with python 3.9. As this project uses os abtractions it should work on any os.
The zip output has been tested with windows explorer and 7zip as such it should would with any zip compatible program.

## Usage
### To add a file to an archive
```sh
pyzip file.zip add file1 file2 file3... 
```
To use deflate compression pass --deflate

To use bzip2 compression pass --bzip2

To not use any compression pass --store

### To remove a file from an archive
```sh
pyzip file.zip remove file1 file2 file3... 
```

### To extract an archive
```sh
pyzip file.zip extract --output=output/
```

### To extract a file from an archive
```sh
pyzip file.zip extract file1 -output=output/
```

### To get info on the archive
```sh
pyzip file.zip info
```