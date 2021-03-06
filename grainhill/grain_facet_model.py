#!/usr/env/python
"""
Model of normal-fault facet evolution using CTS lattice grain approach.
"""

import sys
from grainhill import CTSModel, plot_hill, calculate_settling_rate
from grainhill.lattice_grain import (lattice_grain_node_states,
                                     lattice_grain_transition_list)
import time
import numpy as np
from landlab.ca.celllab_cts import Transition
from landlab.ca.boundaries.hex_lattice_tectonicizer import LatticeNormalFault


SECONDS_PER_YEAR = 365.25 * 24 * 3600
_DEBUG = False


class GrainFacetSimulator(CTSModel):
    """
    Model facet-slope evolution with 60-degree normal-fault slip.
    """
    def __init__(self, grid_size, report_interval=1.0e8, run_duration=1.0,
                 output_interval=1.0e99, disturbance_rate=0.0,
                 weathering_rate=0.0, dissolution_rate=0.0,
                 uplift_interval=1.0, baselevel_rise_interval=0,
                 plot_interval=1.0e99, friction_coef=0.3,
                 fault_x=1.0, cell_width=1.0, grav_accel=9.8,
                 init_state_grid=None, save_plots=False, plot_filename=None,
                 plot_filetype='.png', seed=0, **kwds):
        """Call the initialize() method."""
        self.initialize(grid_size, report_interval, run_duration,
                        output_interval, disturbance_rate, weathering_rate,
                        dissolution_rate, uplift_interval,
                        baselevel_rise_interval, plot_interval, friction_coef,
                        fault_x,cell_width, grav_accel, init_state_grid,
                        save_plots, plot_filename, plot_filetype, seed, **kwds)

    def initialize(self, grid_size, report_interval, run_duration,
                   output_interval, disturbance_rate, weathering_rate,
                   dissolution_rate, uplift_interval, baselevel_rise_interval,
                   plot_interval, friction_coef, fault_x, cell_width,
                   grav_accel, init_state_grid=None, save_plots=False,
                   plot_filename=None, plot_filetype='.png', seed=0, **kwds):
        """Initialize the grain hill model."""
        self.disturbance_rate = disturbance_rate
        self.weathering_rate = weathering_rate
        self.dissolution_rate = dissolution_rate
        self.uplift_interval = uplift_interval
        self.baselevel_rise_interval = baselevel_rise_interval
        self.plot_interval = plot_interval
        self.friction_coef = friction_coef

        self.settling_rate = calculate_settling_rate(cell_width, grav_accel)

        # Call base class init
        super(GrainFacetSimulator, self).initialize(grid_size=grid_size,
                                          report_interval=report_interval,
                                          grid_orientation='vertical',
                                          grid_shape='rect',
                                          show_plots=False,
                                          cts_type='oriented_hex',
                                          run_duration=run_duration,
                                          output_interval=output_interval,
                                          plot_every_transition=False,
                                          initial_state_grid=init_state_grid,
                                          closed_boundaries=(True, True,
                                                             False, False),
                                          seed=seed)

        ns = self.grid.at_node['node_state']
        self.uplifter = LatticeNormalFault(fault_x_intercept=fault_x,
                                           grid=self.grid,
                                           node_state=ns)

        # initialize plotting
        if plot_interval <= run_duration:
            import matplotlib.pyplot as plt
            plt.ion()
            plt.figure(1)
            self.save_plots = save_plots
            if save_plots:
                self.plot_filename = plot_filename
                self.plot_filetype = plot_filetype
                nplots = (self.run_duration / self.plot_interval) + 1
                self.ndigits = int(np.floor(np.log10(nplots))) + 1
                this_filename = (plot_filename + '0'.zfill(self.ndigits)
                                 + plot_filetype)
                print(this_filename)
            else:
                this_filename = None
            plot_hill(self.grid, this_filename)

        # Work out the next times to plot and output
        self.next_output = self.output_interval
        self.next_plot = self.plot_interval
        self.plot_iteration = 1

        # Next time for a progress report to user
        self.next_report = self.report_interval

        # And baselevel adjustment
        self.next_uplift = self.uplift_interval
        if self.baselevel_rise_interval > 0:
            self.next_baselevel = self.baselevel_rise_interval
            self.baselevel_row = 1
        else:
            self.next_baselevel = self.run_duration + 1

        self.current_time = 0.0

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
                                                motion=self.settling_rate)
        xn_list = self.add_weathering_and_disturbance_transitions(xn_list,
                    self.disturbance_rate, self.weathering_rate,
                    self.dissolution_rate)
        return xn_list

    def add_weathering_and_disturbance_transitions(self, xn_list, d=0.0, w=0.0,
                                                   diss=0.0):
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
        d : float (optional, default=0.0)
            Rate of transition (1/time) from fluid / resting grain pair to
            mobile-grain / fluid pair, representing grain disturbance.
        w : float (optional, default=0.0)
            Rate of transition (1/time) from fluid / rock pair to
            fluid / resting-grain pair, representing weathering.
        diss : float (optional, default=0.0)
            Dissolution: rate of transition from fluid / rock pair to
            fluid / fluid pair.

        Returns
        -------
        xn_list : list of Transition objects
            Modified transition list.
        """

        # Disturbance rule
        if d > 0.0:
            xn_list.append( Transition((7,0,0), (0,1,0), d, 'disturbance') )
            xn_list.append( Transition((7,0,1), (0,2,1), d, 'disturbance') )
            xn_list.append( Transition((7,0,2), (0,3,2), d, 'disturbance') )
            xn_list.append( Transition((0,7,0), (4,0,0), d, 'disturbance') )
            xn_list.append( Transition((0,7,1), (5,0,1), d, 'disturbance') )
            xn_list.append( Transition((0,7,2), (6,0,2), d, 'disturbance') )

        # Weathering rule
        if w > 0.0:
            xn_list.append( Transition((8,0,0), (7,0,0), w, 'weathering') )
            xn_list.append( Transition((8,0,1), (7,0,1), w, 'weathering') )
            xn_list.append( Transition((8,0,2), (7,0,2), w, 'weathering') )
            xn_list.append( Transition((0,8,0), (0,7,0), w, 'weathering') )
            xn_list.append( Transition((0,8,1), (0,7,1), w, 'weathering') )
            xn_list.append( Transition((0,8,2), (0,7,2), w, 'weathering') )

        # Dissolution rule
        if diss > 0.0:
            xn_list.append( Transition((8,0,0), (0,0,0), diss, 'dissolution') )
            xn_list.append( Transition((8,0,1), (0,0,1), diss, 'dissolution') )
            xn_list.append( Transition((8,0,2), (0,0,2), diss, 'dissolution') )
            xn_list.append( Transition((0,8,0), (0,0,0), diss, 'dissolution') )
            xn_list.append( Transition((0,8,1), (0,0,1), diss, 'dissolution') )
            xn_list.append( Transition((0,8,2), (0,0,2), diss, 'dissolution') )

        if _DEBUG:
            print('')
            print('setup_transition_list(): list has ' + str(len(xn_list))
                  + ' transitions:')
            for t in xn_list:
                print('  From state ' + str(t.from_state) + ' to state '
                      + str(t.to_state) + ' at rate ' + str(t.rate) + 'called'
                      + str(t.name))

        return xn_list

    def initialize_node_state_grid(self):
        """Set up initial node states.

        Examples
        --------
        >>> from grainhill import GrainHill
        >>> gh = GrainHill((5, 7))
        >>> gh.grid.at_node['node_state'][:20]
        array([8, 7, 7, 8, 7, 7, 7, 0, 7, 7, 0, 7, 7, 7, 0, 0, 0, 0, 0, 0])
        """

        # For shorthand, get a reference to the node-state grid
        nsg = self.grid.at_node['node_state']

        # Fill the bottom two rows with grains
        right_side_x = 0.866025403784 * (self.grid.number_of_node_columns - 1)
        for i in range(self.grid.number_of_nodes):
            if self.grid.node_y[i] < 2.0:
                if (self.grid.node_x[i] > 0.0 and
                    self.grid.node_x[i] < right_side_x):
                    nsg[i] = 8

        # Place "wall" particles in the lower-left and lower-right corners
        if self.grid.number_of_node_columns % 2 == 0:
            bottom_right = self.grid.number_of_node_columns - 1
        else:
            bottom_right = self.grid.number_of_node_columns // 2
        nsg[0] = 8  # bottom left
        nsg[bottom_right] = 8

        return nsg

    def update_until(self, run_to_time):
        """Advance up to a specified time."""
        while self.current_time < run_to_time:

            # Figure out what time to run to this iteration
            next_pause = min(self.next_output, self.next_plot)
            next_pause = min(next_pause, self.next_uplift)
            next_pause = min(next_pause, self.next_baselevel)
            next_pause = min(next_pause, run_to_time)

            # Once in a while, print out simulation and real time to let the user
            # know that the sim is running ok
            current_real_time = time.time()
            if current_real_time >= self.next_report:
                print('Current sim time ' + str(self.current_time) + ' (' + \
                      str(100 * self.current_time / self.run_duration) + '%)')
                self.next_report = current_real_time + self.report_interval

            # Run the model forward in time until the next output step
            print('Running to...' + str(next_pause))
            self.ca.run(next_pause, self.ca.node_state)
            self.current_time = next_pause

            # Handle output to file
            if self.current_time >= self.next_output:
                self.next_output += self.output_interval

            # Handle plotting on display
            if self.current_time >= self.next_plot:
                if self.save_plots:
                    this_filename = (self.plot_filename
                                     + str(self.plot_iteration).zfill(self.ndigits)
                                     + self.plot_filetype)
                else:
                    this_filename = None
                plot_hill(self.grid, this_filename)
                self.plot_iteration += 1
                self.next_plot += self.plot_interval

            # Handle fault slip
            if self.current_time >= self.next_uplift:
                self.uplifter.do_offset(ca=self.ca,
                                        current_time=self.current_time,
                                        rock_state=8)
#                for i in range(self.grid.number_of_links):
#                    if self.grid.status_at_link[i] == 4 and self.ca.next_trn_id[i] != -1:
#                        print((i, self.ca.next_trn_id[i]))
#                        print((self.grid.x_of_node[self.grid.node_at_link_tail[i]]))
#                        print((self.grid.y_of_node[self.grid.node_at_link_tail[i]]))
#                        print((self.grid.x_of_node[self.grid.node_at_link_head[i]]))
#                        print((self.grid.y_of_node[self.grid.node_at_link_head[i]]))
                self.next_uplift += self.uplift_interval

            # Handle baselevel rise
            if self.current_time >= self.next_baselevel:
                self.raise_baselevel(self.baselevel_row)
                self.baselevel_row += 1
                self.next_baselevel += self.baselevel_rise_interval

    def run(self, to=None):
        """Run the model."""
        if to is None:
            to = self.run_duration
        self.update_until(to)

    def raise_baselevel(self, baselevel_row):
        """Raise baselevel on left by closing a node on the left boundary.

        Parameters
        ----------
        baselevel_row : int
            Row number of the next left-boundary node to be closed

        Examples
        --------
        >>> params = { 'grid_size' : (10,5), 'baselevel_rise_interval' : 1.0 }
        >>> params['run_duration'] = 10.0
        >>> params['uplift_interval'] = 11.0
        >>> gfs = GrainFacetSimulator(**params)
        >>> gfs.run()
        Current sim time 0.0 (0.0%)
        Running to...1.0
        Running to...2.0
        Running to...3.0
        Running to...4.0
        Running to...5.0
        Running to...6.0
        Running to...7.0
        Running to...8.0
        Running to...9.0
        Running to...10.0
        >>> gfs.ca.node_state[:50:5]
        array([8, 8, 8, 8, 8, 8, 8, 8, 8, 8])
        """
        baselevel_node = self.grid.number_of_node_columns * baselevel_row
        if baselevel_node < self.grid.number_of_nodes:
            self.ca.node_state[baselevel_node] = 8
            self.ca.bnd_lnk[self.grid.links_at_node[baselevel_node]] = True
            self.grid.status_at_node[baselevel_node] = self.grid.BC_NODE_IS_CLOSED

    def nodes_in_column(self, col, num_rows, num_cols):
        """Return array of node IDs in given column.

        Examples
        --------
        >>> gfs = GrainFacetSimulator((3, 5))
        >>> gfs.nodes_in_column(1, 3, 5)
        array([ 3,  8, 13])
        >>> gfs.nodes_in_column(4, 3, 5)
        array([ 2,  7, 12])
        >>> gfs = GrainFacetSimulator((3, 6))
        >>> gfs.nodes_in_column(3, 3, 6)
        array([ 4, 10, 16])
        >>> gfs.nodes_in_column(4, 3, 6)
        array([ 2,  8, 14])
        """
        base_node = (col // 2) + (col % 2) * ((num_cols + 1) // 2)
        num_nodes = num_rows * num_cols
        return np.arange(base_node, num_nodes, num_cols)

    def get_profile_and_soil_thickness(self):
        """Calculate and return the topographic profile and the regolith
        thickness."""
        nr = self.ca.grid.number_of_node_rows
        nc = self.ca.grid.number_of_node_columns
        data = self.ca.node_state

        elev = np.zeros(nc)
        soil = np.zeros(nc)
        for c in range(nc):
            e = (c%2)/2.0
            s = 0
            r = 0
            while r<nr and data[c*nr+r]!=0:
                e+=1
                if data[c*nr+r]==7:
                    s+=1
                r+=1
            elev[c] = e
            soil[c] = s
        return elev, soil

    def report_info_for_debug(self, current_time):
        """Print out various bits of data, for testing and debugging."""
        print('\n Current time: ' + str(current_time))
        print('Node state:')
        print(self.ca.node_state)
        for lnk in range(self.grid.number_of_links):
            if self.grid.status_at_link[lnk] == 0:
                print((lnk, self.grid.node_at_link_tail[lnk],
                       self.grid.node_at_link_head[lnk],
                       self.ca.node_state[self.grid.node_at_link_tail[lnk]],
                       self.ca.node_state[self.grid.node_at_link_head[lnk]],
                       self.ca.link_state[lnk],self.ca.next_update[lnk],
                       self.ca.next_trn_id[lnk]))
        print('PQ:')
        print(self.ca.priority_queue._queue)

    def plot_to_file(self):
        """Plot profile of hill to file."""
        fname = self.plot_file_name + str(self.plot_number).zfill(4) + '.png'
        plot_hill(self.ca.grid, filename=fname)
        self.plot_number += 1


def get_params_from_input_file(filename):
    """Fetch parameter values from input file."""
    from landlab.core import load_params

    mpd_params = load_params(filename)

    return mpd_params

def main(params):
    """Initialize model with dict of params then run it."""
    grid_size = (int(params['number_of_node_rows']),
                 int(params['number_of_node_columns']))
    grain_facet_model = GrainFacetSimulator(grid_size, **params)
    grain_facet_model.run()



if __name__=='__main__':
    """Executes model."""
    try:
        infile = sys.argv[1]
    except IndexError:
        print('Must include input file name on command line')
        sys.exit(1)

    params = get_params_from_input_file(infile)
    main(params)
