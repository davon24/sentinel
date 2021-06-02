
# macosx ps defunct process

#command: 
ps -A -ostat,ppid,pid,command | grep -e '^[Zz]'
output: 
Z      1  952 (prl_disp_service)
Z      952  1166 (prl_vm_app)



