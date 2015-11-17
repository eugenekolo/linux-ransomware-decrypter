# Bitdefender's Linux Ransomware (Linux.Encoder.1) Decrypter

More Info: http://labs.bitdefender.com/2015/11/linux-ransomware-debut-fails-on-predictable-encryption-key/

## How to
Steps:
1. Hopefully you have NOT deleted any encrypted files
2. Run sort_files.sh / > sorted.list to obtain a list of the encrypted files sorted by encryption time
	* Note: run sort_files.sh /path/to/vm/partition if the data was on a vm
3. Most importantly, obtain the first file in that list, be it X.encrypted (head -1 sorted.list)
4. Find the seed using ./decrypter.py -f /path/to/X.encrypted
5. If you have the seed you can safely decrypt the files. Run ./decrypter.py -s <seed> -l <sorted.list> -e <error.list>
6. Check decryption was correct and clean the ".encrypted" files on your own.
	* Note: Unfortunately, the ransomware does not preserve ownership (user/group), some things might get broken because of this.
7. If you have files still encrypted they will appear in the file you provided as <error.list>. You will need to redo steps 3) -> 6) using the <error.list> until no more files.

## Example
     ```
     bash decrypter/sort_files.sh  > sorted_list
     head -1 sorted_list
     python decrypter/decrypter.py -f ./d/home/user/.bash_logout.encrypted
     $> [*] Seed: 1447255617
     python decrypter/decrypter.py -s 1447255617 -l sorted_list -e error_list
     ```
     
.........
[FAILED] ./d/usr/share/doc/mlocate/README.encrypted
[OK] ./d/usr/share/doc/mlocate/TODO.Debian.encrypted
[OK] ./d/usr/share/doc/readline-common/changelog.Debian.gz.encrypted
[FAILED] ./d/usr/share/doc/readline-common/copyright.encrypted
[FAILED] ./d/usr/share/doc/readline-common/inputrc.arrows.encrypted
[OK] ./d/usr/share/java/libintl.jar.encrypted
[*] recovered 7572 files
[*] failed to recover (probably bad seed) 9424 files
[*] 36 corrupted (probably truncated) files

6) => 3) (because 9424 files still encrypted)

3)
# head -1 error_list 
1447255625.0000000000 ./d/home/README_FOR_DECRYPT.txt.encrypted

4)
# python decrypter/decrypter.py -f ./d/home/README_FOR_DECRYPT.txt.encrypted
[*] Seed: 1447255625

5)
# python decrypter/decrypter.py -s 1447255625 -l error_list -e error_list2

........
[FAILED] ./d/usr/share/doc/mlocate/changelog.gz.encrypted
[OK] ./d/usr/share/doc/mlocate/NEWS.gz.encrypted
[FAILED] ./d/usr/share/doc/mlocate/README.encrypted
[FAILED] ./d/usr/share/doc/readline-common/copyright.encrypted
[OK] ./d/usr/share/doc/readline-common/inputrc.arrows.encrypted
[*] recovered 5000 files
[*] failed to recover (probably bad seed) 4424 files
[*] 0 corrupted (probably truncated) files






6) => 3) (because 4424 files still encrypted)

3)
# head -1 error_list2
1447255634.0000000000 ./d/root/test/size_10028.encrypted

4)
# python decrypter/decrypter.py -f ./d/root/test/size_10028.encrypted
[*] Seed: 1447255634

5)
# python decrypter/decrypter.py -s 1447255634 -l error_list2 -e error_list3

..........
[OK] ./d/usr/share/doc/libsqlite3-0/changelog.html.gz.encrypted
[OK] ./d/usr/share/doc/linux-image-2.6.32-5-amd64/changelog.Debian.gz.encrypted
[OK] ./d/usr/share/doc/locales-all/copyright.encrypted
[OK] ./d/usr/share/doc/lsb-base/copyright.encrypted
[OK] ./d/usr/share/doc/mlocate/AUTHORS.encrypted
[OK] ./d/usr/share/doc/mlocate/changelog.gz.encrypted
[OK] ./d/usr/share/doc/mlocate/README.encrypted
[OK] ./d/usr/share/doc/readline-common/copyright.encrypted
[*] recovered 4424 files
[*] failed to recover (probably bad seed) 0 files
[*] 0 corrupted (probably truncated) files


DONE!
