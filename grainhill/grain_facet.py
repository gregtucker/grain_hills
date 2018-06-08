#!/usr/env/python
"""
Hillslope model with block uplift.
"""

_DEBUG = False

import sys
from cts_model import CTSModel
from lattice_grain import (lattice_grain_node_states,
                           lattice_grain_transition_list)
import time
from numpy import zeros, count_nonzero, where, amax, logical_and
from matplotlib.pyplot import axis
from landlab.ca.celllab_cts import Transition
from landlab.ca.boundaries.hex_lattice_tectonicizer import LatticeNormalFault


class GrainFacet(CTSModel):
    """
    Model hillslope evolution with block uplift.
    """
    def __init__(self, grid_size, report_interval=1.0e8, run_duration=1.0,
                 output_interval=1.0e99, settling_rate=2.2e8,
                 disturbance_rate=1.0, weathering_rate=1.0,
                 uplift_interval=1.0, plot_interval=1.0e99, friction_coef=0.3,
                 fault_x=1.0,
                 rock_state_for_uplift=7, opt_rock_collapse=False,
                 show_plots=True, initial_state_grid=None,
                 opt_track_grains=False, prop_data=None,
                 prop_reset_value=None, callback_fn=None, **kwds):
        """Call the initialize() method."""
        self.initializer(grid_size, report_interval, run_duration,
                        output_interval, settling_rate, disturbance_rate,
                        weathering_rate, uplift_interval, plot_interval,
                        friction_coef, fault_x, rock_state_for_uplift,
                        opt_rock_collapse, show_plots, initial_state_grid,
                        opt_track_grains, prop_data, prop_reset_value,
                        callback_fn, **kwds)

    def initializer(self, grid_size, report_interval, run_duration,
                   output_interval, settling_rate, disturbance_rate,
                   weathering_rate, uplift_interval, plot_interval,
                   friction_coef, fault_x, rock_state_for_uplift, opt_rock_collapse,
                   show_plots, initial_state_grid, opt_track_grains, prop_data,
                   prop_reset_value, callback_fn, **kwds):
        """Initialize the grain hill model."""
        self.settling_rate = settling_rate
        self.disturbance_rate = disturbance_rate
        self.weathering_rate = weathering_rate
        self.uplift_interval = uplift_interval
        self.plot_interval = plot_interval
        self.friction_coef = friction_coef
        self.rock_state = rock_state_for_uplift  # 7 (resting sed) or 8 (rock)
        self.opt_track_grains = opt_track_grains
        self.callback_fn = callback_fn
        if opt_rock_collapse:
            self.collapse_rate = self.settling_rate
        else:
            self.collapse_rate = 0.0

        # Call base class init
        super(GrainFacet, self).initialize(grid_size=grid_size,
                                           report_interval=report_interval,
                                           grid_orientation='vertical',
                                           grid_shape='rect',
                                           show_plots=show_plots,
                                           cts_type='oriented_hex',
                                           run_duration=run_duration,
                                           output_interval=output_interval,
                                           initial_state_grid=initial_state_grid,
                                           prop_data=prop_data,
                                           prop_reset_value=prop_reset_value,
                                           **kwds)

        # Set some things related to property-swapping and/or callback fn
        # if the user wants to track grain motion.
        #if opt_track_grains:
        #    propid = self.ca.propid
        #else:
        #    propid = None

        self.uplifter = LatticeNormalFault(fault_x_intercept=fault_x,
                                           grid=self.grid,
                                           node_state=self.grid.at_node['node_state'],
                                           propid=self.ca.propid,
                                           prop_data=self.ca.prop_data,
                                           prop_reset_value=self.ca.prop_reset_value)

        self.initialize_timing(output_interval, plot_interval, uplift_interval,
                               report_interval)

    def initialize_timing(self, output_interval, plot_interval,
                          uplift_interval, report_interval):
        """Set up variables related to timing of uplift, output, reporting"""

        self.current_time = 0.0

        # Next time for output to file
        self.next_output = output_interval

        # Next time for a plot
        if self._show_plots:
            self.next_plot = plot_interval
        else:
            self.next_plot = self.run_duration + 1

        # Next time for a progress report to user
        self.next_report = report_interval

        # Next time to add baselevel adjustment
        self.next_uplift = uplift_interval

        # Iteration numbers, for output files
        self.output_iteration = 1

    def node_state_dictionary(self):
        """
        Create and return dict of node states.

        Overrides base-class method. Here, we simply call on a function in
        the lattice_grain module.
        """
        return lattice_grain_node_states()

    def transition_list(self):
        """
        Make and return list of Transition object.
        """
        xn_list = lattice_grain_transition_list(g=self.settling_rate,
                                                f=self.friction_coef,
                                                motion=self.settling_rate,
                                                swap=self.opt_track_grains,
                                                callback=self.callback_fn)
        xn_list = self.add_weathering_and_disturbance_transitions(xn_list,
                    self.disturbance_rate, self.weathering_rate,
                    collapse_rate=self.collapse_rate)
        return xn_list

    def add_weathering_and_disturbance_transitions(self, xn_list, d=0.0, w=0.0,
                                                   collapse_rate=0.0,
                                                   swap=False, callback=None):
        """
        Add transition rules representing weathering and/or grain disturbance
        to the list, and return the list.

        Parameters
        ----------
        xn_list : list of Transition objects
            List of objects that encode information about the link-state
            transitions. Normally should first be initialized with lattice-grain
            transition rules, then passed to this function to add rules for
            weathering and disturbance.
        d : float (optional)
            Rate of transition (1/time) from fluid / resting grain pair to
            mobile-grain / fluid pair, representing grain disturbance.
        w : float (optional)
            Rate of transition (1/time) from fluid / rock pair to
            fluid / resting-grain pair, representing weathering.

        Returns
        -------
        xn_list : list of Transition objects
            Modified transition list.
        """

        # Disturbance rule
        if d > 0.0:
            xn_list.append( Transition((7,0,0), (0,1,0), d, 'disturbance', swap, callback) )
            xn_list.append( Transition((7,0,1), (0,2,1), d, 'disturbance', swap, callback) )
            xn_list.append( Transition((7,0,2), (0,3,2), d, 'disturbance', swap, callback) )
            xn_list.append( Transition((0,7,0), (4,0,0), d, 'disturbance', swap, callback) )
            xn_list.append( Transition((0,7,1), (5,0,1), d, 'disturbance', swap, callback) )
            xn_list.append( Transition((0,7,2), (6,0,2), d, 'disturbance', swap, callback) )

        # Weathering rule
        if w > 0.0:
            xn_list.append( Transition((8,0,0), (7,0,0), w, 'weathering') )
            xn_list.append( Transition((8,0,1), (7,0,1), w, 'weathering') )
            xn_list.append( Transition((8,0,2), (7,0,2), w, 'weathering') )
            xn_list.append( Transition((0,8,0), (0,7,0), w, 'weathering') )
            xn_list.append( Transition((0,8,1), (0,7,1), w, 'weathering') )
            xn_list.append( Transition((0,8,2), (0,7,2), w, 'weathering') )

            # "Vertical rock collapse" rule: a rock particle overlying air
            # will collapse, transitioning to a downward-moving grain
            if collapse_rate > 0.0:
                xn_list.append( Transition((0,8,0), (4,0,0), collapse_rate,
                                           'rock collapse', swap, callback))

        if _DEBUG:
            print()
            print('setup_transition_list(): list has ' + str(len(xn_list))
                  + ' transitions:')
            for t in xn_list:
                print('  From state ' + str(t.from_state) + ' to state '
                      + str(t.to_state) + ' at rate ' + str(t.rate)
                      + ' called ' + str(t.name))

        return xn_list

    def initialize_node_state_grid(self):
        """Set up initial node states.

        Examples
        --------
        >>> gh = GrainFacet((5, 7))
        >>> gh.grid.at_node['node_state']
        array([8, 7, 7, 8, 7, 7, 7, 0, 7, 7, 0, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        """

        # For shorthand, get a reference to the node-state grid
        nsg = self.grid.at_node['node_state']

        # Fill the bottom two rows with grains
        right_side_x = 0.866025403784 * (self.grid.number_of_node_columns - 1)
        for i in range(self.grid.number_of_nodes):
            if self.grid.node_y[i] < 2.0:
                if (self.grid.node_x[i] > 0.0 and
                    self.grid.node_x[i] < right_side_x):
                    nsg[i] = 7

        # Place "wall" particles in the lower-left and lower-right corners
        if self.grid.number_of_node_columns % 2 == 0:
            bottom_right = self.grid.number_of_node_columns - 1
        else:
            bottom_right = self.grid.number_of_node_columns // 2
        nsg[0] = 8  # bottom left
        nsg[bottom_right] = 8

        return nsg

    def run(self, to=None):
        """Run the model."""
        if to is None:
            run_to = self.run_duration
        else:
            run_to = to

        while self.current_time < run_to:

            # Figure out what time to run to this iteration
            next_pause = min(self.next_output, self.next_plot)
            next_pause = min(next_pause, self.next_uplift)
            next_pause = min(next_pause, run_to)

            # Once in a while, print out simulation and real time to let the user
            # know that the sim is running ok
            current_real_time = time.time()
            if current_real_time >= self.next_report:
                print('Current sim time' + str(self.current_time) + '(' + \
                      str(100 * self.current_time / self.run_duration) + '%)')
                self.next_report = current_real_time + self.report_interval

            # Run until next pause
            self.ca.run(next_pause, self.ca.node_state)
            self.current_time = next_pause

            # Handle output to file
            if self.current_time >= self.next_output:
                self.write_output(self.grid, 'grain_hill_model',
                                  self.output_iteration)
                self.output_iteration += 1
                self.next_output += self.output_interval

            # Handle plotting on display
            if self._show_plots and self.current_time >= self.next_plot:
                self.ca_plotter.update_plot()
                axis('off')
                self.next_plot += self.plot_interval

            # Handle uplift
            if self.current_time >= self.next_uplift:
                self.uplifter.do_offset(
                    ca=self.ca, current_time=self.current_time,
                    rock_state=self.rock_state)
                self.next_uplift += self.uplift_interval

    def get_profile_and_soil_thickness(self, grid, data):
        """Calculate and return profiles of elevation and soil thickness.

        Examples
        --------
        >>> from landlab import HexModelGrid
        >>> hg = HexModelGrid(4, 5, shape='rect', orientation='vert')
        >>> ns = hg.add_zeros('node', 'node_state', dtype=int)
        >>> ns[[0, 3, 1, 6, 4, 9, 2]] = 8
        >>> ns[[8, 13, 11, 16, 14]] = 7
        >>> gh = GrainHill((3, 7))  # grid size arbitrary here
        >>> (elev, thickness) = gh.get_profile_and_soil_thickness(hg, ns)
        >>> elev
        array([0. , 2.5, 3. , 2.5, 0. ])
        >>> thickness
        array([0., 2., 2., 1., 0.])
        """
        nc = grid.number_of_node_columns
        elev = zeros(nc)
        soil = zeros(nc)
        for col in range(nc):
            states = data[grid.nodes[:, col]]
            (rows_with_rock_or_sed, ) = where(states > 0)
            if len(rows_with_rock_or_sed) == 0:
                elev[col] = 0.0
            else:
                elev[col] = amax(rows_with_rock_or_sed) + 0.5 * (col % 2)
            soil[col] = count_nonzero(logical_and(states > 0, states < 8))

        return elev, soil


def get_params_from_input_file(filename):
    """Fetch parameter values from input file."""
    from landlab.core import load_params

    mpd_params = load_params(filename)
    return mpd_params


def main(params):
    """Initialize model with dict of params then run it."""
    grid_size = (int(params['number_of_node_rows']),
                 int(params['number_of_node_columns']))
    grain_hill_model = GrainHill(grid_size, **params)
    grain_hill_model.run()

    # Temporary: save last image to file
    import matplotlib.pyplot as plt
    plt.savefig('grain_hill_final.png')

if __name__=='__main__':
    """Executes model."""
    try:
        infile = sys.argv[1]
    except IndexError:
        print('Must include input file name on command line')
        sys.exit(1)

    params = get_params_from_input_file(infile)
    main(params)