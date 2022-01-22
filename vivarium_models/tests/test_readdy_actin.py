#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for actin ReaDDy models
"""

from vivarium_models import ReaddyActinProcess
from vivarium.core.composition import simulate_process
from vivarium_models.util import readdy_actin_test_monomers


def remove_extra_dim(list):
    # TODO figure out how to prevent the extra dim from being added
    return list[0]


def test_readdy_actin_process():
    """
    Test the initial ReaDDy actin process
    """
    # initialize the process
    readdy_actin_process = ReaddyActinProcess({})
    # run the simulation
    sim_settings = {
        "total_time": 0.000000005,  # 50 steps
        "initial_state": readdy_actin_test_monomers,
    }
    output = simulate_process(readdy_actin_process, sim_settings)["monomers"]

    found_monomer = False
    found_dimer = False
    assert len(output["topologies"]) == 2
    for t in output["topologies"]:
        top = output["topologies"][t]
        if top["type_name"][0] == "Actin-Monomer":
            found_monomer = True
            particle_ids = remove_extra_dim(top["particle_ids"])
            assert len(particle_ids) == 1
            assert "actin#free" in remove_extra_dim(
                output["particles"][str(particle_ids[0])]["type_name"]
            )
            assert (
                len(
                    remove_extra_dim(
                        output["particles"][str(particle_ids[0])]["neighbor_ids"]
                    )
                )
                == 0
            )
        if top["type_name"][0] == "Arp23-Dimer":
            found_dimer = True
            particle_ids = remove_extra_dim(top["particle_ids"])
            assert len(particle_ids) == 2
            assert "arp2" in remove_extra_dim(
                output["particles"][str(particle_ids[0])]["type_name"]
            )
            assert remove_extra_dim(
                output["particles"][str(particle_ids[0])]["neighbor_ids"]
            ) == [2]
            assert "arp3" in remove_extra_dim(
                output["particles"][str(particle_ids[1])]["type_name"]
            )
            assert remove_extra_dim(
                output["particles"][str(particle_ids[1])]["neighbor_ids"]
            ) == [1]
    assert found_monomer
    assert found_dimer
