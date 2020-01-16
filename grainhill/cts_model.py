#!/usr/env/python
"""
Base class for a "full" generic CTS model.
"""

import time
from numpy import random
from landlab.io.native_landlab import save_grid
from landlab.ca.celllab_cts import Transition, CAPlotter
from matplotlib.pyplot import axis
from six import string_types

_DEBUG = False


class CTSModel(object):
    """
    Implement a generic CellLab-CTS model.

    This is the base class from which models should inherit.
    """

    def __init__(self, grid_size=(5, 5), report_interval=5.0,
                 grid_orientation='vertical', node_layout='rect',
                 show_plots=False, cts_type='oriented_hex',
                 run_duration=1.0, output_interval=1.0e99,
                 plot_every_transition=False, initial_state_grid=None,
                 prop_data=None, prop_reset_value=None, seed=0,
                 closed_boundaries=(False, False, False, False), **kwds):

        self.initialize(grid_size, report_interval, grid_orientation,
                        node_layout, show_plots, cts_type, run_duration,
                        output_interval, plot_every_transition,
                        initial_state_grid, prop_data, prop_reset_value, seed,
                        closed_boundaries, **kwds)

    def initialize(self, grid_size=(5, 5), report_interval=5.0,
                   grid_orientation='vertical', node_layout='rect',
                   show_plots=False, cts_type='oriented_hex',
                   run_duration=1.0, output_interval=1.0e99,
                   plot_every_transition=False, initial_state_grid=None,
                   prop_data=None, prop_reset_value=None, seed=0,
                   closed_boundaries=(False, False, False, False), **kwds):
        """Initialize CTSModel."""

        # Remember the clock time, and calculate when we next want to report
        # progress.
        self.current_real_time = time.time()
        self.next_report = self.current_real_time + report_interval
        self.report_interval = report_interval

        # Interval for output
        self.output_interval = output_interval

        # Duration for run
        self.run_duration = run_duration

        # Create a grid
        self.create_grid_and_node_state_field(grid_size[0], grid_size[1],
                                              grid_orientation, node_layout,
                                              cts_type, closed_boundaries)

        # If prop_data is a string, we assume it is a field name
        if isinstance(prop_data, string_types):
            prop_data = self.grid.add_zeros('node', prop_data)

        # Create the node-state dictionary
        ns_dict = self.node_state_dictionary()

        # Initialize values of the node-state grid
        if initial_state_grid is None:
            nsg = self.initialize_node_state_grid()
        else:
            try:
                nsg = initial_state_grid
                self.grid.at_node['node_state'][:] = nsg
            except TypeError:
                print('If initial_state_grid given, must be array of int')
                raise

        # Create the transition list
        xn_list = self.transition_list()

        # Create the CA object
        if cts_type == 'raster':
            from landlab.ca.raster_cts import RasterCTS
            self.ca = RasterCTS(self.grid, ns_dict, xn_list, nsg, prop_data,
                                prop_reset_value, seed=seed)
        elif cts_type == 'oriented_raster':
            from landlab.ca.oriented_raster_cts import OrientedRasterCTS
            self.ca = OrientedRasterCTS(self.grid, ns_dict, xn_list, nsg,
                                        prop_data, prop_reset_value, seed=seed)
        elif cts_type == 'hex':
            from landlab.ca.hex_cts import HexCTS
            self.ca = HexCTS(self.grid, ns_dict, xn_list, nsg, prop_data,
                             prop_reset_value, seed=seed)
        else:
            from landlab.ca.oriented_hex_cts import OrientedHexCTS
            self.ca = OrientedHexCTS(self.grid, ns_dict, xn_list, nsg,
                                     prop_data, prop_reset_value, seed=seed)

        # Initialize graphics
        self._show_plots = show_plots
        if show_plots:
            self.initialize_plotting(**kwds)

    def _set_closed_boundaries_for_hex_grid(self, closed_boundaries):
        """Setup one or more closed boundaries for a hex grid.

        Parameters
        ----------
        closed_boundaries : 4-element tuple of bool\
            Whether right, top, left, and bottom edges have closed nodes

        Examples
        --------
        >>> from grainhill import CTSModel
        >>> cm = CTSModel(closed_boundaries=(True, True, True, True))
        >>> cm.grid.status_at_node  # doctest: +NORMALIZE_WHITESPACE
        array([4, 4, 4, 4, 4, 4, 0, 4, 0, 0, 4, 0, 4, 0, 0, 4, 0, 4, 0, 0, 4,
               4, 4, 4, 4], dtype=uint8)
        """
        g = self.grid
        if closed_boundaries[0]:
            g.status_at_node[g.nodes_at_right_edge] = g.BC_NODE_IS_CLOSED
        if closed_boundaries[1]:
            g.status_at_node[g.nodes_at_top_edge] = g.BC_NODE_IS_CLOSED
        if closed_boundaries[2]:
            g.status_at_node[g.nodes_at_left_edge] = g.BC_NODE_IS_CLOSED
        if closed_boundaries[3]:
            g.status_at_node[g.nodes_at_bottom_edge] = g.BC_NODE_IS_CLOSED

    def create_grid_and_node_state_field(self, num_rows, num_cols,
                                         grid_orientation, node_layout,
                                         cts_type, closed_bounds):
        """Create the grid and the field containing node states."""

        if cts_type == 'raster' or cts_type == 'oriented_raster':
            from landlab import RasterModelGrid
            self.grid = RasterModelGrid(shape=(num_rows, num_cols),
                                        spacing=1.0)
            self.grid.set_closed_boundaries_at_grid_edges(closed_bounds[0],
                                                          closed_bounds[1],
                                                          closed_bounds[2],
                                                          closed_bounds[3])
        else:
            from landlab import HexModelGrid
            self.grid = HexModelGrid(shape=(num_rows, num_cols), 
                                     spacing=1.0,
                                     orientation=grid_orientation,
                                     node_layout=node_layout)
            if True in closed_bounds:
                self._set_closed_boundaries_for_hex_grid(closed_bounds)

        self.grid.add_zeros('node', 'node_state', dtype=int)

    def node_state_dictionary(self):
        """Create and return a dictionary of all possible node (cell) states.

        This method creates a default set of states (just two); it is a
        template meant to be overridden.
        """
        ns_dict = {0: 'on',
                   1: 'off'}
        return ns_dict

    def transition_list(self):
        """Create and return a list of transition objects.

        This method creates a default set of transitions (just two); it is a
        template meant to be overridden.
        """
        xn_list = []
        xn_list.append(Transition((0, 1, 0), (1, 0, 0), 1.0))
        xn_list.append(Transition((1, 0, 0), (0, 1, 0), 1.0))
        return xn_list

    def write_output(self, grid, outfilename, iteration):
        """Write output to file (currently netCDF)."""
        filename = outfilename + str(iteration).zfill(4) + '.nc'
        save_grid(grid, filename)

    def initialize_node_state_grid(self):
        """Initialize values in the node-state grid.

        This method should be overridden. The default is random "on" and "off".
        """
        num_states = 2
        for i in range(self.grid.number_of_nodes):
            self.grid.at_node['node_state'][i] = random.randint(num_states)
        return self.grid.at_node['node_state']

    def initialize_plotting(self, **kwds):
        """Create and configure CAPlotter object."""
        self.ca_plotter = CAPlotter(self.ca, **kwds)
        self.ca_plotter.update_plot()
        axis('off')

    def run_for(self, dt):

        self.ca.run(self.ca.current_time + dt, self.ca.node_state)


if __name__ == '__main__':
    ctsm = CTSModel(show_plots=True)
    ctsm.run_for(1.0)
    ctsm.ca_plotter.update_plot()
