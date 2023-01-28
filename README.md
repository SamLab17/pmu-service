# PMU Service (Proof of concept)

## Web interface (submit executable to run on server)

```
python3 src/api.py
```

(May complain about some missing dependencies like `flask`, you'll need to `pip install` them).

## Command-line interface (what runs the VM on the server)

```
python3 src/runner.py <executable>
```

Example:

```
~# cat script.sh 
#!/bin/bash

echo "Hello from inside the VM!"

~# python3 src/runner.py script.sh
Copying script.sh to the guest virtual disk
Running script.sh in VM...

Linux debian 5.15.89 #2 SMP Sat Jan 21 14:49:20 CST 2023 x86_64


The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.


Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Fri Jan 27 04:02:32 UTC 2023 on ttyS0
root@debian:~# /root/script.sh

Hello from inside the VM!
```

Also tested with executables that call `get_perf_open` and hardware counters are available inside the VM.

