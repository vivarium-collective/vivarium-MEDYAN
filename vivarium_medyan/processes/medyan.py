import os
import numpy as np
import argparse

from vivarium.core.process import Process
from vivarium.core.composition import (
    simulate_process,
    PROCESS_OUT_DIR,
)
from vivarium.plots.simulation_output import plot_simulation_output

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("vivarium_models"), autoescape=select_autoescape()
)

from pathlib import Path
import subprocess

NAME = "MEDYAN"


def fiber_to_string(type_name, points):
    point_strs = [" ".join([str(element) for element in point]) for point in points]
    line = " ".join(["FILAMENT", str(type_name)] + point_strs)
    return line


def read_coordinates(coordinates_line):
    coordinate_strs = coordinates_line.strip().split(" ")
    coordinates = []
    for n in range(0, len(coordinate_strs), 3):
        point = coordinate_strs[n : n + 3]
        coordinates.append(np.array([float(p) for p in point]))
    return coordinates


def read_fiber(fiber_line, coordinates_line):
    _, id, type, length, delta_l, delta_r = fiber_line.split(" ")
    coordinates = read_coordinates(coordinates_line)
    return {id: {"type_name": type, "points": coordinates}}


class MedyanProcess(Process):
    """
    MEDYAN
    """

    name = NAME

    defaults = {
        "input_directory": "in/filaments",
        "output_directory": "out/filaments",
        "system_template": "filament-system.txt",
        "system_file": "filament-system.txt",
        "fiber_file": "filaments.txt",
        "medyan_executable": "medyan",
        "snapshot": 1.0,
        "tranform_bounds": np.array([0, 0, 0]),
        # TODO: provide a way to parameterize type name,
        #    translating between simulation type names and MEDYAN type indexes
    }

    def __init__(self, parameters=None):
        super().__init__(parameters)

        assert self.parameters["time_step"] > self.parameters["snapshot"]

    def ports_schema(self):
        return {
            "fibers": {
                "*": {
                    "type_name": {
                        "_default": "",
                        "_updater": "set",
                        "_emit": True,
                    },
                    "points": {  # list of shape (3) numpy arrays
                        "_default": [],
                        "_updater": "set",
                        "_emit": True,
                    },
                }
            }
        }

    def initial_state(self, config):
        initial_fibers = {
            unique_id: {"type_name": "A", "points": points}
            for unique_id, points in config.get("fibers", {}).items()
        }
        return {"fibers": initial_fibers}

    def transform_points(self, points, inverse=False):
        transform = np.array(self.parameters["transform_points"])
        if inverse:
            transform = -transform
        return [transform + point for point in points]

    def transform_fiber(self, fiber, inverse=False):
        fiber["points"] = self.transform_points(fiber["points"], inverse)
        return fiber

    def read_snapshot(self, snapshot_path):
        # TODO: read only the last timepoint for each fiber

        with open(snapshot_path, "r") as snapshot:
            snapshot_lines = snapshot.read().split("\n")

        index = 0
        fibers = {}
        while index < len(snapshot_lines):
            line = snapshot_lines[index]
            if "FILAMENT" in line:
                # TODO: parse line and pull out fiber id and type
                coordinates_line = snapshot_lines[index + 1]
                fiber = read_fiber(line, coordinates_line)
                fibers.update(fiber)
                index += 2
            else:
                index += 1

        return fibers

    def next_update(self, timestep, state):
        print("in medyan process next update")

        initial_fibers = state["fibers"]
        fiber_ids = list(initial_fibers.keys())

        fiber_types = set()
        for fiber in initial_fibers.values():
            fiber_types.add(fiber["type_name"])
        num_fiber_types = len(fiber_types)

        fiber_lines = [
            fiber_to_string(fiber["type_name"], self.transform_points(fiber["points"]))
            for fiber in initial_fibers.values()
        ]

        input_directory = Path(self.parameters["input_directory"])

        fiber_text = "\n".join(fiber_lines)

        fiber_path = input_directory / self.parameters["fiber_file"]
        with open(fiber_path, "w") as fiber_file:
            fiber_file.write(fiber_text)

        system_template = self.parameters["system_template"]
        template = env.get_template(system_template)
        system_text = template.render(
            fiber_file=self.parameters["fiber_file"],
            num_fiber_types=num_fiber_types,
            timestep=timestep,
            snapshot_time=self.parameters["snapshot"],
        )

        system_path = input_directory / self.parameters["system_file"]
        with open(system_path, "w") as system_file:
            system_file.write(system_text)

        medyan_command = [
            self.parameters["medyan_executable"],
            "-s",
            system_file.name,
            "-i",
            str(input_directory),
            "-o",
            self.parameters["output_directory"],
        ]

        medyan_process = subprocess.Popen(medyan_command, stdout=subprocess.PIPE)
        output, error = medyan_process.communicate()

        print(output.decode("utf-8"))

        # TODO: perform the reverse transform for output points

        output_directory = Path(self.parameters["output_directory"])
        fibers = self.read_snapshot(output_directory / "snapshot.traj")

        fibers = {
            fiber_ids[int(id)]: self.transform_fiber(fiber, inverse=True)
            for id, fiber in fibers.items()
        }

        return {"fibers": fibers}


def main():
    """Simulate the process and plot results."""
    parser = argparse.ArgumentParser(description="Run a MEDYAN simulation")
    parser.add_argument(
        "medyan_executable_path",
        help="the file path to the MEDYAN executable",
    )
    args = parser.parse_args()

    # make an output directory to save plots
    out_dir = os.path.join(PROCESS_OUT_DIR, NAME)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    medyan = MedyanProcess(
        {
            # "...../medyan/build/medyan"
            "medyan_executable": args.medyan_executable_path,
            "transform_points": [500, 500, 500],
            "time_step": 10.0,
        }
    )
    initial_state = {
        "fibers": {
            "1": {
                "type_name": "Actin-Polymer",
                "points": [np.array([-70.0, 0.0, 100.0]), np.array([10.0, 100.0, 0.0])],
            },
            "2": {
                "type_name": "Actin-Polymer",
                "points": [np.array([-70.0, 100.0, 0.0]), np.array([10.0, 0.0, 100.0])],
            },
        }
    }

    output = simulate_process(
        medyan,
        {"initial_state": initial_state, "total_time": 100, "return_raw_data": True},
    )

    # plot the simulation output
    plot_settings = {}
    plot_simulation_output(output, plot_settings, out_dir)


if __name__ == "__main__":
    main()
