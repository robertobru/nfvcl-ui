from threading import Thread
from time import sleep

import requests

get_headers = {"Accept": "application/json"}
post_headers = {"Accept": "application/json", "Content-type": "application/json"}
nfvcl_base_url = "http://127.0.0.1:5003"

topology_data_raw = {'vims': [], 'networks': [], 'routers': []}
pdu_data_raw = []
blue_data_generic = []
blue_detailed = []
nsi_data = []
vnf_data = []
blue_type = []

def get_dynamic_data():
    return {
        'topology_data_raw': topology_data_raw,
        'pdu_data_raw': pdu_data_raw,
        'blue_data_generic': blue_data_generic,
        'blue_detailed': blue_detailed,
        'nsi_data': nsi_data,
        'vnf_data': blue_vnfs,
        'blue_type': blue_type
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
        blue_vnfs, blue_type
    while True:
        # print('@@@ resting')
        blue_type = requests.get(
            "{}/nfvcl/api/bluetype".format(nfvcl_base_url), params=None, verify=False, stream=True,
            headers=get_headers).json()
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

