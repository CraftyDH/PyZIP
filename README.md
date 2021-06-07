# PyZIP
A Python command line implementation of ZIP using only std.

## Supports
Currently PyZIP supports compression and uncompression using DEFLATE and BZip2.

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