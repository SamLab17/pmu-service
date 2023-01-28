#!/usr/bin/expect

set disk [lindex $argv 0];
set program [lindex $argv 1];

spawn qemu-system-x86_64 \
	--enable-kvm \
	--smp 4 \
	-m 4G \
	-nographic \
	-nic none \
	-drive "file=$disk,format=qcow2" \
	-snapshot \
	-kernel "images/kernel.img" \
	-append "root=/dev/sda1 console=ttyS0,115200n8"

expect "debian login:"
send "root\r"

expect "~#"
send "$program\r"

set timeout [lindex $argv 2]
expect {
	"~#" { send "shutdown -h now" }
	timeout { puts "\n --- \n TIMEOUT \n --- \n"; exit 1 }
}

