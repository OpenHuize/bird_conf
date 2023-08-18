#!/bin/bash
as_set=("AS-HUIZE" "AS61302")
prefix=$(bgpq4 -b -A -6 ${as_set[*]} -R 48 -l allowed_prefix)
if [[ "$prefix" =~ ^ERROR.* ]]; then
    exit
else
echo "$prefix" > /etc/bird/filters/allowed_prefix.conf
fi

prefix=$(bgpq4 -b -A -6 AS-POEMA -R 48 -l AS_POEMA)
if [[ "$prefix" =~ ^ERROR.* ]]; then
    exit
else
echo "$prefix" > /etc/bird/filters/AS-POEMA.conf
fi

prefix=$(bgpq4 -b -A -6 AS-5V -R 48 -l AS_5V)
if [[ "$prefix" =~ ^ERROR.* ]]; then
    exit
else
echo "$prefix" > /etc/bird/filters/AS-5V.conf
fi

prefix=$(bgpq4 -b -A -6 AS-JSMSR -R 48 -l AS_JSMSR)
if [[ "$prefix" =~ ^ERROR.* ]]; then
    exit
else
echo "$prefix" > /etc/bird/filters/AS-JSMSR.conf
fi

prefix=$(bgpq4 -b -A -6 AS-K2HOST -R 48 -l AS_K2HOST)
if [[ "$prefix" =~ ^ERROR.* ]]; then
    exit
else
echo "$prefix" > /etc/bird/filters/AS-K2HOST.conf
fi

prefix=$(bgpq4 -b -A -6 AS-86 -R 48 -l AS_86)
if [[ "$prefix" =~ ^ERROR.* ]]; then
    exit
else
echo "$prefix" > /etc/bird/filters/AS-86.conf
fi

prefix=$(bgpq4 -b -A -6 AS-ShizukuGlobal-Europe -R 48 -l AS_ShizukuGlobal_Europe)
if [[ "$prefix" =~ ^ERROR.* ]]; then
    exit
else
echo "$prefix" > /etc/bird/filters/AS-ShizukuGlobal-Europe.conf
fi

prefix=$(bgpq4 -b -A -6  AS-HURRICANE -R 48 -l AS_HURRICANE)
if [[ "$prefix" =~ ^ERROR.* ]]; then
    exit
else
echo "$prefix" > /etc/bird/filters/AS-HURRICANE.conf
fi

prefix=$(bgpq4 -b -A -6  AS-DANGELO -R 48 -l AS_DANGELO)
if [[ "$prefix" =~ ^ERROR.* ]]; then
    exit
else
echo "$prefix" > /etc/bird/filters/AS-DANGELO.conf
fi

prefix=$(bgpq4 -b -A -6 AS-WOLFNET -R 48 -l AS_WOLFNET)
if [[ "$prefix" =~ ^ERROR.* ]]; then
    exit
else
echo "$prefix" > /etc/bird/filters/AS-WOLFNET.conf
fi


prefix=$(bgpq4 -b -A -4 AS-WOLFNET -R 24 -l AS_WOLFNET_V4)
if [[ "$prefix" =~ ^ERROR.* ]]; then
    exit
else
echo "$prefix" > /etc/bird/filters/AS-WOLFNET.ipv4.conf
fi

/usr/sbin/birdc 'c'
