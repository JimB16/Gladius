# Gladius
tools/ has python scripts for extracting and modifying data for the game Gladius by LucasArts. All tools were upgraded from their original version using python2 to python3.

## bec-tool.py
This tool unpacks the content from a bec-archive which is used by Gladius to store game and audio data. While unpacking a filelist is created that is necessary to repack the content into a new bec-archive.
The tool can also create a bec-archive from a previously unpacked archive. It is possible to repack with changed files, it is not possible to add files since this requires additional information about all files in the archive.
PS2 and GameCube version use slightly different variants of this archive which I couldn't get reproduce without an additional option "--gc" that will produce bec-archives which are compatible with the GameCube version.

To unpack call the tool with the "-unpack" option:
python3 tools/bec-tool.py -unpack gladius.bec gladius_bec/ gladius_bec_FileList.txt

To pack files into an archive call the tool with the "-pack" option:
python3 tools/bec-tool.py -pack gladius_bec/ gladius.bec gladius_bec_FileList.txt

## tok-tool.py
The tok-tool is to compress the file "skills.tok" with the dictionary compression that is used by the game. As far as I know this compression is also used for the effect-files (i.e. particle effect settings).
Input is a single text file that will be compressed, output are 3 files with the data for the strings, lines and overall file data.

To compress a file call the tool with the "-c" option:
python3 tools/tok-tool.py -c skills.tok skills_strings.bin skills_lines.bin skills.tok.brf

