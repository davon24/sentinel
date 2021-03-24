
sentinel update-config watch-ssh-linux-log '{"logfile":"/var/log/secure","thresh":"60","attempts":"3","clear":"600","ssh_port":"22"}'

---

https://code.google.com/archive/p/sshwatch/

  """
   Intrusion Prevention System (IPS) for ssh (default port 22),
   this IPS responds to the suspicious activity by setting the firewall
   to block network traffic from the suspected malicious source.
   Suspicious activity is determined via auth or security logs.
     
   This IPS is linux only, using iptables, and thus must be run as root.

   thresh   = ( number of seconds between consecutive attempts )

   attempts = ( number of consecutive attempts ) 
    
   clear    = ( number of seconds elapsed to clear active source blocks ) 
    
   This IPS has been tested on:
   debian linux - /var/log/auth.log
   redhat linux - /var/log/secure 

   Best practice for running this program:
   ./sshwatch.py /var/log/auth.log >>/root/sshwatch.log 2>&1 &

   Program Overview:
   Continuously tail (subprocess tail -F) the system security logs,
   watching for a match on "sshd", "Failed password", "Invalid user".
   With a match, add the source ip to a list.  After number of
   sequentially matched failed attempts, in consecutive order,
   from the same source ip, under the thresh hold time,
   puts the source ip in iptables block.
   The "clear" value will remove the iptables block at selected
   interval. 

   "I basically got sick of seeing all these ssh dictionary attacks
   in my security logs." Enjoy! and Happy IPS'ing, 
   Updated Sun Jul 31 07:41:19 PDT 2011 v1.7 krink@csun.edu
   """



