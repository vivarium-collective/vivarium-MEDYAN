import os
import numpy as np
import argparse
import shutil

from vivarium.core.process import Process
from vivarium.core.composition import simulate_process
from vivarium.plots.simulation_output import plot_simulation_output

from jinja2 import Environment, FileSystemLoader, select_autoescape

from pathlib import Path
import subprocess
from vivarium_medyan.library.schema import fibers_schema
from vivarium_medyan.data.fibers import initial_fibers

NAME = "MEDYAN"


class MedyanProcess(Process):
    """
    MEDYAN
    """

    name = NAME

    defaults = {
        "model_name": "medyan_Chandrasekaran_2019_no_tread_2mUNI_alphaA_0.1_MA_0.675",
        "input_directory": "in/",
        "output_directory": "out/",
        "template_directory": "vivarium_medyan/templates/",
        "medyan_executable": "medyan",
        "snapshot": 1.0,
        "transform_points": np.array([0, 0, 0]),
        "filament_projection_type": "",
    }

    def __init__(self, parameters=None):
        super().__init__(parameters)
        assert self.parameters["time_step"] >= self.parameters["snapshot"]
        self._jinja_environment = None
        self.filament_type_names = []
        self.input_path = Path(self.parameters["input_directory"]) / Path(
            self.parameters["model_name"]
        )
        if not os.path.exists(self.input_path):
            os.makedirs(self.input_path)
        self.output_path = Path(self.parameters["output_directory"]) / Path(
            self.parameters["model_name"]
        )
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def jinja_environment(self):
        if self._jinja_environment is None:
            self._jinja_environment = Environment(
                loader=FileSystemLoader(self.parameters["template_directory"]),
                autoescape=select_autoescape(),
            )
        return self._jinja_environment

    def ports_schema(self):
        return fibers_schema()

    def initial_state(self, config):
        return {}

    def next_update(self, timestep, state):
        print("in medyan process next update")

        init_fibers = state["fibers"]

        # move additional config files to input directory
        template_directory = Path(self.parameters["template_directory"]) / Path(
            self.parameters["model_name"]
        )
        config_files = template_directory.glob("*")
        for config_file in config_files:
            if (
                self.parameters["model_name"] in config_file.name
                or "txt" not in config_file.suffix
            ):
                continue
            shutil.copyfile(config_file, self.input_path / config_file.name)

        # create fiber input file
        fiber_lines = [
            self.fiber_to_string(
                fiber["type_name"], self.transform_points(fiber["points"])
            )
            for fiber in init_fibers.values()
        ]
        fiber_text = "\n".join(fiber_lines)
        fiber_path = self.input_path / "filaments.txt"
        with open(fiber_path, "w") as fiber_file:
            fiber_file.write(fiber_text)

        # render template
        system_template_path = str(
            Path(self.parameters["model_name"])
            / (self.parameters["model_name"] + ".txt")
        )
        template = self.jinja_environment().get_template(system_template_path)
        system_text = template.render(
            timestep=timestep,
            snapshot_time=self.parameters["snapshot"],
            projection_type=""
            if not self.parameters["filament_projection_type"]
            else "PROJECTIONTYPE:               "
            + self.parameters["filament_projection_type"],
        )
        system_file_path = self.input_path / (self.parameters["model_name"] + ".txt")
        with open(system_file_path, "w") as system_file:
            system_file.write(system_text)

        # run MEDYAN
        medyan_command = [
            self.parameters["medyan_executable"],
            "-s",
            system_file.name,
            "-i",
            str(self.input_path),
            "-o",
            Path(self.parameters["output_directory"])
            / Path(self.parameters["model_name"]),
        ]
        medyan_process = subprocess.Popen(medyan_command, stdout=subprocess.PIPE)
        output, error = medyan_process.communicate()
        print(output.decode("utf-8"))

        # get outputs
        box_extent = MedyanProcess.read_box_extent(system_text)
        fibers = self.read_snapshot(self.output_path / "snapshot.traj")
        fibers = {
            fiber_id: self.transform_fiber(fiber, inverse=True)
            for fiber_id, fiber in fibers.items()
        }

        # import ipdb; ipdb.set_trace()

        return {"fibers_box_extent": box_extent, "fibers": fibers}

    def transform_points(self, points, inverse=False):
        transform = np.array(self.parameters["transform_points"])
        if inverse:
            transform = -transform
        return [transform + point for point in points]

    def transform_fiber(self, fiber, inverse=False):
        fiber["points"] = self.transform_points(fiber["points"], inverse)
        return fiber

    def read_snapshot(self, snapshot_path):
        # TODO: optimize to read only the last timepoint for each fiber
        with open(snapshot_path, "r") as snapshot:
            snapshot_lines = snapshot.read().split("\n")
        index = 0
        fibers = {}
        while index < len(snapshot_lines):
            line = snapshot_lines[index]
            if "FILAMENT" in line:
                coordinates_line = snapshot_lines[index + 1]
                fiber = self.read_fiber(line, coordinates_line)
                fibers.update(fiber)
                index += 2
            else:
                index += 1
        return fibers

    def fiber_to_string(self, type_name, points):
        if type_name not in self.filament_type_names:
            type_index = len(self.filament_type_names)
            self.filament_type_names.append(type_name)
        else:
            type_index = self.filament_type_names.index(type_name)
        type_name = self.filament_type_names[type_index]
        point_strs = [" ".join([str(element) for element in point]) for point in points]
        line = " ".join(["FILAMENT", str(type_index)] + point_strs)
        return line

    @staticmethod
    def read_coordinates(coordinates_line):
        coordinate_strs = coordinates_line.strip().split(" ")
        coordinates = []
        for n in range(0, len(coordinate_strs), 3):
            point = coordinate_strs[n : n + 3]
            coordinates.append(np.array([float(p) for p in point]))
        return coordinates

    def read_fiber(self, fiber_line, coordinates_line):
        _, fiber_id, type_index, length, delta_l, delta_r = fiber_line.split(" ")
        type_name = self.filament_type_names[int(type_index)]
        coordinates = MedyanProcess.read_coordinates(coordinates_line)
        return {fiber_id: {"type_name": type_name, "points": coordinates}}

    @staticmethod
    def read_box_extent(system_text):
        lines = system_text.split("\n")
        n_compartments = np.zeros(3)
        compartment_size = np.zeros(3)
        coords = ["X", "Y", "Z"]
        for line in lines:
            for dim in range(len(coords)):
                coord = coords[dim]
                if f"N{coord}:" in line:
                    n_compartments[dim] = int(line.split()[1])
                if f"COMPARTMENTSIZE{coord}:" in line:
                    compartment_size[dim] = float(line.split()[1])
        return np.multiply(n_compartments, compartment_size)


def main():
    """Simulate the process and plot results."""
    parser = argparse.ArgumentParser(description="Run a MEDYAN simulation")
    parser.add_argument(
        "medyan_executable_path",
        help="the file path to the MEDYAN executable",
    )
    args = parser.parse_args()
    medyan = MedyanProcess(
        {
            "medyan_executable": args.medyan_executable_path,
            "transform_points": [2000.0, 1000.0, 1000.0],
            "time_step": 10.0,
        }
    )
    output = simulate_process(
        medyan,
        {"initial_state": initial_fibers, "total_time": 30, "return_raw_data": True},
    )


if __name__ == "__main__":
    main()
