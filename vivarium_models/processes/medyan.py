import os
import numpy as np
import argparse

from vivarium.core.process import Process
from vivarium.core.composition import (
    simulate_process,
    PROCESS_OUT_DIR,
)
from vivarium.plots.simulation_output import plot_simulation_output
from vivarium_models.util import medyan_chandrasekaran_2019_fibers

from jinja2 import Environment, PackageLoader, select_autoescape
from simularium_models_util.actin import ActinGenerator, FiberData

env = Environment(
    loader=PackageLoader("vivarium_models"), autoescape=select_autoescape()
)

from pathlib import Path
import subprocess

NAME = "MEDYAN"
DEFAULT_COMPARTMENT_SIZE = 500.0


class MedyanProcess(Process):
    """
    MEDYAN
    """

    name = NAME

    defaults = {
        "model_name": "medyan_Chandrasekaran_2019_no_tread_2mUNI_alphaA_0.1_MA_0.675",
        "input_directory": "in/",
        "output_directory": "out/",
        "medyan_executable": "medyan",
        "snapshot": 1.0,
        # TODO: provide a way to parameterize type name,
        #    translating between simulation type names and MEDYAN type indexes
    }

    def __init__(self, parameters=None):
        super().__init__(parameters)

        assert self.parameters["time_step"] > self.parameters["snapshot"]

    def ports_schema(self):
        return {
            "fibers_box_size": {
                "_default": 0.0,
                "_updater": "set",
                "_emit": True,
            },
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
            },
        }

    def initial_state(self, config):
        initial_fibers = {
            unique_id: {"type_name": "A", "points": points}
            for unique_id, points in config.get("fibers", {}).items()
        }
        return {
            "fibers_box_size": config["fibers_box_size"],
            "fibers": initial_fibers,
        }

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
                fiber = MedyanProcess.read_fiber(line, coordinates_line)
                fibers.update(fiber)
                index += 2
            else:
                index += 1

        return fibers

    def next_update(self, timestep, state):
        print("UNICORN in medyan process next update")

        initial_fibers = state["fibers"]
        fibers_data = []
        for fiber_id in initial_fibers:
            fibers_data.append(FiberData(
                fiber_id=fiber_id,
                points=initial_fibers[fiber_id]["points"],
                type_name=initial_fibers[fiber_id]["type_name"],
            ))
        
        cropped_fibers_data = ActinGenerator.get_cropped_fibers(
            fibers_data=fibers_data, 
            min_extent=np.zeros(3),
            max_extent=np.array(3 * [state["fibers_box_size"]]),
        )
        cropped_fibers = {
            fiber_data.fiber_id : {
                "type_name": "Actin-Polymer", # TODO convert MEDYAN types
                "points": fiber_data.points
            }
            for fiber_data in cropped_fibers_data
        }
        
        fiber_ids = list(cropped_fibers.keys())

        fiber_lines = [
            MedyanProcess.fiber_to_string(
                fiber["type_name"], fiber["points"]
            )
            for fiber in cropped_fibers.values()
        ]

        input_directory = Path(self.parameters["input_directory"]) / Path(
            self.parameters["model_name"]
        )

        output_directory = Path(self.parameters["output_directory"]) / Path(
            self.parameters["model_name"]
        )
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        fiber_text = "\n".join(fiber_lines)

        fiber_path = input_directory / "filaments.txt"
        with open(fiber_path, "w") as fiber_file:
            fiber_file.write(fiber_text)
            
        n_compartments = int(round(
            float(state["fibers_box_size"]) / DEFAULT_COMPARTMENT_SIZE))
        system_template = self.parameters["model_name"] + ".txt"
        template = env.get_template(system_template)
        system_text = template.render(
            timestep=timestep,
            snapshot_time=self.parameters["snapshot"],
            n_compartments=n_compartments,
        )

        system_path = input_directory / (self.parameters["model_name"] + ".txt")
        with open(system_path, "w") as system_file:
            system_file.write(system_text)

        medyan_command = [
            self.parameters["medyan_executable"],
            "-s",
            system_file.name,
            "-i",
            str(input_directory),
            "-o",
            Path(self.parameters["output_directory"])
            / Path(self.parameters["model_name"]),
        ]

        medyan_process = subprocess.Popen(medyan_command, stdout=subprocess.PIPE)
        output, error = medyan_process.communicate()

        print(output.decode("utf-8"))

        fibers = self.read_snapshot(output_directory / "snapshot.traj")

        fibers = {
            fiber_ids[int(id)]: fiber
            for id, fiber in fibers.items()
        }
        
        # import ipdb; ipdb.set_trace()
        
        return {"fibers": fibers}

    @staticmethod
    def fiber_to_string(type_name, points):
        point_strs = [" ".join([str(element) for element in point]) for point in points]
        line = " ".join(["FILAMENT", str(type_name)] + point_strs)
        return line

    @staticmethod
    def read_coordinates(coordinates_line):
        coordinate_strs = coordinates_line.strip().split(" ")
        coordinates = []
        for n in range(0, len(coordinate_strs), 3):
            point = coordinate_strs[n : n + 3]
            coordinates.append(np.array([float(p) for p in point]))
        return coordinates

    @staticmethod
    def read_fiber(fiber_line, coordinates_line):
        _, id, type_name, length, delta_l, delta_r = fiber_line.split(" ")
        coordinates = MedyanProcess.read_coordinates(coordinates_line)
        return {
            id: {
                "type_name": "Actin-Polymer",  # TODO convert MEDYAN integer type to type name
                "points": coordinates
            }
        }


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
            "medyan_executable": args.medyan_executable_path,
            "time_step": 10.0,
        }
    )
    initial_state = {
        "fibers_box_size": 4000.0,
        "fibers": medyan_chandrasekaran_2019_fibers,
    }

    output = simulate_process(
        medyan,
        {
            "initial_state": initial_state, 
            "total_time": 100, 
            "return_raw_data": True
        },
    )

    # plot the simulation output
    plot_settings = {}
    plot_simulation_output(output, plot_settings, out_dir)


if __name__ == "__main__":
    main()
