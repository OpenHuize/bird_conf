# bird/peers 目录配置说明
## Peers 目录 及 Session protocol 命名规则：
``` U/D/P/G/R ``` 为Session类型

```

U = Upstream
D = Downstream
P = Peering
G = GRC (Global route collector)，例如 RIS/BGP.TOOLS SESSION
R = IX Route Server

```
> 例如 ``` D_AS138211 / U_AS58453 / P_AS13335 ```


## ebgp_export 参数解释：
``` ebgp_export(ASN , "session type", prepend_number, allow_downstream) ```
``` ASN ``` : 对端的 ASN，纯数字，如 ``` 200105  ```
``` session type ``` : 会话的类型，可选参数：``` upstream ``` / ``` ixrs ``` / ``` peer ``` / ``` downstream ``` / ``` grc ```
``` perpend number ``` : Prepend的次数，可选范围：``` 1~8 ```
``` allow_downstream ``` : 是否发送从 downstream 收到的 prefix，如果 upstream 不允许带下游填写 ``` false ``` ， 默认为 ``` true ```
> 填写例子： ``` where ebgp_import(4134 , "upstream", 0, true); ```


## 完整的使用例子：

```
# cat /etc/bird/peers/D_AS00000.conf
# ipv4 session
protocol bgp D_AS00000_v4 from tpl_bgp_v4 {
    neighbor 91.192.81.1 as 00000;
    ipv4 {
        #table bgp_v4_own; # 路由放到一个“仅限本网”的路由表。 与 allow_downstream 配合使用，当上游不允许带下游时，取消注释此行。
         export filter {
            if ebgp_export(00000 , "downstream", 0, true) then accept;
            reject;
        };
        import where ebgp_import(00000 , "downstream", 0, true);
        import limit off;
    };
}

# ipv6 session
protocol bgp D_AS00000_v6 from tpl_bgp {
    neighbor fe80::cafe as 00000;
    ipv6 {
        #table bgp_v6_own; # 路由放到一个“仅限本网”的路由表。 与 allow_downstream 配合使用，当上游不允许带下游时，取消注释此行。
         export filter {
            if ebgp_export(00000 , "downstream", 0, true) then accept;
            reject;
        };
        import where ebgp_import(00000 , "downstream", 0, true);
        import limit off;
    };
}

```

## ibgp_import 参数解释(v1.3+):
``` ibgp_import(int bgp_med_ping; int extra_bgp_med; int prepend_num) ```

bgp_med_ping: 两个iBGP节点之间的隧道的延迟

extra_bgp_med: 额外增加bgp_med，如打算给特定节点降低优先级

新的bgp_med  = 原bgp_med + bgp_med_ping + extra_bgp_med，bgp_med越低优先级越高。应此，bgp_med可以实现选定到指定路由的最小延迟路径。

prepend_num: ibgp导入时prepend本地asn的次数，如本机不支持非对称路由可能会造成问题。

## ibgp_export 参数解释(v1.3+):
``` ibgp_export(int prepend_num) ```

prepend_num：导出时prepend次数

## Huicast和Huize节点的互联
由于路由表的识别是通过bgp community来实现的，不同ASN会造成bgp community不统一。因此，AS61302和AS60539节点直接的iBGP需要进行转义。

路由表务必需要选定table bgp_v4/bgp_v6，将路由导入到主表可能会导致服务器失联。

```
#AS60539节点这边的配置

protocol bgp I_HUICAST_SIN3 from tpl_bgp {
    neighbor 2a13:aac7:13:2::2 as 61302;
    allow bgp_local_pref on;
    ipv4 {
        table bgp_v4;
        import limit off;
        export limit off;
        import filter{
        #bgp community escape
        if (61302, 2, 100) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 100)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,100));
        }
        if (61302, 2, 10) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 10)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,10));
        }
        if (61302, 2, 1) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 1)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,1));
        }

        ibgp_import(46, 0, 0);
        accept;
        }; 

       export filter {
        ibgp_export(0);
        accept;
       };
       
    };

    ipv6 {
        table bgp_v6;
        import limit off;
        export limit off;
        import filter{
        
        #bgp community escape
        if (61302, 2, 100) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 100)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,100));
        }
        if (61302, 2, 10) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 10)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,10));
        }
        if (61302, 2, 1) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 1)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,1));
        }

        ibgp_import(46, 0, 0);
        accept;
       }; 

       export filter {
        ibgp_export(0);
        accept;
       };
    };
} 
 
#AS61302节点这边的配置

protocol bgp I_HUICAST_TPE2 from tpl_bgp {
    neighbor 2a13:aac7:13:2::1 as 60539;
    allow bgp_local_pref on;
    ipv4 {
        table bgp_v4;
        import limit off;
        export limit off;
        import filter{
        
        #bgp community escape
        if (60539, 2, 100) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 100)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,100));
        }
        if (60539, 2, 10) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 10)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,10));
        }
        if (60539, 2, 1) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 1)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,1));
        }

        ibgp_import(46, 0, 0);
        accept;
       };

       export filter {
        ibgp_export(0);
        accept;
       };
    
    };

    ipv6 {
        table bgp_v6;
        import limit off;
        export limit off;
        import filter{
        
        #bgp community escape
        if (60539, 2, 100) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 100)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,100));
        }
        if (60539, 2, 10) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 10)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,10));
        }
        if (60539, 2, 1) ~ bgp_large_community then {
            # bgp_large_community.delete([(60539, 2, 1)]);
            bgp_large_community.add((LOCAL_ASN, 2 ,1));
        }

        ibgp_import(46, 0, 0);
        accept;
       };

       export filter {
        ibgp_export(0);
        accept;
       };
    };
} 

```
