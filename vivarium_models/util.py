import numpy as np

def agents_update(existing, projected):
    update = {"_add": [], "_delete": []}

    for id, state in projected.items():
        if id in existing:
            update[id] = state
        else:
            update["_add"].append({"key": id, "state": state})

    for existing_id in existing.keys():
        if existing_id not in projected:
            update["_delete"].append(existing_id)

    return update


def create_monomer_update(previous_monomers, new_monomers, box_center, box_size):
    topologies_update = agents_update(
        previous_monomers["topologies"], new_monomers["topologies"]
    )

    particles_update = agents_update(
        previous_monomers["particles"], new_monomers["particles"]
    )

    return {
        "monomers": {
            "box_center": box_center,
            "box_size": box_size,
            "topologies": topologies_update, 
            "particles": particles_update
        }
    }
    


readdy_actin_test_monomers = {
    "monomers": {
        "box_center": np.zeros(3),  # to be chosen by alternator
        "box_size": 0.0,
        "topologies": {
            1: {
                "type_name": "Arp23-Dimer",
                "particle_ids": [1, 2],
            },
            0: {
                "type_name": "Actin-Monomer",
                "particle_ids": [0],
            },
        },
        "particles": {
            0: {
                "type_name": "actin#free_ATP",
                "position": np.array([2, 0, 0]),
                "neighbor_ids": [],
            },
            1: {
                "type_name": "arp2",
                "position": np.array([0, 0, 0]),
                "neighbor_ids": [2],
            },
            2: {
                "type_name": "arp3#ATP",
                "position": np.array([0, 0, 4]),
                "neighbor_ids": [1],
            },
        },
    }
}

medyan_chandrasekaran_2019_fibers = {
    # "1": {
    #     "type_name": "Actin-Polymer",
    #     "points": [
    #         np.array([1000.00000000, 2000.00000000, 2000.00000000]),
    #         np.array([3160.00000000, 2000.00000000, 2000.00000000]),
    #     ],
    # },
    "1": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 912.50000000, 1000.00000000]),
            np.array([3160.00000000, 912.50000000, 1000.00000000]),
        ],
    },
    "2": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 947.50000000, 939.37822174]),
            np.array([3160.00000000, 947.50000000, 939.37822174]),
        ],
    },
    "3": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 930.00000000, 969.68911087]),
            np.array([3160.00000000, 930.00000000, 969.68911087]),
        ],
    },
    "4": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 947.50000000, 1000.00000000]),
            np.array([3160.00000000, 947.50000000, 1000.00000000]),
        ],
    },
    "5": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 930.00000000, 1030.31088913]),
            np.array([3160.00000000, 930.00000000, 1030.31088913]),
        ],
    },
    "6": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 947.50000000, 1060.62177826]),
            np.array([3160.00000000, 947.50000000, 1060.62177826]),
        ],
    },
    "7": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 965.00000000, 909.06733260]),
            np.array([3160.00000000, 965.00000000, 909.06733260]),
        ],
    },
    "8": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 982.50000000, 939.37822174]),
            np.array([3160.00000000, 982.50000000, 939.37822174]),
        ],
    },
    "9": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 965.00000000, 969.68911087]),
            np.array([3160.00000000, 965.00000000, 969.68911087]),
        ],
    },
    "10": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 982.50000000, 1000.00000000]),
            np.array([3160.00000000, 982.50000000, 1000.00000000]),
        ],
    },
    "11": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 965.00000000, 1030.31088913]),
            np.array([3160.00000000, 965.00000000, 1030.31088913]),
        ],
    },
    "12": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 982.50000000, 1060.62177826]),
            np.array([3160.00000000, 982.50000000, 1060.62177826]),
        ],
    },
    "13": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 965.00000000, 1090.93266740]),
            np.array([3160.00000000, 965.00000000, 1090.93266740]),
        ],
    },
    "14": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1000.00000000, 909.06733260]),
            np.array([3160.00000000, 1000.00000000, 909.06733260]),
        ],
    },
    "15": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1017.50000000, 939.37822174]),
            np.array([3160.00000000, 1017.50000000, 939.37822174]),
        ],
    },
    "16": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1000.00000000, 969.68911087]),
            np.array([3160.00000000, 1000.00000000, 969.68911087]),
        ],
    },
    "17": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1017.50000000, 1000.00000000]),
            np.array([3160.00000000, 1017.50000000, 1000.00000000]),
        ],
    },
    "18": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1000.00000000, 1030.31088913]),
            np.array([3160.00000000, 1000.00000000, 1030.31088913]),
        ],
    },
    "19": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1017.50000000, 1060.62177826]),
            np.array([3160.00000000, 1017.50000000, 1060.62177826]),
        ],
    },
    "20": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1000.00000000, 1090.93266740]),
            np.array([3160.00000000, 1000.00000000, 1090.93266740]),
        ],
    },
    "21": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1035.00000000, 909.06733260]),
            np.array([3160.00000000, 1035.00000000, 909.06733260]),
        ],
    },
    "22": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1052.50000000, 939.37822174]),
            np.array([3160.00000000, 1052.50000000, 939.37822174]),
        ],
    },
    "23": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1035.00000000, 969.68911087]),
            np.array([3160.00000000, 1035.00000000, 969.68911087]),
        ],
    },
    "24": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1052.50000000, 1000.00000000]),
            np.array([3160.00000000, 1052.50000000, 1000.00000000]),
        ],
    },
    "25": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1035.00000000, 1030.31088913]),
            np.array([3160.00000000, 1035.00000000, 1030.31088913]),
        ],
    },
    "26": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1052.50000000, 1060.62177826]),
            np.array([3160.00000000, 1052.50000000, 1060.62177826]),
        ],
    },
    "27": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1035.00000000, 1090.93266740]),
            np.array([3160.00000000, 1035.00000000, 1090.93266740]),
        ],
    },
    "28": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1070.00000000, 969.68911087]),
            np.array([3160.00000000, 1070.00000000, 969.68911087]),
        ],
    },
    "29": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1087.50000000, 1000.00000000]),
            np.array([3160.00000000, 1087.50000000, 1000.00000000]),
        ],
    },
    "30": {
        "type_name": "Actin-Polymer",
        "points": [
            np.array([1000.00000000, 1070.00000000, 1030.31088913]),
            np.array([3160.00000000, 1070.00000000, 1030.31088913]),
        ],
    },
}
