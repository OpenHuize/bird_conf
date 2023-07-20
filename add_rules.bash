#!/bin/bash
ip -4 rule add from all iif eth1 table 147
ip -6 rule add from all iif eth1 table 147
ip -4 rule add from all fwmark 212271 lookup 147
ip -6 rule add from all fwmark 212271 lookup 147
