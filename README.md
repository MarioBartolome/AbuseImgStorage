# AbuseImgStorage

<p align="center">
  <img src="https://user-images.githubusercontent.com/23175380/41865407-3f1cf97c-78ad-11e8-852f-fca05b59bbea.jpg">
</p>


### To fragment a file into "images" ;)

`user@computer ~/AbuseImgStorage/FileComposer> python3 Fragmentor.py chunk PATH_TO_FILE`

It will create 2-5MB chunks, that will display a small image (to avoid overloading too much). Also, and this is 
**important**, it will generate a ``.db`` file. **KEEP IT**. This file is needed to reconstruct the original from the 
chunks.


- Maybe you want a different max or min size for the chunks. 
    - You can alter the min size limit with the modifier `-m` or `-min-size` followed by the size in MB.
    
    `user@computer ~/AbuseImgStorage/FileComposer> python3 Fragmentor.py chunk PATH_TO_FILE -m SIZE_IN_MB`
    - You can alter the max size limit with the modifier `-M` or `-max-size` followed by the size in MB.
    
    `user@computer ~/AbuseImgStorage/FileComposer> python3 Fragmentor.py chunk PATH_TO_FILE -M SIZE_IN_MB`


### To reconstruct the original file from the pieces: 

Make sure **the `.db` file is in the same folder as the pieces**. 
Also, on this very first version, the names of the pieces should be the same as the ones created during the 
fragmentation process. 

`user@computer ~/AbuseImgStorage/FileComposer> python3 Fragmentor.py reconstruct PATH_TO_DB`

It will recreate the original file the chunks were made from.


### To check the integrity of the reconstructed files: 

If you have both files, the original and the reconstructed one, and want to check if they're really
the same, you can do it: 

`user@computer ~/AbuseImgStorage/FileComposer> python3 Fragmentor.py check PATH_TO_ORIGINAL PATH_TO_RECONSTRUCTED`


Use it at your own discretion.


**Need help?** ask for it: `user@computer ~/AbuseImgStorage/FileComposer> python3 Fragmentor.py {chunk, reconstruct, check} --help`

