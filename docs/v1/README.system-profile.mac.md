# system profile, mac  

generate a system profile  
```
sentinel gen-system-profile  
```

list system profiles  
```
sentinel list-system-profile
1 930ce78766d465721b760149c19eefb49aac0c38 2021-02-08 17:09:42
2 7e626b4731507c45e582a840b2920793cff092d5 2021-02-08 17:50:15
3 07b07b899341e7a5231dbaeb4a37c1fa47003920 2021-02-09 17:04:34
```

rowid '2' is after mac os upgrade and reboot.  
View full details of rowid 2
```
sentinel get-system-profile-rowid 2
```

See what has changed between rowid 1 and 2
```
sentinel diff-system-profile-rowid 1 2
```

---

Data structures are python dictionary paths prefixed with indicators '<' '=' '>' 'x'    
```
< ['SPExtensionsDataType'][723]['_name']
= ['SPUSBDataType'][0]['_name']
x ['SPSoftwareDataType'][0]['os_version']
> ['SPNetworkDataType'][5]['IPv6']['Addresses'][2]
```


python dictionary path "['SPExtensionsDataType'][723]['_name']" exists only in 1, '<'
```
sentinel get-system-profile-data 1 "['SPExtensionsDataType'][723]['_name']"
webdav_fs
```


python dictionary path "['SPUSBDataType'][0]['_name']" are equal in 1 and 2, '='
```
sentinel get-system-profile-data 1 "['SPUSBDataType'][0]['_name']"
USB31Bus
sentinel get-system-profile-data 2 "['SPUSBDataType'][0]['_name']"
USB31Bus
```


python dictionary path "['SPSoftwareDataType'][0]['os_version']" are not equal, 'x'
```
sentinel get-system-profile-data 1 "['SPSoftwareDataType'][0]['os_version']"
macOS 11.1 (20C69)
sentinel get-system-profile-data 2 "['SPSoftwareDataType'][0]['os_version']"
macOS 11.2 (20D64)
```


python dictionary path "['SPNetworkDataType'][5]['IPv6']['Addresses'][2]" exists only in 2, '>'    
remember that python indexes start at zero, and [2] is a python list of three items     
```
sentinel get-system-profile-data 2 "['SPNetworkDataType'][5]['IPv6']['Addresses']"
['2600:380:b410:86d6:1870:e9df:13a2:6a0a', '2600:380:b410:86d6:30fc:eb8b:2d44:743d', '2603:8000:2602:2500:a5:d240:2b34:1624']
```



