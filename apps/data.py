from threading import Thread
from time import sleep

import requests

get_headers = {"Accept": "application/json"}
post_headers = {"Accept": "application/json", "Content-type": "application/json"}
nfvcl_base_url = "http://192.168.102.224:5003"

topology_data_raw = {'vims': [], 'networks': [], 'routers': []}
pdu_data_raw = []
blue_data_generic = []
blue_detailed = []
nsi_data = []
vnf_data = []


def get_dynamic_data():
    return {
        'topology_data_raw': topology_data_raw,
        'pdu_data_raw': pdu_data_raw,
        'blue_data_generic': blue_data_generic,
        'blue_detailed': blue_detailed,
        'nsi_data': nsi_data,
        'vnf_data': blue_vnfs
    }


nsi_keys = ['_id', 'name', 'nsState', 'currentOperation', 'errorDetail', 'deploymentStatus', 'constituent-vnfr-ref',
            'operational-status', 'config-status', 'detailed-status', 'orchestration-progress', 'create-time',
            'nsd-name-ref', 'instantiate_params', 'flavor', 'image', 'vld']


def delete_blue(blue_id):
    res = requests.delete(
        "{}/nfvcl/api/blue?id={}".format(nfvcl_base_url, blue_id),
        params=None, verify=False, stream=True, headers=get_headers
    )
    print("delete_blue", res.status_code, res.json())
    return res.status_code, res.json()


def add_blue(body):
    res = requests.post(
        "{}/nfvcl/api/blue".format(nfvcl_base_url),
        json=body, params=None, verify=False, stream=True, headers=post_headers
    )
    return res.status_code, res.json()


def poll():
    global topology_data_raw, blue_data_generic, blue_detailed, nsi_data, vnf_data, pdu_data_raw, vnf_data_raw, \
        blue_vnfs
    while True:
        # print('@@@ resting')
        topology_data_raw = requests.get(
            "{}/nfvcl/api/topology".format(nfvcl_base_url), params=None, verify=False, stream=True,
            headers=get_headers).json()
        blue_data_generic = requests.get(
            "{}/nfvcl/api/blue".format(nfvcl_base_url), params=None, verify=False, stream=True,
            headers=get_headers).json()
        # labels = [b['id'] for b in blue_data_generic]
        # print('---------- poll {}'.format(labels))
        blue_detailed = requests.get(
            "{}/nfvcl/api/blue?detailed=True".format(nfvcl_base_url), params=None, verify=False, stream=True,
            headers=get_headers).json()
        nsi_ = requests.get(
            "{}/nfvcl/api/nsi".format(nfvcl_base_url), params=None, verify=False, stream=True,
            headers=get_headers).json()
        pdu_data_raw = requests.get(
            "{}/nfvcl/api/pdu".format(nfvcl_base_url), params=None, verify=False, stream=True,
            headers=get_headers).json()
        vnf_data_raw = requests.get(
            "{}/nfvcl/api/vnfi".format(nfvcl_base_url), params=None, verify=False, stream=True,
            headers=get_headers).json()
        osm_vim_raw = requests.get(
            "{}/nfvcl/api/vim".format(nfvcl_base_url), params=None, verify=False, stream=True,
            headers=get_headers).json()

        vim_id_to_name = {item['_id']: "{}@{}".format(item['vim_tenant_name'], item['name']) for item in osm_vim_raw}

        # print(vnf_data_raw)
        nsi_data = [{k: v for (k, v) in element.items() if k in nsi_keys} for element in nsi_]
        # print(nsi_data)

        blue_vnfs = {}
        for b in blue_detailed:
            blue_vnfs[b['id']] = []
            for ns in b['ns']:
                nsi_id = ns['nsi_id']
                for v in vnf_data_raw:
                    if v['nsr-id-ref'] == ns['nsi_id']:
                        if len(v['vdur']) > 0:
                            type_ = 'VNF'
                        elif 'kdur' in v and len(v['kdur']) > 0:
                            type_ = 'KNF'
                        elif 'pdur' in v and len(v['pdur']) > 0:
                            type_ = 'PNF'
                        else:
                            type_ = '-'

                        blue_vnfs[b['id']].append(
                            {
                                'name': v['vnfd-ref'],
                                'type': type_,
                                'mgt_ip': v['ip-address'],
                                'vnf_id': v['vnfd-id'],
                                'nsd_id': nsi_id,
                                'vim': vim_id_to_name[v['vim-account-id']] if v['vim-account-id'] in vim_id_to_name else
                                v['vim-account-id']
                            }
                        )
        # print(blue_vnfs)

        sleep(5)


# thread = Thread(target=poll, args=(msg, blue_id, CandidateBlue, ))
# thread.daemon = True
thread = Thread(target=poll)
thread.start()
sleep(2)
print(topology_data_raw)

"""
blue_data_generic = [
    {
        "id": "YOQD8O",
        "type": "K8s",
        "created": "11/17/2021, 21:08:20",
        "modified": "11/17/2021, 21:18:32",
        "no_vims": 1,
        "no_nsd": 2,
        "no_primitives": 3
    },
    {
        "id": "ul9maTvFQA",
        "type": "VO",
        "created": "01/20/2022, 18:08:30",
        "modified": "01/20/2022, 18:09:21",
        "no_vims": 1,
        "no_nsd": 1,
        "no_primitives": 0
    }
]


topology_data_raw = {
    "vims": [
        {
            "schema_version": "1.0",
            "name": "os-3",
            "vim_type": "openstack",
            "vim_url": "http://192.168.100.4:5000/v3",
            "vim_tenant_name": "admin",
            "vim_user": "admin",
            "vim_password": "pap3rin0",
            "config": {
                "additionalProp1": {
                    "insecure": True,
                    "APIversion": "v3.3"
                },
                "use_floating_ip": False
            },
            "networks": [
                {
                    "name": "mngmnt-vnf"
                },
                {
                    "name": "mngn-vnf-os"
                },
                {
                    "name": "net1"
                },
                {
                    "name": "net2"
                }
            ],
            "routers": [
                {
                    "name": "mngn-vnf-os-router"
                },
                {
                    "name": "trex-router"
                }
            ]
        }
    ],
    "networks": [
        {
            "name": "mngmnt-vnf",
            "external": False,
            "type": "vlan",
            "vid": 1000,
            "dhcp": False,
            "cidr": "192.168.15.0/24",
            "allocation_pool": [
                {
                    "start": "192.168.15.1",
                    "end": "192.168.15.253"
                }
            ],
            "gateway": "192.168.15.254",
            "dns_nameservers": [
                "192.168.255.25"
            ],
            "ids": [
                {
                    "l2net_id": "8be65c70-af87-43a9-81a7-d17e42709fce",
                    "l3net_id": None,
                    "vim": "os-3"
                }
            ]
        },
        {
            "name": "mngn-vnf-os",
            "external": False,
            "type": "vxlan",
            "dhcp": True,
            "cidr": "192.168.13.0/24",
            "allocation_pool": [
                {
                    "start": "192.168.13.1",
                    "end": "192.168.13.199"
                }
            ],
            "gateway": "192.168.13.254",
            "dns_nameservers": [
                "192.168.255.25"
            ],
            "ids": [
                {
                    "l2net_id": "9dd6804f-c7e8-4fc9-8e86-8d37d1bb9313",
                    "l3net_id": "74cb7865-6331-4be6-a249-bf08ff7fbfb7",
                    "vim": "os-3"
                }
            ]
        },
        {
            "name": "os-intercon",
            "external": False,
            "type": "vlan",
            "vid": 990,
            "dhcp": False,
            "cidr": "172.16.0.0/24",
            "allocation_pool": [
                {
                    "start": "172.16.0.101",
                    "end": "172.16.0.151"
                }
            ],
            "gateway": "172.16.16.254",
            "dns_nameservers": []
        },
        {
            "name": "net1",
            "external": False,
            "type": "vxlan",
            "dhcp": True,
            "cidr": "10.0.10.0/24",
            "allocation_pool": [
                {
                    "start": "10.0.10.1",
                    "end": "10.0.10.253"
                }
            ],
            "gateway": "10.0.10.254",
            "ids": [
                {
                    "l2net_id": "899f75b3-79be-48a9-b730-7925a2d3069d",
                    "l3net_id": "3b4d4a17-783b-4bb7-a3a6-8bf54541b753",
                    "vim": "os-3"
                }
            ]
        },
        {
            "name": "net2",
            "external": False,
            "type": "vxlan",
            "dhcp": True,
            "cidr": "10.0.11.0/24",
            "allocation_pool": [
                {
                    "start": "10.0.11.1",
                    "end": "10.0.11.253"
                }
            ],
            "gateway": "10.0.11.254",
            "ids": [
                {
                    "l2net_id": "2b00444b-988c-44d0-8daa-de9089baad0e",
                    "l3net_id": "a807ddc6-2709-43b6-83d7-b388e9a51023",
                    "vim": "os-3"
                }
            ]
        }
    ],
    "routers": [
        {
            "name": "mngn-vnf-os-router",
            "ports": [
                {
                    "net": "mngn-vnf-os",
                    "ip_addr": "192.168.13.254 "
                },
                {
                    "net": "mngmnt-vnf",
                    "ip_addr": "192.168.15.213"
                }
            ]
        },
        {
            "name": "trex-router",
            "ports": [
                {
                    "net": "net1",
                    "ip_addr": "10.0.10.254"
                },
                {
                    "net": "net2",
                    "ip_addr": "10.0.11.254"
                }
            ]
        }
    ]
}
"""

blue_type = [{
    "_id": {
        "$oid": "61859af927a75729fc1e254b"
    },
    "category": "4G",
    "flavors": {
        "hard": [
            "monolithic"
        ],
        "soft": [
            "pnf"
        ]
    },
    "id": "OAI",
    "module": "blueprint_oai"
}, {
    "_id": {
        "$oid": "61859af927a75729fc1e254c"
    },
    "category": "4G",
    "flavors": {
        "hard": [
            "monolithic",
            "bypass"
        ],
        "soft": [
            "pnf"
        ]
    },
    "id": "AmariBypass",
    "module": "blueprint_amari"
}, {
    "_id": {
        "$oid": "61859af927a75729fc1e254d"
    },
    "category": "service",
    "flavors": {
        "hard": [
            "tunnel"
        ],
        "soft": []
    },
    "id": "VyOsMultipleTunnels",
    "module": "blueprint_multivyos"
}, {
    "_id": {
        "$oid": "61859af927a75729fc1e254e"
    },
    "category": "4G",
    "flavors": {
        "hard": [
            "monolithic",
            "1nic"
        ],
        "soft": [
            "pnf"
        ]
    },
    "id": "OAI_1nic",
    "module": "blueprint_oai_1nic"
}, {
    "_id": {
        "$oid": "61859af927a75729fc1e254f"
    },
    "category": "service",
    "flavors": {
        "hard": [
            "mcxptt"
        ],
        "soft": []
    },
    "id": "Mcxptt",
    "module": "blueprint_mcxptt"
}, {
    "_id": {
        "$oid": "61859af927a75729fc1e2550"
    },
    "category": "5G",
    "flavors": {
        "hard": [
            "monolithic"
        ],
        "soft": [
            "pnf"
        ]
    },
    "id": "Amari5G",
    "module": "blueprint_amari5G"
}, {
    "_id": {
        "$oid": "61859af927a75729fc1e2551"
    },
    "category": "5G",
    "flavors": {
        "hard": [
            "modular",
            "bypass"
        ],
        "soft": [
            "pnf"
        ]
    },
    "id": "Open5GS",
    "module": "blueprint_open5gs"
}, {
    "_id": {
        "$oid": "61859af927a75729fc1e2552"
    },
    "category": "service",
    "flavors": {
        "hard": [
            "k8s"
        ],
        "soft": []
    },
    "id": "K8s",
    "module": "blueprint_k8s"
}, {
    "_id": {
        "$oid": "61859af927a75729fc1e2553"
    },
    "category": "service",
    "flavors": {
        "hard": [
            "router"
        ],
        "soft": []
    },
    "id": "VyOSBlue",
    "module": "blueprint_vyos"
}, {
    "_id": {
        "$oid": "61859af927a75729fc1e2554"
    },
    "category": "service",
    "flavors": {
        "hard": [
            "VO"
        ],
        "soft": []
    },
    "id": "VO",
    "module": "blueprint_vo"
}, {
    "_id": {
        "$oid": "61859af927a75729fc1e2555"
    },
    "category": "5G",
    "flavors": {
        "hard": [
            "k8s"
        ],
        "soft": [
            "pnf"
        ]
    },
    "id": "Open5Gs_K8s",
    "module": "blueprint_Open5GS_K8s"
}, {
    "_id": {
        "$oid": "61859af927a75729fc1e2556"
    },
    "category": "5G",
    "flavors": {
        "hard": [
            "ueransim"
        ],
        "soft": []
    },
    "id": "UeRanSimBlue",
    "module": "blueprint_ueransim"
}]

"""
blue_detailed = [
    {
        "id": "YOQD8O",
        "type": "K8s",
        "created": "11/17/2021, 21:08:20",
        "modified": "11/17/2021, 21:18:32",
        "supported_ops": [
            "init",
            "add_worker",
            "del_worker",
            "nfvo_k8s_onboard",
            "monitor",
            "log"
        ],
        "config": {
            "cni": "flannel",
            "load_balancer": {
                "pools": [
                    {
                        "net_name": "mngmnt-vnf",
                        "cidr": "192.168.25.0/24",
                        "ip_start": "192.168.25.111",
                        "ip_end": "192.168.25.130",
                        "mode": "layer2"
                    }
                ],
                "mode": "layer2"
            },
            "controller_ip": "192.168.25.60",
            "pod_network_cidr": "10.254.0.0/16",
            "master_credentials": "apiVersion: v1\nclusters:\n- cluster:\n    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUMvakNDQWVhZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJeE1URXhOekl4TVRNMU1Wb1hEVE14TVRFeE5USXhNVE0xTVZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTFhFClBMamk2RHNsampWMEhhZ1BWenFFY1RoMXZmazRoSnE4bEZXdUxxS3RETUt3UU1CVmpBWlRPL09PRmk5akdHZ3cKbXQ2TWdubTdEUE02alZpNkRSa3d5VXlSaTdxSFlrTWdYUkswV1Y5bjk4SzNlNFB3QlNVeG5NOEZkb3U2bDdkcAoyTWZHS1A3TmFIdGVpaC9lT0NFTzRkM0kvUjJyRCt0cjl1OEpHdmFRbFVLM1k0c1hrQnhFRnQ4cFp2bnFQT0gzClBmUTlMMUZCWnNXckJFT0hjUXcrRnlEVEMrTm92VHd2RnBvK1VNYUprN2tLWDYwQTZQZ1RvdmZmTGxWUU1MZTIKL29WN1pGdlNsNzh0VHFQdmdUMXhya0JMaGpMV2JqRlRaS2dwbEd6cEdiSEd1VmFXeUYzWlVtM2ZML0NrUFQ2cgo3cnQ4UHhVbUhDYksyN1ZCR3ZVQ0F3RUFBYU5aTUZjd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZEVHZSTDhnVjNyMWdkYTM5ZnlmeWJhZUxPcjlNQlVHQTFVZEVRUU8KTUF5Q0NtdDFZbVZ5Ym1WMFpYTXdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBRFJJelRlUTVxc1o3cjdObjJuVgpNSGU0UWNlVmR6bkYwUVhFc3dYTjd1L0QyU3NEMDZhOXhKYlpmZDRJc0ZSWG5pVnZXM0lPQmFDa2NXOFJ0bFB4CjlUQ0RJV2l6cjFLOTh2bHVYdmJGeUxJb1NKczNQdVdrMGFPcE9Rd1dYZ3Z3Q3ZTdGVaL0lxOGFaRzVoUVZDTDcKbk5xVmt0RkJpT2paWHFIZHBJU3A0VzdsNTE5b2tRWUhSc0lONU5JRFQrWThoRkNtZnZkQWpYaEhVZnhYTklxawpnRlJZTVVjakIzRnE3SVB4M3VQay9oSk8valdyRHA3SW4zMDluM3FzMUQ5MWJRVjN0Vkg0K0FNQ1hqODVsMmdMClhJd01hL0xTSTJkSTI2L2FyQ0JXbUtiUk1LR3h3ZmljbEtUdmRRelczWjZSVFdXZy9ubmxoemFGVVRRa2R4RloKeWdnPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==\n    server: https://192.168.25.60:6443\n  name: kubernetes\ncontexts:\n- context:\n    cluster: kubernetes\n    user: kubernetes-admin\n  name: kubernetes-admin@kubernetes\ncurrent-context: kubernetes-admin@kubernetes\nkind: Config\npreferences: {}\nusers:\n- name: kubernetes-admin\n  user:\n    client-certificate-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lJUzl5OWlpNkdBNWd3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TVRFeE1UY3lNVEV6TlRGYUZ3MHlNakV4TVRjeU1URXpOVFZhTURReApGekFWQmdOVkJBb1REbk41YzNSbGJUcHRZWE4wWlhKek1Sa3dGd1lEVlFRREV4QnJkV0psY201bGRHVnpMV0ZrCmJXbHVNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQTV1VU1ib0hYTlQrTy9FWGgKUHFCOHB5ZnRCNHE0VUFlSWtqZ0ZSUmZtNWlnbE8va3QwbGtmS2dHaFh0V3BLdjRjV29LS29GSHRCYzZBTzVBMgpCQXpKRTF1TUpGc0VhZnpXMml3QlVHeU8yR1dnQmhOQnJtOWMzZU01aUw0djRTSG5VRjM2anhrTE1vbzdVcTNRCnpQaXU0TmxpZXc3RGFJRFZ1aE93WlZ4dnplMy82aEhvTUtvUXV3V1B5NllKS2d4bHhPb0xFWE9rYXl3ZG1ORUIKaFNIbW9ySVJ3emxXUnVRaGpyYmdIUzFzc2h6YnVWdkNrM0trZy84N0JZMW5qUzI1VVFjbitGVEtFV0RQY2t5NgpDM0tWNTB6OUxDd0d5ZXNGaFZnd0ZPbFd3WE5reHIvN3ZubXZ1dThwNUVaV3huZEdmTkIyc2VUcnBRUU92b3VPCm9WUFJ6UUlEQVFBQm8xWXdWREFPQmdOVkhROEJBZjhFQkFNQ0JhQXdFd1lEVlIwbEJBd3dDZ1lJS3dZQkJRVUgKQXdJd0RBWURWUjBUQVFIL0JBSXdBREFmQmdOVkhTTUVHREFXZ0JRMDcwUy9JRmQ2OVlIV3QvWDhuOG0ybml6cQovVEFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBYkRrZ0F2VGpVei90VEkxdG0vbmFzWEx4aW1yZDF6K0dMSzRQCkdBeDZsdWVZUjhEV0hsS2JGb2JRUUFkOTdNeU43MzRsZlIwMnBBL09EaU13K2t0OXVhaGFyZDRTajhqelY2R0MKeW01RTVBa3FVVzZoTmtvR1IxYllsVnU1enRETFVWWkRYcCtyTDV5a0Z1bjFCdUQ0a2twVzdwY3lNYXpOMEtycwpXWlZXaTZiMWxFUkxsZmJZSzZ6UlpONktFMmp4anFpblZOaHJ2YmwrU2VNN1M1enhkMlk4WW1NNll6THVHQ1BiCmNkN1Z0ZGYrZnhOLzJ0R3RpVkRrOFpPQzdrZDJ3YkJSNE1YNmFzakFuUTdKR2pwTWJQR2E2TDBadXhXcysrOE8KNk1SZnYrR1ZGbkxxZFRUYk9EK1hmUlVBeEdmbUZLU290cm1CQWpHWHlLOWV3Z2Z0MlE9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==\n    client-key-data: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFcEFJQkFBS0NBUUVBNXVVTWJvSFhOVCtPL0VYaFBxQjhweWZ0QjRxNFVBZUlramdGUlJmbTVpZ2xPL2t0CjBsa2ZLZ0doWHRXcEt2NGNXb0tLb0ZIdEJjNkFPNUEyQkF6SkUxdU1KRnNFYWZ6VzJpd0JVR3lPMkdXZ0JoTkIKcm05YzNlTTVpTDR2NFNIblVGMzZqeGtMTW9vN1VxM1F6UGl1NE5saWV3N0RhSURWdWhPd1pWeHZ6ZTMvNmhIbwpNS29RdXdXUHk2WUpLZ3hseE9vTEVYT2theXdkbU5FQmhTSG1vcklSd3psV1J1UWhqcmJnSFMxc3NoemJ1VnZDCmszS2tnLzg3QlkxbmpTMjVVUWNuK0ZUS0VXRFBja3k2QzNLVjUwejlMQ3dHeWVzRmhWZ3dGT2xXd1hOa3hyLzcKdm5tdnV1OHA1RVpXeG5kR2ZOQjJzZVRycFFRT3ZvdU9vVlBSelFJREFRQUJBb0lCQUV6cmw0V2xHZFh5YzZjVgpmS0dKZzUySVRvM0pwL2Q1V3dValJwWXJEVkExcFpuaVBHS3NNQmFsYm1ZU2xnWHRtL0tITkxtT01ZRlN0eU9nCnVtNEUrR1BMaHRlQnZ1bTBRcnR5RjRuOGNHWWxEUGVaS0xOOUJCb2puY0l4WWZBRmhITWdxOTFLUVpHM3ZXV2cKNUVPMHdVWEZCZXJyRXl4WVoxdFRQZHUydk1TRVdGSTY1WnEzYjB4L1ZwSEtSaENLVXVMbXBhZWcyVStnSVN0VQp2MVlNbXZPS0VxR0t5MTFZb20wd3hhRHU0V2tNUHVBdlE2dXk1dExWdWxKSDBwbGE1d3VYYjZGSkNHZFU1aWV4CjBnWnpoV2p1YWljZUVGMmd2ajlLZXJRMEY1YkhWbTQxM0cwaU82TDdraGpLVHdMd3dkOExhRkg2RVROdDJjMmEKN2lVVmdCMENnWUVBOEh6clBRSUJyWDgza3gxWWRzTXQwV2tNSkk4eVg3N1N0VTN2SFV2TXRWK3dBMVk0SmpUUwpNOWdoMXMyQWFkU3A3eHhkaStKb3FBL3lZc3o2RWNrWkdjZG9ZMm5ROTl2bWlYNnVLQ1IrWmtZUTNCVzdJWXZZCkI2eXE4ZG85NHZ6ZXpwS3BJT1NHYW4xK0d6TmFiZUV6M3hYUnFCL2dNRnpRS25WVWd1QlBCWXNDZ1lFQTljbTQKWkwyaTcyWkVOcEZJMlNlblJ4WUdOS3E1bXo5d1dEa3RsU21FRlFsK3ErenNabGgrSEFmTkxmZmJ5cGlIL3VOWAo5aGpRUkl0Q2k0TjJ1ZjRJZnBWZ0JkTElzeGpqTzZsWjZOR3plYkdWQks2OVFkUmhZNDFHS2xpL2FVWnprODRaClBVa3hYdWVCQThKQ012WTRqR1h2MFU5QzY3eTNrNTh3UllaVFlRY0NnWUVBbU84SDlmTXB0L2k0RWVGT21iQUQKbWpHUW5FdElRS1VzZ0VvQWJ3UCtPYldSVEgzdkZUVHdIREl0U3RuQytRcFp5d3FoM3N4cnU3endhcTVwdFJmSwowNThCSG45emVid3BQblVHTWRjTFh1VGQ0ZWdiNmZoeHVHZXhDajY4cm5ZYkJ3a3pid3lGQW9HdHlZUjkxSFNyCnRRbStHNG14MjIrYW5mV2hlZDFGdzRNQ2dZQnJxVytXMlNaYzNSdjJGdytrNTJTems2Y21QTDVPamF4RlNNNTUKcnhUSExrQ0pTSitJZVN6TVZIS0F0emhVZHhuakFXeVBSUEU5aFE2aUUvVFdwYnJNejl1ZTBXVE9acEZxbWRUagpVYS9mRjNWaDlyUzUrRENzcmI1VllFaC84YmRBd0I5NEkrNTNWc3JCZmI4SG1hak5mdjFjWHU2K1dnekRvaEEvCjlBWGowd0tCZ1FESnVRSFoxd0RLbmwzT3AyaWRtdzdlc0RuUDdPcVdRQnBJKy84SUJud3JyZlBSL0xOSzlNOFQKOHVtU25zOEhyZmlpbUdJVzl6U2xUek5hVXFRdndLMjk1aFA1QXhtcnQ1L0N5bEpZdzJxM2NzWkIwOWJGY0ExOAp1R1diNUM0T2hpVGYra0tpU3Qwdy8zQnFkN0tkekNGRUdhRnlac1F4QjlLZ01rZEx1VnFoVHc9PQotLS0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQo="
        },
        "vims": [
            {
                "name": "os-5",
                "tenant": "admin",
                "core": True,
                "mgt": "mngmnt-vnf",
                "tacs": [
                    {
                        "id": "1",
                        "worker_mgt_ip": "192.168.25.77",
                        "worker_data_ip": [
                            {
                                "net": "mgt",
                                "ip": "192.168.25.77"
                            }
                        ]
                    }
                ]
            }
        ],
        "ns": [
            {
                "status": "day2",
                "type": "master",
                "vim": "os-5",
                "nsi_id": "cb5832a7-3e34-4954-8e62-53d74a062b6d",
                "nsd_id": "cacc594a-3d42-4d13-9bb2-d2d054d52ac6"
            },
            {
                "status": "day2",
                "type": "worker",
                "vim": "os-5",
                "nsi_id": "e88d71b0-fff0-49bc-a45a-d8146bd20243",
                "nsd_id": "b385f255-69e0-42bb-b1cc-403935df6636"
            }
        ],
        "vnfd": {
            "core": [
                {
                    "id": "vnfd",
                    "name": "YOQD8O_k8s_master",
                    "vl": [
                        {
                            "vld": "mgt",
                            "name": "ens3",
                            "mgt": True,
                            "intf_type": "VIRTIO"
                        }
                    ]
                }
            ],
            "tac": [
                {
                    "tac": "1",
                    "vnfd": [
                        {
                            "id": "vnfd",
                            "name": "YOQD8O_k8s_worker_tac_1",
                            "vl": [
                                {
                                    "vld": "mgt",
                                    "name": "ens3",
                                    "mgt": True,
                                    "port-security-enabled": False,
                                    "intf_type": "VIRTIO"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "primitives": [
            {
                "result": {
                    "response": "{\n    \"id\": \"40d5d8b3-69a0-409b-87b0-c8abc747676d\"\n}\n",
                    "details": {
                        "_id": "40d5d8b3-69a0-409b-87b0-c8abc747676d",
                        "id": "40d5d8b3-69a0-409b-87b0-c8abc747676d",
                        "operationState": "COMPLETED",
                        "queuePosition": 0,
                        "stage": "",
                        "errorMessage": "",
                        "detailedStatus": None,
                        "statusEnteredTime": 1637183731.7485728,
                        "nsInstanceId": "cb5832a7-3e34-4954-8e62-53d74a062b6d",
                        "lcmOperationType": "action",
                        "startTime": 1637183469.6736858,
                        "isAutomaticInvocation": False,
                        "operationParams": {
                            "member_vnf_index": "1",
                            "primitive": "flexops",
                            "primitive_params": {
                                "config-content": {
                                    "conf_files": [
                                        {
                                            "src": "http://192.168.103.246:5003/nfvcl_day2/day2/flannel_config_YOQD8O.yaml",
                                            "name": "kube_cni.yaml"
                                        },
                                        {
                                            "src": "http://192.168.103.246:5003/nfvcl_day2/day2/metallb_manifest_YOQD8O.yaml",
                                            "name": "metallb_manifest.yaml"
                                        },
                                        {
                                            "src": "http://192.168.103.246:5003/nfvcl_day2/day2/metallb_config_YOQD8O.yaml",
                                            "name": "metallb_config.yaml"
                                        },
                                        {
                                            "src": "http://192.168.103.246:5003/nfvcl_day2/day2/openebs_operator_YOQD8O.yaml",
                                            "name": "openebs_operator.yaml"
                                        },
                                        {
                                            "src": "http://192.168.103.246:5003/nfvcl_day2/day2/default_storageclass_YOQD8O.yaml",
                                            "name": "default_storageclass.yaml"
                                        },
                                        {
                                            "src": "http://192.168.103.246:5003/nfvcl_day2/day2/regcred_YOQD8O.yaml",
                                            "name": "regcred.yaml"
                                        }
                                    ],
                                    "playbooks": [
                                        {
                                            "prio": 10,
                                            "src": "http://192.168.103.246:5003/nfvcl_day2/day2/ansible_k8s_k8s_controller_YOQD8O_1_step1.yaml",
                                            "name": "ansible_k8s_k8s_controller_YOQD8O_1_step1.yaml"
                                        }
                                    ],
                                    "action_id": "8c3c4990-3e64-4711-b5f2-e03f67834499",
                                    "post_url": "http://192.168.103.246:5003/nfvcl_day2/actions",
                                    "nsd_id": "k8s_controller_YOQD8O",
                                    "vnfd_id": 1,
                                    "blue_id": "YOQD8O"
                                }
                            },
                            "lcmOperationType": "action",
                            "nsInstanceId": "cb5832a7-3e34-4954-8e62-53d74a062b6d"
                        },
                        "isCancelPending": False,
                        "links": {
                            "self": "/osm/nslcm/v1/ns_lcm_op_occs/40d5d8b3-69a0-409b-87b0-c8abc747676d",
                            "nsInstance": "/osm/nslcm/v1/ns_instances/cb5832a7-3e34-4954-8e62-53d74a062b6d"
                        },
                        "_admin": {
                            "created": 1637183469.6737285,
                            "modified": 1637183731.7485762,
                            "projects_read": [
                                "d5bb416c-d75e-491b-b910-88b8f45d3153"
                            ],
                            "projects_write": [
                                "d5bb416c-d75e-491b-b910-88b8f45d3153"
                            ],
                            "worker": "5f0cb184c234"
                        },
                        "detailed-status": {
                            "Code": "0",
                            "output": "8c3c4990-3e64-4711-b5f2-e03f67834499"
                        }
                    },
                    "status": 202,
                    "charm_status": "completed"
                },
                "primitive": {
                    "ns-name": "k8s_controller_YOQD8O",
                    "primitive_data": {
                        "member_vnf_index": "1",
                        "primitive": "flexops",
                        "primitive_params": {
                            "config-content": {
                                "conf_files": [
                                    {
                                        "src": "http://192.168.103.246:5003/nfvcl_day2/day2/flannel_config_YOQD8O.yaml",
                                        "name": "kube_cni.yaml"
                                    },
                                    {
                                        "src": "http://192.168.103.246:5003/nfvcl_day2/day2/metallb_manifest_YOQD8O.yaml",
                                        "name": "metallb_manifest.yaml"
                                    },
                                    {
                                        "src": "http://192.168.103.246:5003/nfvcl_day2/day2/metallb_config_YOQD8O.yaml",
                                        "name": "metallb_config.yaml"
                                    },
                                    {
                                        "src": "http://192.168.103.246:5003/nfvcl_day2/day2/openebs_operator_YOQD8O.yaml",
                                        "name": "openebs_operator.yaml"
                                    },
                                    {
                                        "src": "http://192.168.103.246:5003/nfvcl_day2/day2/default_storageclass_YOQD8O.yaml",
                                        "name": "default_storageclass.yaml"
                                    },
                                    {
                                        "src": "http://192.168.103.246:5003/nfvcl_day2/day2/regcred_YOQD8O.yaml",
                                        "name": "regcred.yaml"
                                    }
                                ],
                                "playbooks": [
                                    {
                                        "prio": 10,
                                        "src": "http://192.168.103.246:5003/nfvcl_day2/day2/ansible_k8s_k8s_controller_YOQD8O_1_step1.yaml",
                                        "name": "ansible_k8s_k8s_controller_YOQD8O_1_step1.yaml"
                                    }
                                ],
                                "action_id": "8c3c4990-3e64-4711-b5f2-e03f67834499",
                                "post_url": "http://192.168.103.246:5003/nfvcl_day2/actions",
                                "nsd_id": "k8s_controller_YOQD8O",
                                "vnfd_id": 1,
                                "blue_id": "YOQD8O"
                            }
                        }
                    }
                },
                "time": "11/17/2021, 21:15:41"
            },
            {
                "result": {
                    "response": "{\n    \"id\": \"389dfdf9-641e-46b3-b213-ff133d36187b\"\n}\n",
                    "details": {
                        "_id": "389dfdf9-641e-46b3-b213-ff133d36187b",
                        "id": "389dfdf9-641e-46b3-b213-ff133d36187b",
                        "operationState": "COMPLETED",
                        "queuePosition": 0,
                        "stage": "",
                        "errorMessage": "",
                        "detailedStatus": None,
                        "statusEnteredTime": 1637183893.2802482,
                        "nsInstanceId": "e88d71b0-fff0-49bc-a45a-d8146bd20243",
                        "lcmOperationType": "action",
                        "startTime": 1637183741.4010017,
                        "isAutomaticInvocation": False,
                        "operationParams": {
                            "member_vnf_index": "1",
                            "primitive": "flexops",
                            "primitive_params": {
                                "config-content": {
                                    "conf_files": [],
                                    "playbooks": [
                                        {
                                            "prio": 10,
                                            "src": "http://192.168.103.246:5003/nfvcl_day2/day2/ansible_k8s_k8s_worker_tac_1_YOQD8O_1_step1.yaml",
                                            "name": "ansible_k8s_k8s_worker_tac_1_YOQD8O_1_step1.yaml"
                                        }
                                    ],
                                    "action_id": "03ce8ef8-f2f8-4222-820c-c6841ad3d65c",
                                    "post_url": "http://192.168.103.246:5003/nfvcl_day2/actions",
                                    "nsd_id": "k8s_worker_tac_1_YOQD8O",
                                    "vnfd_id": 1,
                                    "blue_id": "YOQD8O"
                                }
                            },
                            "lcmOperationType": "action",
                            "nsInstanceId": "e88d71b0-fff0-49bc-a45a-d8146bd20243"
                        },
                        "isCancelPending": False,
                        "links": {
                            "self": "/osm/nslcm/v1/ns_lcm_op_occs/389dfdf9-641e-46b3-b213-ff133d36187b",
                            "nsInstance": "/osm/nslcm/v1/ns_instances/e88d71b0-fff0-49bc-a45a-d8146bd20243"
                        },
                        "_admin": {
                            "created": 1637183741.4010541,
                            "modified": 1637183893.280251,
                            "projects_read": [
                                "d5bb416c-d75e-491b-b910-88b8f45d3153"
                            ],
                            "projects_write": [
                                "d5bb416c-d75e-491b-b910-88b8f45d3153"
                            ],
                            "worker": "5f0cb184c234"
                        },
                        "detailed-status": {
                            "Code": "0",
                            "output": "03ce8ef8-f2f8-4222-820c-c6841ad3d65c"
                        }
                    },
                    "status": 202,
                    "charm_status": "completed"
                },
                "primitive": {
                    "ns-name": "k8s_worker_tac_1_YOQD8O",
                    "primitive_data": {
                        "member_vnf_index": "1",
                        "primitive": "flexops",
                        "primitive_params": {
                            "config-content": {
                                "conf_files": [],
                                "playbooks": [
                                    {
                                        "prio": 10,
                                        "src": "http://192.168.103.246:5003/nfvcl_day2/day2/ansible_k8s_k8s_worker_tac_1_YOQD8O_1_step1.yaml",
                                        "name": "ansible_k8s_k8s_worker_tac_1_YOQD8O_1_step1.yaml"
                                    }
                                ],
                                "action_id": "03ce8ef8-f2f8-4222-820c-c6841ad3d65c",
                                "post_url": "http://192.168.103.246:5003/nfvcl_day2/actions",
                                "nsd_id": "k8s_worker_tac_1_YOQD8O",
                                "vnfd_id": 1,
                                "blue_id": "YOQD8O"
                            }
                        }
                    }
                },
                "time": "11/17/2021, 21:18:22"
            },
            {
                "result": {
                    "response": "{\n    \"id\": \"ee023a75-d9db-4707-9d97-1bb42baab5b4\"\n}\n",
                    "details": {
                        "_id": "ee023a75-d9db-4707-9d97-1bb42baab5b4",
                        "id": "ee023a75-d9db-4707-9d97-1bb42baab5b4",
                        "operationState": "COMPLETED",
                        "queuePosition": 0,
                        "stage": "",
                        "errorMessage": "",
                        "detailedStatus": None,
                        "statusEnteredTime": 1637183912.3570096,
                        "nsInstanceId": "cb5832a7-3e34-4954-8e62-53d74a062b6d",
                        "lcmOperationType": "action",
                        "startTime": 1637183902.3363063,
                        "isAutomaticInvocation": False,
                        "operationParams": {
                            "member_vnf_index": "1",
                            "primitive": "flexops",
                            "primitive_params": {
                                "config-content": {
                                    "conf_files": [],
                                    "playbooks": [
                                        {
                                            "prio": 10,
                                            "src": "http://192.168.103.246:5003/nfvcl_day2/day2/ansible_k8s_k8s_controller_YOQD8O_1_step2.yaml",
                                            "name": "ansible_k8s_k8s_controller_YOQD8O_1_step2.yaml"
                                        }
                                    ],
                                    "action_id": "4f42cf57-e2c5-4142-9a45-34f35875d471",
                                    "post_url": "http://192.168.103.246:5003/nfvcl_day2/actions",
                                    "nsd_id": "k8s_controller_YOQD8O",
                                    "vnfd_id": 1,
                                    "blue_id": "YOQD8O"
                                }
                            },
                            "lcmOperationType": "action",
                            "nsInstanceId": "cb5832a7-3e34-4954-8e62-53d74a062b6d"
                        },
                        "isCancelPending": False,
                        "links": {
                            "self": "/osm/nslcm/v1/ns_lcm_op_occs/ee023a75-d9db-4707-9d97-1bb42baab5b4",
                            "nsInstance": "/osm/nslcm/v1/ns_instances/cb5832a7-3e34-4954-8e62-53d74a062b6d"
                        },
                        "_admin": {
                            "created": 1637183902.336349,
                            "modified": 1637183912.357013,
                            "projects_read": [
                                "d5bb416c-d75e-491b-b910-88b8f45d3153"
                            ],
                            "projects_write": [
                                "d5bb416c-d75e-491b-b910-88b8f45d3153"
                            ],
                            "worker": "5f0cb184c234"
                        },
                        "detailed-status": {
                            "Code": "0",
                            "output": "4f42cf57-e2c5-4142-9a45-34f35875d471"
                        }
                    },
                    "status": 202,
                    "charm_status": "completed"
                },
                "primitive": {
                    "ns-name": "k8s_controller_YOQD8O",
                    "primitive_data": {
                        "member_vnf_index": "1",
                        "primitive": "flexops",
                        "primitive_params": {
                            "config-content": {
                                "conf_files": [],
                                "playbooks": [
                                    {
                                        "prio": 10,
                                        "src": "http://192.168.103.246:5003/nfvcl_day2/day2/ansible_k8s_k8s_controller_YOQD8O_1_step2.yaml",
                                        "name": "ansible_k8s_k8s_controller_YOQD8O_1_step2.yaml"
                                    }
                                ],
                                "action_id": "4f42cf57-e2c5-4142-9a45-34f35875d471",
                                "post_url": "http://192.168.103.246:5003/nfvcl_day2/actions",
                                "nsd_id": "k8s_controller_YOQD8O",
                                "vnfd_id": 1,
                                "blue_id": "YOQD8O"
                            }
                        }
                    }
                },
                "time": "11/17/2021, 21:18:32"
            }
        ]
    },
    {
        "id": "ul9maTvFQA",
        "type": "VO",
        "created": "01/20/2022, 18:08:30",
        "modified": "01/20/2022, 18:09:21",
        "supported_ops": [
            "init",
            "upgrade",
            "monitor",
            "log"
        ],
        "config": {
            "device": {
                "endpoint": "D001",
                "registrationId": "ul9maTvFQA",
                "address": "127.0.0.1:8080",
                "Version": "1.0",
                "lifetime": 30,
                "bindingMode": "M",
                "rootPath": "/",
                "resourceType": "oma.lwm2m",
                "secure": False,
                "additionalRegistrationAttributes": ""
            },
            "objectLinks": [
                "3303/0",
                "3303/1",
                "3303/2",
                "3326/0",
                "26242/0",
                "26243/0",
                "3306/1",
                "3306/2",
                "3306/3",
                "3306/4",
                "3306/5"
            ],
            "url": "tcp://192.168.25.128:1883",
            "cleanSession": True,
            "username": "",
            "password": "",
            "mqttQos": 0,
            "external_ip": "192.168.25.111"
        },
        "vims": [
            {
                "name": "os-5",
                "tenant": "admin",
                "core": True,
                "load_balancer_net": {
                    "id": "mngmnt-vnf"
                },
                "mgt": "mngmnt-vnf"
            }
        ],
        "ns": [
            {
                "status": "day2",
                "type": "vo",
                "vim": "os-5",
                "nsi_id": "110f7f03-e1c2-46ab-9a46-406f618f40a1",
                "nsd_id": "ca8add0c-b38a-41e8-94bc-145d3d9e4b08"
            }
        ],
        "vnfd": [
            {
                "id": "vo",
                "name": "ul9maTvFQA_vo",
                "vl": [
                    {
                        "vld": "data",
                        "mgt": True,
                        "k8s-cluster-net": "data_net",
                        "vim_net": "mngmnt-vnf"
                    }
                ]
            }
        ],
        "primitives": []
    }
]
"""
