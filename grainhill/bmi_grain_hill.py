#! /usr/bin/env python
"""Basic Model Interface implementation for the GrainHill model."""

import numpy as np

from bmipy import Bmi
from grainhill import GrainHill
from landlab import load_params

_DEFAULT_PARAMETERS = {
    'report_interval': 100000000.0,
    'run_duration': 1.0,
    'output_interval': 1e+99,
    'disturbance_rate': 1.0,
    'weathering_rate': 1.0,
    'dissolution_rate': 0.0,
    'uplift_interval': 1.0,
    'plot_interval': 1e+99,
    'friction_coef': 0.3,
    'rock_state_for_uplift': 7,
    'opt_rock_collapse': False,
    'opt_track_grains': False,
    'grid_size': (5, 5),
    'cell_width': 1.0,
    'grav_accel': 9.8,
}


class BmiGrainHill(Bmi):

    """Simulate hillslope profile evolution."""

    _name = "BmiGrainHill"
    _input_var_names = ("node_state",)
    _output_var_names = ("node_state",)

    def __init__(self):
        """Create a BmiGrainHill model that is ready for initialization."""
        self._model = None
        self._values = {}
        self._var_units = {}
        self._var_loc = {}
        self._grids = {}
        self._grid_type = {}

        self._start_time = 0.0
        self._end_time = np.finfo("d").max
        self._time_units = "y"

    def initialize(self, filename=None):
        """Initialize the GrainHill model.

        Parameters
        ----------
        filename : str, optional
            Path to name of input file.
        """
        if isinstance(filename, str):
            p = load_params(filename)
        elif isinstance(filename, dict):
            p = filename
        else:
            p = _DEFAULT_PARAMETERS
        if ('number_of_node_rows' in p and 'number_of_node_columns' in p):
            p['grid_size'] = (p['number_of_node_rows'],
                              p['number_of_node_columns'])
            p.pop('number_of_node_rows')
            p.pop('number_of_node_columns')

        # Handle plotting and output options


        self._model = GrainHill(**p)
        self.grid = self._model.grid  # Landlab grid as public attribute

        self._values = {"node_state": self.grid.at_node['node_state']}
        self._var_units = {"node_state": "-"}
        self._var_loc = {"node_state": "node"}
        self._grids = {0: ["node_state"]}
        self._grid_type = {0: "unstructured"}  # closest BMI category to hexagona

        self._initialized = True

    def update(self):
        """Advance forward for one year."""
        self._model.run(to=self._model.current_time + 1.0)

    def update_frac(self, time_frac):
        """Update model by a fraction of a time step.

        Parameters
        ----------
        time_frac : float
            Fraction of a year.
        """
        self._model.run(to=self._model.current_time + time_frac)

    def update_until(self, then):
        """Update model until a particular time.

        Parameters
        ----------
        then : float
            Time to run model until.
        """
        self._model.run(to=then)

    # def run(self):
    #     """Run model from start to finish.
    #
    #     This is not a BMI function, but helpful to have nonetheless.
    #     """
    #     if not self._initialized:
    #         print('Must call initialize() before run()')
    #         raise Exception
    #
    #     self.plot_to_file()
    #     next_file_plot = self.file_plot_interval
    #     uplift_change_time = self.uplift_duration
    #     while self.model.current_time < self.run_duration:
    #         next_pause = min(next_file_plot, self.run_duration)
    #         next_pause = min(next_pause, uplift_change_time)
    #         if self.model.current_time >= uplift_change_time:
    #             self.model.next_uplift = self.run_duration
    #             uplift_change_time = self.run_duration
    #         self.update_until(next_pause)
    #         if self.model.current_time >= next_file_plot:
    #             self.plot_to_file()
    #             next_file_plot += self.file_plot_interval
    #
    def finalize(self):
        """Finalize model."""
        self._model = None

    def get_var_type(self, var_name):
        """Data type of variable.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        str
            Data type.
        """
        return str(self.get_value_ptr(var_name).dtype)

    def get_var_units(self, var_name):
        """Get units of variable.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        str
            Variable units.
        """
        return self._var_units[var_name]

    def get_var_nbytes(self, var_name):
        """Get units of variable.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        int
            Size of data array in bytes.
        """
        return self.get_value_ptr(var_name).nbytes

    def get_var_itemsize(self, name):
        return np.dtype(self.get_var_type(name)).itemsize

    def get_var_location(self, name):
        return self._var_loc[name]

    def get_var_grid(self, var_name):
        """Grid id for a variable.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        int
            Grid id.
        """
        for grid_id, var_name_list in self._grids.items():
            if var_name in var_name_list:
                return grid_id

    def get_grid_rank(self, grid_id):
        """Rank of grid.

        Parameters
        ----------
        grid_id : int
            Identifier of a grid.

        Returns
        -------
        int
            Rank of grid.
        """
        return 2

    def get_grid_size(self, grid_id):
        """Size of grid.

        Parameters
        ----------
        grid_id : int
            Identifier of a grid.

        Returns
        -------
        int
            Size of grid.
        """
        return self.grid.number_of_nodes

    def get_value_ptr(self, var_name):
        """Reference to values.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        array_like
            Value array.
        """
        return self._values[var_name]

    def get_value(self, var_name):
        """Copy of values.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.

        Returns
        -------
        array_like
            Copy of values.
        """
        return self.get_value_ptr(var_name).copy()

    def get_value_at_indices(self, var_name, indices):
        """Get values at particular indices.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.
        indices : array_like
            Array of indices.

        Returns
        -------
        array_like
            Values at indices.
        """
        return self.get_value_ptr(var_name).take(indices)

    def set_value(self, var_name, src):
        """Set model values.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.
        src : array_like
            Array of new values.
        """
        val = self.get_value_ptr(var_name)
        val[:] = src

    def set_value_at_indices(self, name, inds, src):
        """Set model values at particular indices.

        Parameters
        ----------
        var_name : str
            Name of variable as CSDMS Standard Name.
        src : array_like
            Array of new values.
        indices : array_like
            Array of indices.
        """
        val = self.get_value_ptr(name)
        val.flat[inds] = src

    def get_component_name(self):
        """Name of the component."""
        return self._name

    def get_input_item_count(self):
        """Get names of input variables."""
        return len(self._input_var_names)

    def get_output_item_count(self):
        """Get names of output variables."""
        return len(self._output_var_names)

    def get_input_var_names(self):
        """Get names of input variables."""
        return self._input_var_names

    def get_output_var_names(self):
        """Get names of output variables."""
        return self._output_var_names

    def get_grid_shape(self, grid_id):
        """Number of rows and columns of uniform rectilinear grid."""
        return np.array([self.grid.number_of_node_rows,
                         self.grid.number_of_node_columns],
                         dtype=np.int)

    def get_grid_spacing(self, grid_id):
        """Spacing of rows and columns of uniform rectilinear grid."""
        return 1.0

    def get_grid_origin(self, grid_id):
        """Origin of uniform rectilinear grid."""
        return np.zeros(2)

    def get_grid_type(self, grid_id):
        """Type of grid."""
        return self._grid_type[grid_id]

    def get_start_time(self):
        """Start time of model."""
        return 0.0

    def get_end_time(self):
        """End time of model."""
        return self._model.run_duration

    def get_current_time(self):
        return self._model.current_time

    def get_time_step(self):
        return 1.0  # GrainHill does not use a time step

    def get_time_units(self):
        return "y"

    def get_grid_edge_count(self, grid):
        return self.grid.number_of_links

    def get_grid_edge_nodes(self, grid, edge_nodes):
        edge_nodes[:] = self.grid.nodes_at_link.flatten()
        return 0

    def get_grid_face_count(self, grid):
        return self.grid.number_of_cells

    def get_grid_node_count(self, grid):
        return self.grid.number_of_nodes

    def get_grid_nodes_per_face(self, grid, nodes_per_face):
        nodes_per_face[:] = 6 + np.zeros(self.grid.number_of_cells,
                                         dtype=np.int)
        return 0

    def get_grid_x(self, grid, x):
        x[:] = self.grid.x_of_node
        return 0

    def get_grid_y(self, grid, y):
        y[:] = self.grid.y_of_node
        return 0

    # To implement, Landlab HexModelGrid first needs
    # a nodes_at_cell property
    def get_grid_face_nodes(self, grid, face_nodes):
        raise NotImplementedError("get_grid_node_count")

    def get_grid_face_edges(self, grid, face_edges):
        raise NotImplementedError("get_grid_node_count")

    def get_grid_z(self, grid, z):
        raise NotImplementedError("get_grid_z")
